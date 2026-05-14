const TOKEN_URL = '/api/auth/token';
const TOKENS_KEY = 'tetrics_tokens';

interface Tokens {
  access_token: string;
  refresh_token: string;
  expires_at: number;
}

interface UserInfo {
  username: string;
  email: string;
  roles: string[];
}

function decodeJwt(token: string): Record<string, any> {
  const base64Url = token.split('.')[1];
  const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
  const jsonPayload = decodeURIComponent(
    atob(base64)
      .split('')
      .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
      .join('')
  );
  return JSON.parse(jsonPayload);
}

function getTokens(): Tokens | null {
  if (typeof window === 'undefined') return null;
  const raw = localStorage.getItem(TOKENS_KEY);
  if (!raw) return null;
  try {
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

function setAuthCookie(): void {
  document.cookie = 'tetrics_auth=1; path=/; max-age=86400; SameSite=Lax';
}

function removeAuthCookie(): void {
  document.cookie = 'tetrics_auth=; path=/; max-age=0';
}

function setTokens(tokens: Tokens): void {
  localStorage.setItem(TOKENS_KEY, JSON.stringify(tokens));
  setAuthCookie();
}

function clearTokens(): void {
  localStorage.removeItem(TOKENS_KEY);
  removeAuthCookie();
}

let refreshPromise: Promise<Tokens> | null = null;

async function requestTokens(body: Record<string, string>): Promise<Tokens> {
  const response = await fetch(TOKEN_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });

  if (!response.ok) {
    throw new Error('Authentication failed');
  }

  const data = await response.json();
  return {
    access_token: data.access_token,
    refresh_token: data.refresh_token,
    expires_at: Date.now() + data.expires_in * 1000,
  };
}

async function refreshAccessToken(refreshToken: string): Promise<Tokens> {
  // Deduplicate concurrent refresh attempts
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    const tokens = await requestTokens({
      grant_type: 'refresh_token',
      refresh_token: refreshToken,
    });
    setTokens(tokens);
    return tokens;
  })();

  try {
    return await refreshPromise;
  } finally {
    refreshPromise = null;
  }
}

async function getAccessToken(): Promise<string | null> {
  const tokens = getTokens();
  if (!tokens) return null;

  // Refresh if expiring within 30 seconds
  if (Date.now() > tokens.expires_at - 30000) {
    try {
      const fresh = await refreshAccessToken(tokens.refresh_token);
      return fresh.access_token;
    } catch {
      clearTokens();
      return null;
    }
  }

  return tokens.access_token;
}

function parseUser(token: string): UserInfo {
  const payload = decodeJwt(token);
  return {
    username: payload.preferred_username || '',
    email: payload.email || '',
    roles: payload.realm_access?.roles || [],
  };
}

async function login(username: string, password: string): Promise<UserInfo> {
  const data = await requestTokens({
    grant_type: 'password',
    username,
    password,
  });
  setTokens(data);

  return parseUser(data.access_token);
}

function logout(): void {
  clearTokens();
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new Event('tetrics-logout'));
  }
}

function getUser(): UserInfo | null {
  const tokens = getTokens();
  if (!tokens) return null;
  try {
    return parseUser(tokens.access_token);
  } catch {
    return null;
  }
}

export {
  getAccessToken,
  getTokens,
  setTokens,
  clearTokens,
  decodeJwt,
  login,
  logout,
  getUser,
  parseUser,
};
export type { UserInfo, Tokens };

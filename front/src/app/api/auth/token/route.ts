import { NextResponse } from 'next/server';

const KEYCLOAK_URL =
  process.env.NEXT_PUBLIC_KEYCLOAK_URL || process.env.KEYCLOAK_URL || 'http://localhost:8080';
const KEYCLOAK_REALM =
  process.env.NEXT_PUBLIC_KEYCLOAK_REALM || process.env.KEYCLOAK_REALM || 'tetrics';
const KEYCLOAK_CLIENT_ID =
  process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_ID || process.env.KEYCLOAK_CLIENT_ID || 'fastapi-client';
const KEYCLOAK_CLIENT_SECRET =
  process.env.NEXT_PUBLIC_KEYCLOAK_CLIENT_SECRET || process.env.KEYCLOAK_CLIENT_SECRET || '';

type TokenRequestBody = {
  grant_type?: string;
  username?: string;
  password?: string;
  refresh_token?: string;
};

export async function POST(request: Request) {
  let body: TokenRequestBody;

  try {
    body = (await request.json()) as TokenRequestBody;
  } catch {
    return NextResponse.json({ detail: 'Invalid request body' }, { status: 400 });
  }

  if (body.grant_type !== 'password' && body.grant_type !== 'refresh_token') {
    return NextResponse.json({ detail: 'Unsupported grant type' }, { status: 400 });
  }

  const tokenUrl = `${KEYCLOAK_URL}/realms/${KEYCLOAK_REALM}/protocol/openid-connect/token`;
  const params = new URLSearchParams({
    client_id: KEYCLOAK_CLIENT_ID,
    grant_type: body.grant_type,
  });

  if (KEYCLOAK_CLIENT_SECRET) {
    params.set('client_secret', KEYCLOAK_CLIENT_SECRET);
  }

  if (body.grant_type === 'password') {
    if (!body.username || !body.password) {
      return NextResponse.json(
        { detail: 'Username and password are required' },
        { status: 400 }
      );
    }
    params.set('username', body.username);
    params.set('password', body.password);
  }

  if (body.grant_type === 'refresh_token') {
    if (!body.refresh_token) {
      return NextResponse.json({ detail: 'Refresh token is required' }, { status: 400 });
    }
    params.set('refresh_token', body.refresh_token);
  }

  const response = await fetch(tokenUrl, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: params.toString(),
  });

  const responseBody = await response.text();
  const contentType = response.headers.get('content-type') || 'application/json';

  return new NextResponse(responseBody, {
    status: response.status,
    headers: {
      'Content-Type': contentType,
    },
  });
}
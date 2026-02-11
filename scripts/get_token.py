#!/usr/bin/env python3
"""
Script to get an access token from Keycloak and print it to stdout.
Usage: python get_token.py [username] [password]
If no username/password provided, uses client credentials flow.
"""

import sys
import httpx


def get_access_token(username=None, password=None, debug=False):
    """Get access token from Keycloak."""
    token_url = "http://localhost:8080/realms/lks/protocol/openid-connect/token"
    
    data = {
        "client_id": "fastapi-client",
        "client_secret": "fastapi-client-secret-123",
        "scope": "openid"
    }
    
    if username and password:
        # User credentials flow
        data.update({
            "grant_type": "password",
            "username": username,
            "password": password
        })
    else:
        # Client credentials flow
        data["grant_type"] = "client_credentials"
    
    if debug:
        print(f"Request URL: {token_url}", file=sys.stderr)
        print(f"Request data: {data}", file=sys.stderr)
    
    try:
        response = httpx.post(
            token_url, 
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if debug:
            print(f"Response status: {response.status_code}", file=sys.stderr)
            print(f"Response headers: {dict(response.headers)}", file=sys.stderr)
            print(f"Response body: {response.text}", file=sys.stderr)
        
        response.raise_for_status()
        return response.json()["access_token"]
    except httpx.HTTPError as e:
        print(f"Error getting token: {e}", file=sys.stderr)
        if hasattr(e, 'response') and e.response:
            print(f"Response status: {e.response.status_code}", file=sys.stderr)
            print(f"Response body: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except KeyError:
        print("Error: No access_token in response", file=sys.stderr)
        sys.exit(1)


def main():
    debug = "--debug" in sys.argv
    if debug:
        sys.argv.remove("--debug")
    
    if len(sys.argv) == 3:
        # User credentials provided
        username = sys.argv[1]
        password = sys.argv[2]
        token = get_access_token(username, password, debug)
    elif len(sys.argv) == 1:
        # No arguments - use client credentials
        token = get_access_token(debug=debug)
    else:
        print("Usage: python get_token.py [username password] [--debug]", file=sys.stderr)
        print("If no arguments provided, uses client credentials flow", file=sys.stderr)
        print("Add --debug flag to see request/response details", file=sys.stderr)
        sys.exit(1)
    
    print(token)


if __name__ == "__main__":
    main()

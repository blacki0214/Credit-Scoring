"""
Student API demo runner.

Supports two auth modes:
1) Firebase bearer token (real auth)
2) Development-only bypass (no bearer; requires API server configured with
   DEMO_AUTH_BYPASS_ENABLED=true and ENVIRONMENT!=production)

Usage examples:
  python demo_student_api.py --base-url http://localhost:8000 --mode bypass
  python demo_student_api.py --base-url http://localhost:8000 --mode token --token <id_token>
  python demo_student_api.py --base-url http://localhost:8000 --mode firebase-login \
      --firebase-api-key <web_api_key> --email <user@email.com> --password <password>
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any, Dict

import requests


DEFAULT_PAYLOAD = {
    "age": 21,
    "gpa_latest": 3.2,
    "academic_year": 3,
    "major": "technology",
    "program_level": "undergraduate",
    "living_status": "dormitory",
    "has_buffer": True,
    "support_sources": ["family", "part_time"],
    "monthly_income": 9_000_000,
    "monthly_expenses": 3_000_000,
}


def fetch_firebase_id_token(firebase_api_key: str, email: str, password: str) -> str:
    """Sign in with Firebase Auth REST API and return ID token."""
    url = (
        "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
        f"?key={firebase_api_key}"
    )
    body = {
        "email": email,
        "password": password,
        "returnSecureToken": True,
    }
    resp = requests.post(url, json=body, timeout=20)
    if resp.status_code != 200:
        raise RuntimeError(f"Firebase login failed: {resp.status_code} {resp.text}")
    data = resp.json()
    token = data.get("idToken")
    if not token:
        raise RuntimeError("Firebase login response missing idToken")
    return token


def call_endpoint(base_url: str, path: str, payload: Dict[str, Any], headers: Dict[str, str]) -> Dict[str, Any]:
    url = f"{base_url.rstrip('/')}{path}"
    resp = requests.post(url, json=payload, headers=headers, timeout=20)
    return {
        "url": url,
        "status_code": resp.status_code,
        "body": resp.json() if "application/json" in resp.headers.get("content-type", "") else resp.text,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Demo student scoring endpoints")
    parser.add_argument("--base-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument(
        "--mode",
        choices=["bypass", "token", "firebase-login"],
        required=True,
        help="Auth mode",
    )
    parser.add_argument("--token", default="", help="Firebase ID token for mode=token")
    parser.add_argument("--firebase-api-key", default="", help="Firebase Web API key")
    parser.add_argument("--email", default="", help="Firebase user email")
    parser.add_argument("--password", default="", help="Firebase user password")
    args = parser.parse_args()

    payload = dict(DEFAULT_PAYLOAD)
    headers: Dict[str, str] = {"Content-Type": "application/json"}

    try:
        if args.mode == "token":
            if not args.token:
                raise RuntimeError("--token is required for mode=token")
            headers["Authorization"] = f"Bearer {args.token}"
        elif args.mode == "firebase-login":
            if not args.firebase_api_key or not args.email or not args.password:
                raise RuntimeError(
                    "--firebase-api-key, --email, and --password are required for mode=firebase-login"
                )
            token = fetch_firebase_id_token(args.firebase_api_key, args.email, args.password)
            headers["Authorization"] = f"Bearer {token}"
        else:
            # bypass mode: no Authorization header.
            pass

        score_result = call_endpoint(
            base_url=args.base_url,
            path="/api/student/credit-score",
            payload=payload,
            headers=headers,
        )
        limit_result = call_endpoint(
            base_url=args.base_url,
            path="/api/student/calculate-limit",
            payload=payload,
            headers=headers,
        )

        print("\n=== /api/student/credit-score ===")
        print(f"status: {score_result['status_code']}")
        print(json.dumps(score_result["body"], indent=2, ensure_ascii=False))

        print("\n=== /api/student/calculate-limit ===")
        print(f"status: {limit_result['status_code']}")
        print(json.dumps(limit_result["body"], indent=2, ensure_ascii=False))
        return 0
    except Exception as exc:
        print(f"Demo failed: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

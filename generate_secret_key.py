#!/usr/bin/env python
"""
Generate a secure SECRET_KEY for Django production deployment.

Usage:
    python generate_secret_key.py

Output:
    A new random SECRET_KEY suitable for Django production.
    Copy this value to your .env file: SECRET_KEY=<generated_key>
"""

from django.core.management.utils import get_random_secret_key

if __name__ == "__main__":
    secret_key = get_random_secret_key()
    print("=" * 80)
    print("GENERATED SECRET_KEY (copy this to your .env file):")
    print("=" * 80)
    print(f"SECRET_KEY={secret_key}")
    print("=" * 80)
    print("\n⚠️  IMPORTANT SECURITY NOTES:")
    print("1. Never commit your .env file to version control")
    print("2. Keep this SECRET_KEY safe and secret")
    print("3. Rotate it periodically in production")
    print("4. Use different keys for development and production")
    print("=" * 80)

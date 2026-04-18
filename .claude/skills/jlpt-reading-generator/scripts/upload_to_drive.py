#!/usr/bin/env python3
"""
Upload images to Google Drive and update CSV with shareable links.

Credentials auto-detection (searches in order):
    1. secrets/service_account.json  (Service Account — no browser needed)
    2. secrets/credentials.json      (OAuth2 — needs browser on first run)
    3. --credentials flag             (explicit path)

Usage:
    # === Service Account (recommended) ===
    # Just place secrets/service_account.json and run:
    python3 upload_to_drive.py \
        --img-dir assets/img/tim_thong_tin \
        --csv sheets/n5_samples_v2.csv

    # === OAuth2 ===
    # First time: authenticate (opens browser)
    python3 upload_to_drive.py --auth

    # Then upload:
    python3 upload_to_drive.py \
        --img-dir assets/img/tim_thong_tin \
        --csv sheets/n5_samples_v2.csv

    # Upload specific files only
    python3 upload_to_drive.py \
        --files n5_6.png n5_7.png n5_8.png \
        --img-dir assets/img/tim_thong_tin

Setup:
    pip install google-auth google-auth-oauthlib google-api-python-client --break-system-packages

Credentials setup:
    Option A — Service Account (recommended for automation):
        1. Google Cloud Console → IAM & Admin → Service Accounts
        2. Create service account → Download JSON key
        3. Save as: secrets/service_account.json
        4. Share the Drive folder with the service account email (Editor role)

    Option B — OAuth2 (needs browser once):
        1. Google Cloud Console → APIs & Credentials
        2. Create OAuth 2.0 Client ID (Desktop app)
        3. Download JSON → save as: secrets/credentials.json
        4. Run: python3 upload_to_drive.py --auth
        5. Token saved automatically to secrets/token.json
"""

import argparse
import csv
import json
import os
import sys
from pathlib import Path

# Google API imports
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account as sa_module
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SCOPES = ['https://www.googleapis.com/auth/drive.file']

# --- Auto-detect paths (relative to project root) ---
# Project root = 4 levels up from this script:
#   scripts/ → jlpt-reading-generator/ → skills/ → .claude/ → PROJECT_ROOT
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent.parent.parent  # .claude/skills/jlpt.../scripts → root

SECRETS_DIR = PROJECT_ROOT / 'secrets'
SERVICE_ACCOUNT_PATH = SECRETS_DIR / 'service_account.json'
OAUTH_CREDENTIALS_PATH = SECRETS_DIR / 'credentials.json'
TOKEN_PATH = SECRETS_DIR / 'token.json'

DEFAULT_FOLDER_ID = '13hW7nalQDbpL8olH4ffRApvHc-24Fzr3'


def detect_auth_method() -> str:
    """Detect which auth method to use based on available files."""
    if SERVICE_ACCOUNT_PATH.exists():
        return 'service_account'
    if TOKEN_PATH.exists() or OAUTH_CREDENTIALS_PATH.exists():
        return 'oauth'
    return 'none'


def authenticate_service_account():
    """Authenticate using a service account JSON key."""
    if not SERVICE_ACCOUNT_PATH.exists():
        print(f"ERROR: Service account key not found at {SERVICE_ACCOUNT_PATH}")
        sys.exit(1)

    creds = sa_module.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_PATH), scopes=SCOPES
    )
    print(f"  Auth: Service Account ({SERVICE_ACCOUNT_PATH.name})")
    return creds


def authenticate_oauth(credentials_path: str = None):
    """Authenticate with OAuth2. Opens browser on first run."""
    creds = None

    # Load existing token
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)

    # Refresh or create new token
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Find credentials.json
            cred_path = credentials_path or str(OAUTH_CREDENTIALS_PATH)
            if not os.path.exists(cred_path):
                print("ERROR: OAuth credentials not found.")
                print(f"  Expected: {OAUTH_CREDENTIALS_PATH}")
                print(f"  Or use: --credentials /path/to/credentials.json")
                print()
                print("  Download from Google Cloud Console:")
                print("    1. Go to https://console.cloud.google.com/apis/credentials")
                print("    2. Create OAuth 2.0 Client ID (Desktop app)")
                print("    3. Download JSON")
                print(f"    4. Save to: {OAUTH_CREDENTIALS_PATH}")
                sys.exit(1)

            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save token
        SECRETS_DIR.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, 'w') as f:
            f.write(creds.to_json())
        print(f"  Token saved to {TOKEN_PATH}")

    print(f"  Auth: OAuth2 ({TOKEN_PATH.name})")
    return creds


def get_drive_service(credentials_path: str = None):
    """Get authenticated Google Drive service. Auto-detects auth method."""
    method = detect_auth_method()

    if method == 'service_account':
        creds = authenticate_service_account()
    elif method == 'oauth':
        creds = authenticate_oauth(credentials_path)
    else:
        # No credentials found — guide user
        print("=" * 60)
        print("  No Google Drive credentials found!")
        print("=" * 60)
        print()
        print(f"  Place ONE of these files in: {SECRETS_DIR}/")
        print()
        print("  Option A (recommended): service_account.json")
        print("    → No browser needed, works fully automated")
        print("    → Create at: Google Cloud Console → Service Accounts")
        print()
        print("  Option B: credentials.json")
        print("    → Needs browser once for OAuth consent")
        print("    → Create at: Google Cloud Console → OAuth 2.0 Client IDs")
        print()
        print(f"  Then run: python3 {sys.argv[0]} --auth")
        sys.exit(1)

    return build('drive', 'v3', credentials=creds)


def upload_file(service, file_path: str, folder_id: str) -> dict:
    """Upload a single file to Google Drive folder. Returns file metadata."""
    file_name = os.path.basename(file_path)

    # Detect mimetype
    ext = Path(file_path).suffix.lower()
    mimetypes = {
        '.png': 'image/png', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg',
        '.gif': 'image/gif', '.webp': 'image/webp', '.svg': 'image/svg+xml',
        '.html': 'text/html', '.csv': 'text/csv', '.json': 'application/json',
    }
    mimetype = mimetypes.get(ext, 'application/octet-stream')

    # Check if file already exists in folder
    query = f"name = '{file_name}' and '{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, fields="files(id, name, webViewLink)").execute()
    existing = results.get('files', [])

    if existing:
        file_id = existing[0]['id']
        media = MediaFileUpload(file_path, mimetype=mimetype)
        updated = service.files().update(
            fileId=file_id,
            media_body=media,
            fields='id, name, webViewLink, webContentLink'
        ).execute()
        print(f"  ~ Updated: {file_name} (id: {file_id})")
        return updated
    else:
        file_metadata = {
            'name': file_name,
            'parents': [folder_id]
        }
        media = MediaFileUpload(file_path, mimetype=mimetype)
        created = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink, webContentLink'
        ).execute()

        # Make file viewable by anyone with link
        service.permissions().create(
            fileId=created['id'],
            body={'type': 'anyone', 'role': 'reader'}
        ).execute()

        print(f"  + Uploaded: {file_name} (id: {created['id']})")
        return created


def make_direct_link(file_id: str) -> str:
    """Create a direct image link from Google Drive file ID."""
    return f"https://drive.google.com/uc?id={file_id}&export=view"


def upload_images(img_dir: str, folder_id: str, files: list = None,
                  credentials_path: str = None) -> dict:
    """Upload all PNG images in directory to Google Drive.

    Returns: dict mapping local filename -> {id, link, direct_link}
    """
    service = get_drive_service(credentials_path)
    img_path = Path(img_dir)

    if files:
        png_files = [img_path / f for f in files]
    else:
        png_files = sorted(img_path.glob('*.png'))

    if not png_files:
        print(f"No PNG files found in {img_dir}")
        return {}

    print(f"\nUploading {len(png_files)} files to Drive folder {folder_id}...")
    results = {}
    for f in png_files:
        if not f.exists():
            print(f"  x File not found: {f}")
            continue
        info = upload_file(service, str(f), folder_id)
        file_id = info['id']
        results[f.name] = {
            'id': file_id,
            'link': info.get('webViewLink', ''),
            'direct_link': make_direct_link(file_id)
        }

    print(f"\nDone! {len(results)}/{len(png_files)} files uploaded.")
    return results


def update_csv(csv_path: str, upload_results: dict, img_dir: str):
    """Update general_image column in CSV with Google Drive direct links."""
    if not upload_results:
        print("No upload results to update CSV with.")
        return

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        rows = list(reader)

    if 'general_image' not in fieldnames:
        print(f"ERROR: CSV {csv_path} has no 'general_image' column")
        return

    updated_count = 0
    for row in rows:
        local_path = row.get('general_image', '')
        filename = os.path.basename(local_path)
        if filename in upload_results:
            row['general_image'] = upload_results[filename]['direct_link']
            updated_count += 1

    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\n  CSV updated: {updated_count} rows in {csv_path}")

    print("\nLink mapping:")
    for filename, info in upload_results.items():
        print(f"  {filename} -> {info['direct_link']}")


def main():
    parser = argparse.ArgumentParser(
        description='Upload images to Google Drive & update CSV',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f"""
Credentials auto-detection (from {SECRETS_DIR}/):
  1. service_account.json  → Service Account (no browser)
  2. credentials.json      → OAuth2 (browser once)

Examples:
  # Auth (OAuth only, service account needs no auth step)
  python3 {sys.argv[0]} --auth

  # Upload all PNGs + update CSV
  python3 {sys.argv[0]} --csv sheets/n5_samples_v2.csv

  # Upload specific files
  python3 {sys.argv[0]} --files n5_6.png n5_7.png
"""
    )
    parser.add_argument('--auth', action='store_true',
                        help='Authenticate only (OAuth2 first-time setup)')
    parser.add_argument('--credentials', type=str, default=None,
                        help='Path to credentials.json (overrides auto-detect)')
    parser.add_argument('--img-dir', type=str, default='assets/img/tim_thong_tin',
                        help='Directory containing images (default: assets/img/tim_thong_tin)')
    parser.add_argument('--csv', type=str, default=None,
                        help='CSV file to update general_image column')
    parser.add_argument('--folder-id', type=str, default=DEFAULT_FOLDER_ID,
                        help=f'Google Drive folder ID (default: {DEFAULT_FOLDER_ID})')
    parser.add_argument('--files', nargs='+', default=None,
                        help='Specific filenames to upload (default: all PNG in img-dir)')

    args = parser.parse_args()

    # Show detected config
    print(f"Project root: {PROJECT_ROOT}")
    print(f"Secrets dir:  {SECRETS_DIR}")
    print(f"Auth method:  {detect_auth_method()}")

    if args.auth:
        method = detect_auth_method()
        if method == 'service_account':
            print("\nService account detected — no auth step needed!")
            print(f"  File: {SERVICE_ACCOUNT_PATH}")
            authenticate_service_account()
            print("\nAuthentication OK!")
        else:
            authenticate_oauth(args.credentials)
            print("\nAuthentication complete!")
        return

    # Upload
    results = upload_images(
        img_dir=args.img_dir,
        folder_id=args.folder_id,
        files=args.files,
        credentials_path=args.credentials
    )

    # Update CSV if specified
    if args.csv and results:
        update_csv(args.csv, results, args.img_dir)

    # Save mapping to JSON
    if results:
        mapping_path = os.path.join(args.img_dir, '_drive_links.json')
        with open(mapping_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        print(f"\n  Link mapping saved to {mapping_path}")


if __name__ == '__main__':
    main()

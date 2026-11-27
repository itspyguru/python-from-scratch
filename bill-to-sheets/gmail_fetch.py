import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]
QUERY = "subject:(invoice OR receipt) has:attachment filename:pdf newer_than:60d"


def get_gmail():
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
        creds = flow.run_local_server(port=0)
        with open("token.json", "w") as f:
            f.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)


def find_pdfs(part, found):
    if part.get("filename", "").lower().endswith(".pdf"):
        found.append(part)
    for child in part.get("parts", []):
        find_pdfs(child, found)


def download_bills(folder="bills", limit=10):
    os.makedirs(folder, exist_ok=True)
    gmail = get_gmail()
    result = gmail.users().messages().list(userId="me", q=QUERY, maxResults=limit).execute()
    saved = 0
    for msg in result.get("messages", []):
        full = gmail.users().messages().get(userId="me", id=msg["id"]).execute()
        pdfs = []
        find_pdfs(full["payload"], pdfs)
        for part in pdfs:
            path = os.path.join(folder, part["filename"])
            if os.path.exists(path):
                continue
            att = gmail.users().messages().attachments().get(
                userId="me", messageId=msg["id"], id=part["body"]["attachmentId"]
            ).execute()
            with open(path, "wb") as f:
                f.write(base64.urlsafe_b64decode(att["data"]))
            print("Downloaded", part["filename"])
            saved += 1
    print(f"{saved} new bills downloaded")


if __name__ == "__main__":
    download_bills()

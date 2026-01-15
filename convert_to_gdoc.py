"""
Convert HTML file in Google Drive to Google Docs format
"""

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os
import pickle
import io

# Google Drive API scopes
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_credentials():
    """Get or create Google API credentials"""
    creds = None
    
    # Check if token.pickle exists (saved credentials)
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If no valid credentials, let user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # You need to create credentials.json from Google Cloud Console
            if not os.path.exists('credentials.json'):
                print("=" * 50)
                print("ERROR: credentials.json not found!")
                print("=" * 50)
                print("""
To create credentials.json:
1. Go to https://console.cloud.google.com
2. Select your project
3. Go to APIs & Services → Credentials
4. Click "Create Credentials" → "OAuth client ID"
5. Select "Desktop app"
6. Download the JSON file
7. Rename it to 'credentials.json'
8. Place it in this folder
                """)
                return None
            
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save credentials for next time
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def convert_html_to_gdoc(file_id, folder_id=None):
    """
    Convert an HTML file to Google Docs format
    
    Args:
        file_id: The ID of the HTML file in Google Drive
        folder_id: The folder ID to save the new doc (optional, uses same folder if not provided)
    """
    creds = get_credentials()
    if not creds:
        return None
    
    service = build('drive', 'v3', credentials=creds)
    
    try:
        # Get the original file info
        file_info = service.files().get(fileId=file_id, fields='name, parents').execute()
        original_name = file_info.get('name', 'Converted Document')
        parents = file_info.get('parents', [])
        
        # Remove .html extension for new name
        new_name = original_name.replace('.html', '').replace('.htm', '')
        
        print(f"Converting: {original_name}")
        print(f"New name: {new_name}")
        
        # Download the HTML content
        request = service.files().get_media(fileId=file_id)
        content = io.BytesIO()
        downloader = MediaIoBaseDownload(content, request)
        
        done = False
        while not done:
            status, done = downloader.next_chunk()
        
        content.seek(0)
        html_content = content.read()
        
        # Save temporarily
        temp_file = 'temp_report.html'
        with open(temp_file, 'wb') as f:
            f.write(html_content)
        
        # Upload as Google Doc (conversion happens automatically)
        file_metadata = {
            'name': new_name,
            'mimeType': 'application/vnd.google-apps.document'  # This triggers conversion!
        }
        
        # Use same folder as original file
        if parents:
            file_metadata['parents'] = parents
        elif folder_id:
            file_metadata['parents'] = [folder_id]
        
        media = MediaFileUpload(temp_file, mimetype='text/html', resumable=True)
        
        new_file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id, name, webViewLink'
        ).execute()
        
        # Clean up temp file
        os.remove(temp_file)
        
        print("=" * 50)
        print("✅ CONVERSION SUCCESSFUL!")
        print("=" * 50)
        print(f"New Document ID: {new_file.get('id')}")
        print(f"Document Name: {new_file.get('name')}")
        print(f"View Link: {new_file.get('webViewLink')}")
        print("=" * 50)
        
        return new_file
        
    except Exception as e:
        print(f"Error: {e}")
        return None

def list_html_files(folder_id=None):
    """List HTML files in Google Drive"""
    creds = get_credentials()
    if not creds:
        return []
    
    service = build('drive', 'v3', credentials=creds)
    
    query = "mimeType='text/html'"
    if folder_id:
        query += f" and '{folder_id}' in parents"
    
    results = service.files().list(
        q=query,
        fields="files(id, name, createdTime, parents)"
    ).execute()
    
    files = results.get('files', [])
    
    print("=" * 50)
    print("HTML FILES IN GOOGLE DRIVE:")
    print("=" * 50)
    
    for i, f in enumerate(files, 1):
        print(f"{i}. {f['name']}")
        print(f"   ID: {f['id']}")
        print(f"   Created: {f.get('createdTime', 'Unknown')}")
        print()
    
    return files

def main():
    print("=" * 50)
    print("   HTML TO GOOGLE DOC CONVERTER")
    print("=" * 50)
    
    # Your folder ID
    folder_id = "1CwmxaJ5LEvokptosoiNx1rHXC-wL110-"  # ProgrammX folder
    
    # List HTML files
    html_files = list_html_files(folder_id)
    
    if not html_files:
        print("No HTML files found!")
        return
    
    # Convert the most recent one (or specify by ID)
    print("\nConverting the most recent HTML file...")
    
    # Get the first file (most recent)
    file_to_convert = html_files[0]
    
    # Convert it
    result = convert_html_to_gdoc(file_to_convert['id'], folder_id)
    
    if result:
        print("\n✅ Done! Check your Google Drive for the new document.")

if __name__ == "__main__":
    main()


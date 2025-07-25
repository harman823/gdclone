import os
from datetime import datetime
from services.auth_handler import is_token_valid

# Import supabase client directly to avoid conflicts
try:
    from utils.supabase_client import supabase
    print(f"✅ Successfully imported supabase client: {type(supabase)}")
except ImportError as e:
    print(f"❌ Failed to import supabase client: {e}")
    # Fallback: create client directly
    from supabase import create_client
    from dotenv import load_dotenv
    load_dotenv()
    
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    print(f"✅ Created supabase client directly: {type(supabase)}")

BUCKET_NAME = 'userfiles'  # Make sure this bucket exists

# Verify supabase client is working
def verify_supabase_client():
    """Verify that the supabase client is properly initialized"""
    try:
        # Check if client has required methods
        if not hasattr(supabase, 'table'):
            raise AttributeError("Supabase client missing 'table' method")
        if not hasattr(supabase, 'storage'):
            raise AttributeError("Supabase client missing 'storage' method")
        
        print("✅ Supabase client verification passed")
        return True
    except Exception as e:
        print(f"❌ Supabase client verification failed: {e}")
        return False

# Run verification on import
verify_supabase_client()

# ✅ Get email of user by user_id
def get_email_by_user_id(user_id):
    try:
        response = supabase.table("users").select("email").eq("id", user_id).execute()
        if response.data and len(response.data) > 0:
            return response.data[0]["email"]
        return None
    except Exception as e:
        print(f"Error getting email for user {user_id}: {e}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        return None

# ✅ Upload file to Supabase bucket
def upload_file(file, token, user_id):
    if not is_token_valid(token):
        return {"error": "Invalid or expired token"}

    email = get_email_by_user_id(user_id)
    if not email:
        return {"error": "User not found"}

    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    file_path = f"{email}/{timestamp}_{file.filename}"
    file_options = {"content-type": file.content_type or "application/octet-stream"}

    try:
        file_data = file.read()
        response = supabase.storage.from_(BUCKET_NAME).upload(file_path, file_data, file_options)
        
        # Handle different response formats
        if hasattr(response, 'error') and response.error:
            return {"error": str(response.error)}
        elif isinstance(response, dict) and 'error' in response:
            return {"error": str(response['error'])}
            
        return {"message": "File uploaded successfully", "path": file_path}
    except Exception as e:
        return {"error": f"Upload failed: {e}"}

# ✅ List all files uploaded by user (by email folder)
def list_userfiles(token, user_id):
    if not is_token_valid(token):
        return {"error": "Invalid or expired token"}

    email = get_email_by_user_id(user_id)
    if not email:
        return {"error": "User not found"}

    try:
        # List files in the user's email folder
        result = supabase.storage.from_(BUCKET_NAME).list(path=email)
        
        # Handle different response formats
        if isinstance(result, list):
            files = result
        elif hasattr(result, 'data') and result.data:
            files = result.data
        elif isinstance(result, dict) and 'error' in result:
            return {"error": f"Storage error: {result['error']}"}
        else:
            files = []

        # Format the response with file details
        formatted_files = []
        for file_obj in files:
            if isinstance(file_obj, dict):
                # Extract file information
                file_info = {
                    "name": file_obj.get("name", ""),
                    "size": file_obj.get("metadata", {}).get("size", 0) if file_obj.get("metadata") else 0,
                    "created_at": file_obj.get("created_at", ""),
                    "updated_at": file_obj.get("updated_at", ""),
                    "content_type": file_obj.get("metadata", {}).get("mimetype", "") if file_obj.get("metadata") else ""
                }
                
                # Only include actual files (not folders)
                if file_info["name"] and not file_info["name"].endswith('/'):
                    formatted_files.append(file_info)

        return {
            "message": f"Found {len(formatted_files)} files",
            "files": formatted_files,
            "user_email": email
        }
        
    except Exception as e:
        print(f"List files error: {e}")
        import traceback
        traceback.print_exc()
        return {"error": f"Listing failed: {str(e)}"}

# ✅ Download a file
def download_file(token, user_id, filename):
    if not is_token_valid(token):
        return {"error": "Invalid or expired token"}

    email = get_email_by_user_id(user_id)
    if not email:
        return {"error": "User not found"}

    file_path = f"{email}/{filename}"

    try:
        result = supabase.storage.from_(BUCKET_NAME).download(file_path)
        return result  # returns a requests.Response object
    except Exception as e:
        return {"error": f"Download failed: {e}"}


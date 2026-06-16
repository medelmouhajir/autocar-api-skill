import requests
import os
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AutoCarClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("AUTOCAR_API_URL", "https://auto.wan.ma")
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def login(self, email, password):
        url = f"{self.base_url}api/v1/Auth/login"
        payload = {"email": email, "password": password}
        
        try:
            response = requests.post(url, json=payload)
            
            if response.status_code == 200:
                data = response.json()
                logger.debug(f"Login response data: {data}")
                logger.debug(f"Available keys in response: {list(data.keys())}")
                
                # Try multiple possible field names for access token
                access_token = (
                    data.get("accessToken") or 
                    data.get("access_token") or 
                    data.get("token") or
                    (data.get("data", {}).get("accessToken") if isinstance(data.get("data"), dict) else None) or
                    (data.get("data", {}).get("access_token") if isinstance(data.get("data"), dict) else None)
                )
                
                # Try multiple possible field names for refresh token
                refresh_token = (
                    data.get("refreshToken") or 
                    data.get("refresh_token") or
                    (data.get("data", {}).get("refreshToken") if isinstance(data.get("data"), dict) else None) or
                    (data.get("data", {}).get("refresh_token") if isinstance(data.get("data"), dict) else None)
                )
                
                if not access_token:
                    logger.error(f"No access token found in response. Full response: {data}")
                    return {
                        "success": False,
                        "message": "Login successful but access token not found in response.",
                        "debug_response": data
                    }
                
                return {
                    "success": True, 
                    "message": "Logged in successfully.", 
                    "accessToken": access_token,
                    "refreshToken": refresh_token
                }
            else:
                logger.error(f"Login failed with status {response.status_code}: {response.text}")
                return {
                    "success": False, 
                    "message": f"Login failed: {response.text}", 
                    "status": response.status_code
                }
        except Exception as e:
            logger.exception(f"Exception during login: {e}")
            return {
                "success": False,
                "message": f"Login error: {str(e)}"
            }

    def request(self, method, endpoint, payload, access_token):
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {access_token}"
        }
        
        try:
            response = requests.request(method, url, json=payload, headers=headers)
            
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "data": response.json() if (response.text and "application/json" in response.headers.get("Content-Type", "")) else response.text
            }
        except Exception as e:
            logger.exception(f"Exception during request: {e}")
            return {
                "success": False,
                "status": getattr(response, "status_code", None),
                "error": str(e),
                "text": getattr(response, "text", "No response")
            }

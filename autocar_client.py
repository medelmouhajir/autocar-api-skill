import requests
import os

class AutoCarClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("AUTOCAR_API_URL", "https://auto.wan.ma")
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def login(self, email, password):
        url = f"{self.base_url}api/v1/Auth/login"
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True, 
                "message": "Logged in successfully.", 
                "accessToken": data.get("accessToken"),
                "refreshToken": data.get("refreshToken")
            }
        else:
            return {
                "success": False, 
                "message": f"Login failed: {response.text}", 
                "status": response.status_code
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
        
        response = requests.request(method, url, json=payload, headers=headers)
        
        try:
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "data": response.json() if (response.text and "application/json" in response.headers.get("Content-Type", "")) else response.text
            }
        except Exception as e:
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "error": str(e),
                "text": response.text
            }

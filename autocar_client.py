import requests
import os

class AutoCarClient:
    def __init__(self, base_url=None):
        self.base_url = base_url or os.getenv("AUTOCAR_API_URL", "https://auto.wan.ma")
        if not self.base_url.endswith("/"):
            self.base_url += "/"

    def _get_headers(self, db):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        token = db.get("accessToken")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def login(self, email, password, db):
        url = f"{self.base_url}api/v1/Auth/login"
        payload = {"email": email, "password": password}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            db["accessToken"] = data.get("accessToken")
            db["refreshToken"] = data.get("refreshToken")
            db["userEmail"] = email
            return {"success": True, "message": "Logged in successfully", "data": data}
        else:
            return {"success": False, "message": f"Login failed: {response.text}", "status": response.status_code}

    def refresh_token(self, db):
        refresh_token = db.get("refreshToken")
        if not refresh_token:
            return False
        
        url = f"{self.base_url}api/v1/Auth/refresh"
        payload = {"refreshToken": refresh_token}
        response = requests.post(url, json=payload)
        
        if response.status_code == 200:
            data = response.json()
            db["accessToken"] = data.get("accessToken")
            db["refreshToken"] = data.get("refreshToken")
            return True
        return False

    def request(self, method, endpoint, payload, db):
        # Remove leading slash if present
        if endpoint.startswith("/"):
            endpoint = endpoint[1:]
        
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(db)
        
        # Try request
        response = requests.request(method, url, json=payload, headers=headers)
        
        # Handle 401 Unauthorized - try refresh
        if response.status_code == 401 and db.get("refreshToken"):
            if self.refresh_token(db):
                headers = self._get_headers(db)
                response = requests.request(method, url, json=payload, headers=headers)
        
        try:
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "data": response.json() if response.text else None
            }
        except Exception as e:
            return {
                "success": response.status_code < 400,
                "status": response.status_code,
                "error": str(e),
                "text": response.text
            }

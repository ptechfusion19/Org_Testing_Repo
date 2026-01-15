import requests
import base64

class RestClient:
    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.base_url = "https://api.dataforseo.com"
    
    def _get_auth_header(self):
        credentials = f"{self.username}:{self.password}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return {"Authorization": f"Basic {encoded}"}
    
    def post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"
        
        # Convert dict with numeric keys to list
        if isinstance(data, dict):
            post_data = [data[key] for key in sorted(data.keys())]
        else:
            post_data = data
            
        try:
            response = requests.post(url, json=post_data, headers=headers)
            return response.json()
        except Exception as e:
            return {
                "status_code": 0,
                "status_message": str(e)
            }
    
    def get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        headers = self._get_auth_header()
        
        try:
            response = requests.get(url, headers=headers)
            return response.json()
        except Exception as e:
            return {
                "status_code": 0,
                "status_message": str(e)
            }


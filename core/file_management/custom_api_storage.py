
try:
    import requests
except:
    requests = None

from typing import Union, List, Dict, Any

from .storage_interface import StorageInterface

class CustomAPIStorage(StorageInterface):
    """
    Implementation of storage via a Custom API.
    Expects endpoints for upload, download, etc.
    """
    def __init__(self, api_url, api_key):
        self.api_url = api_url.rstrip('/')
        self.headers = {'Authorization': f'Bearer {api_key}'}

    def save(self, file, filename: str, path_dir: Union[str, List[str]] = "", access_rights: str = "rw", visibility: str = "private") -> Dict[str, Any]:
        # This is a hypothetical implementation assuming a standard multipart/form-data upload
        safe_path = self._get_safe_path(filename, path_dir)
        
        files = {'file': (filename, file)}
        data = {
            'path': safe_path,
            'access_rights': access_rights,
            'visibility': visibility
        }
        
        try:
            if hasattr(file, 'seek'):
                file.seek(0)
                
            response = requests.post(f"{self.api_url}/upload", files=files, data=data, headers=self.headers)
            response.raise_for_status()
            return response.json() # Expecting metadata back
        except requests.RequestException as e:
            print(f"Custom API Error: {e}")
            return False

    def read(self, filename: str, path_dir: Union[str, List[str]] = "") -> bytes:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.get(f"{self.api_url}/files", params={'path': safe_path}, headers=self.headers)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            raise FileNotFoundError(f"Custom API File {safe_path} not found: {e}")

    def get_metadata(self, filename: str, path_dir: Union[str, List[str]] = "") -> Dict[str, Any]:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.get(f"{self.api_url}/metadata", params={'path': safe_path}, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
             raise FileNotFoundError(f"Custom API Metadata for {safe_path} not found: {e}")

    def update(self, filename: str, new_file, path_dir: Union[str, List[str]] = "") -> bool:
        # Assuming update is same as save/overwrite
        result = self.save(new_file, filename, path_dir)
        return bool(result)

    def delete(self, filename: str, path_dir: Union[str, List[str]] = "") -> bool:
        safe_path = self._get_safe_path(filename, path_dir)
        try:
            response = requests.delete(f"{self.api_url}/files", params={'path': safe_path}, headers=self.headers)
            return response.status_code == 200
        except requests.RequestException:
            return False

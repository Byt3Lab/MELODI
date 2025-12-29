import unittest
from unittest.mock import MagicMock, patch
import sys
import os

# Mock modules that might be missing or trigger unwanted imports
sys.modules['flask'] = MagicMock()
sys.modules['werkzeug'] = MagicMock()
sys.modules['werkzeug.utils'] = MagicMock()
sys.modules['core'] = MagicMock()
sys.modules['core.utils'] = MagicMock()

# Define mocks for utils used in storage.py
def mock_join_paths(*args):
    return "/".join(args)

def mock_create_dir(path):
    pass

sys.modules['core.utils'].join_paths = mock_join_paths
sys.modules['core.utils'].create_dir_if_not_exist = mock_create_dir
sys.modules['werkzeug.utils'].secure_filename = lambda x: x

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import storage
from core.file_management.storage import Storage, LocalStorage, S3Storage, GoogleCloudStorage, CustomAPIStorage

class TestStorageBackends(unittest.TestCase):

    def setUp(self):
        self.mock_app = MagicMock()
        self.mock_app.config = {
            'PATH_DIR_STORAGE': './test_storage',
            'STORAGE_TYPE': 'local'
        }
        self.mock_file = MagicMock()
        self.mock_file.filename = 'test.txt'
        self.mock_file.read.return_value = b'content'

    def test_local_storage_init(self):
        storage = Storage(self.mock_app)
        self.assertIsInstance(storage.backend, LocalStorage)

    @patch('core.file_management.storage.boto3')
    def test_s3_storage_init(self, mock_boto3):
        self.mock_app.config['STORAGE_TYPE'] = 's3'
        self.mock_app.config['AWS_ACCESS_KEY_ID'] = 'key'
        self.mock_app.config['AWS_SECRET_ACCESS_KEY'] = 'secret'
        self.mock_app.config['AWS_BUCKET_NAME'] = 'bucket'
        
        storage = Storage(self.mock_app)
        self.assertIsInstance(storage.backend, S3Storage)
        mock_boto3.client.assert_called_with('s3', aws_access_key_id='key', aws_secret_access_key='secret', region_name=None)

    @patch('core.file_management.storage.gcs')
    def test_gcs_storage_init(self, mock_gcs):
        self.mock_app.config['STORAGE_TYPE'] = 'gcs'
        self.mock_app.config['GCS_BUCKET_NAME'] = 'bucket'
        
        storage = Storage(self.mock_app)
        self.assertIsInstance(storage.backend, GoogleCloudStorage)
        mock_gcs.Client.assert_called()

    def test_custom_api_storage_init(self):
        self.mock_app.config['STORAGE_TYPE'] = 'custom_api'
        self.mock_app.config['CUSTOM_STORAGE_API_URL'] = 'http://api.com'
        self.mock_app.config['CUSTOM_STORAGE_API_KEY'] = 'key'
        
        storage = Storage(self.mock_app)
        self.assertIsInstance(storage.backend, CustomAPIStorage)

    @patch('core.file_management.storage.requests')
    def test_custom_api_save(self, mock_requests):
        self.mock_app.config['STORAGE_TYPE'] = 'custom_api'
        self.mock_app.config['CUSTOM_STORAGE_API_URL'] = 'http://api.com'
        self.mock_app.config['CUSTOM_STORAGE_API_KEY'] = 'key'
        
        storage = Storage(self.mock_app)
        
        mock_response = MagicMock()
        mock_response.json.return_value = {'filename': 'test.txt', 'backend': 'custom'}
        mock_requests.post.return_value = mock_response
        
        result = storage.save(self.mock_file)
        self.assertEqual(result['backend'], 'custom')
        mock_requests.post.assert_called()

if __name__ == '__main__':
    unittest.main()

"""Client"""

class FileClientInterface():
    """Generic Client Interface"""

    def file_upload(self, file_name, file_path):
        """uploads a file"""

    def file_download(self, file_name, download_path):
        """downloads a file"""

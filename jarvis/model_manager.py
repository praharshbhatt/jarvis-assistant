import os
from huggingface_hub import hf_hub_download

class ModelManager:
    """A class to manage the downloading of models from Hugging Face Model Hub."""

    def __init__(self, repo_id, filename, local_dir_relative_path="models"):
        """Initialize the ModelManager with repo_id, filename, and local directory path."""
        self.repo_id = repo_id
        self.filename = filename
        self.local_dir = os.path.join(os.getcwd(), local_dir_relative_path)

    def download_model(self):
        """Download the model from Hugging Face Model Hub. Return True if successful, False otherwise."""
        try:
            hf_hub_download(
                repo_id=self.repo_id,
                filename=self.filename,
                cache_dir=self.filename,
                local_dir=self.local_dir,
            )
            return True
        except Exception as e:
            print(f"An error occurred while downloading the model: {e}")
            return False
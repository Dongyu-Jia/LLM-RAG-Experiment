import os
import subprocess

def download_github_repo(repo_url, dest_folder):
    """
    Downloads a public GitHub repository to a local folder.

    Parameters:
    repo_url (str): The URL of the GitHub repository.
    dest_folder (str): The local destination folder where the repository will be cloned.

    Returns:
    None
    """
    if not os.path.exists(dest_folder):
        os.makedirs(dest_folder)
    
    subprocess.run(['git', 'clone', repo_url, dest_folder], check=True)

# Example usage:
# download_github_repo('https://github.com/user/repo.git', '/path/to/local/folder')
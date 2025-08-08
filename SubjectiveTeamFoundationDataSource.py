import os
import subprocess

from subjective_abstract_data_source_package import SubjectiveDataSource
from brainboost_data_source_logger_package.BBLogger import BBLogger
from brainboost_configuration_package.BBConfig import BBConfig


class SubjectiveTeamFoundationDataSource(SubjectiveDataSource):
    def __init__(self, name=None, session=None, dependency_data_sources=[], subscribers=None, params=None):
        super().__init__(name=name, session=session, dependency_data_sources=dependency_data_sources, subscribers=subscribers, params=params)
        self.params = params

    def fetch(self):
        collection_url = self.params['collection_url']
        repo_name = self.params['repo_name']
        target_directory = self.params['target_directory']
        username = self.params['username']
        password = self.params['password']

        BBLogger.log(f"Starting fetch process for TFS repository '{repo_name}' from '{collection_url}' into directory '{target_directory}'.")

        if not os.path.exists(target_directory):
            try:
                os.makedirs(target_directory)
                BBLogger.log(f"Created directory: {target_directory}")
            except OSError as e:
                BBLogger.log(f"Failed to create directory '{target_directory}': {e}")
                raise

        try:
            BBLogger.log("Configuring TFS credentials.")
            auth_command = [
                'git', 'credential', 'approve'
            ]
            credential_data = f"url={collection_url}\nusername={username}\npassword={password}\n"
            subprocess.run(auth_command, input=credential_data.encode(), check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            repo_url = f"{collection_url}/{repo_name}.git"
            BBLogger.log(f"Cloning TFS repository '{repo_name}' from '{repo_url}'.")
            subprocess.run(['git', 'clone', repo_url], cwd=target_directory, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            BBLogger.log("Successfully cloned TFS repository.")
        except subprocess.CalledProcessError as e:
            BBLogger.log(f"Error cloning TFS repository: {e.stderr.decode().strip()}")
        except Exception as e:
            BBLogger.log(f"Unexpected error cloning TFS repository: {e}")

    # ------------------------------------------------------------------
    def get_icon(self):
        """Return SVG icon content, preferring a local icon.svg in the plugin folder."""
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.svg')
        try:
            if os.path.exists(icon_path):
                with open(icon_path, 'r', encoding='utf-8') as f:
                    return f.read()
        except Exception:
            pass
        return """<svg viewBox=\"0 0 256 256\" xmlns=\"http://www.w3.org/2000/svg\"><rect width=\"256\" height=\"256\" rx=\"24\" fill=\"#6C33AF\"/><path fill=\"#fff\" d=\"M64 96h128v24H64zm0 40h96v24H64z\"/></svg>"""

    def get_connection_data(self):
        """
        Return the connection type and required fields for Team Foundation.
        """
        return {
            "connection_type": "TeamFoundation",
            "fields": ["collection_url", "repo_name", "username", "password", "target_directory"]
        }



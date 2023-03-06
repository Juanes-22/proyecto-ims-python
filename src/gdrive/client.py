import os
import os.path
import logging

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
import httplib2.error

class GoogleDrive:
    SCOPES = ["https://www.googleapis.com/auth/drive"]

    def __init__(self, credentials_json_path: str) -> None:
        self.credentials = ServiceAccountCredentials.from_json_keyfile_name(credentials_json_path, GoogleDrive.SCOPES)
        self.service = build("drive", "v3", credentials=self.credentials)

        # setup logging
        self._logger = logging.getLogger('gdrive')
        self._logger.info(f"Google Drive API initialized")

    def upload_csv_file(self, file_path: str, folder_name: str, parents: list=None) -> None:
        """Upload a csv file to google drive folder

        Args:
            file_path: Path for the csv file
            folder_name: Name of the folder that will contain the file (if not created)
            parents: Parent folder IDs
        """
        try:
            # check if folder exists
            response = self.service.files().list(
                q=f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive'
            ).execute()

            if not response['files']:
                file_metadata = {
                    'name': 'Mediciones',
                    'mimeType': 'application/vnd.google-apps.folder',
                    'parents': parents
                }
                
                # if the folder does not exists, create it
                file = self.service.files().create(
                    body=file_metadata, 
                    fields='id'
                ).execute()

                folder_id = file.get('id')

                self._logger.info("Created folder ID: {}".format(file.get('id')))
            else:
                # store the folder id
                folder_id = response['files'][0]['id']

            # set up the csv file to upload
            file_metadata = {
                'name': os.path.basename(file_path).replace('.csv', ''),
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id]
            }

            media = MediaFileUpload(filename=file_path, mimetype='text/csv')

            # upload the csv file
            uploaded_file = self.service.files().create(body=file_metadata, 
                                                    media_body=media, 
                                                    fields='id').execute()

            self._logger.info(f"Uploaded file ID: {uploaded_file.get('id')}")
        
        except HttpError as e:
            self._logger.error(f"An error ocurred: {e}")

        except httplib2.error.ServerNotFoundError as e:
            self._logger.error(f"An error ocurred: {e}")

        except Exception as e:
            self._logger.error(f"An error ocurred: {e}")

    def delete_file(self, file_id: str) -> None:
        """Permanently delete a file, skipping the trash.

        Args:
            file_id: ID of the file to delete.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
        except HttpError as e:
            self._logger.error(f"An error ocurred: {e}")
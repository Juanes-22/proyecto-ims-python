import os
import os.path

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload


class GoogleDrive:
    def __init__(self) -> None:
        SCOPES = ["https://www.googleapis.com/auth/drive"]

        self.creds = ServiceAccountCredentials.from_json_keyfile_name(os.path.join(os.getcwd(), "src", "gdrive_exporter", "credentials.json"), SCOPES)
        
        # create drive api client
        self.service = build("drive", "v3", credentials=self.creds)

    def upload_csv_file(self, file_path: str, folder_name: str, parents: list=None) -> None:
        try:
            # call the Drive v3 API
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

                file = self.service.files().create(
                    body=file_metadata, 
                    fields='id'
                ).execute()

                folder_id = file.get('id')

                print("Created folder ID: {}".format(file.get('id')))
            else:
                folder_id = response['files'][0]['id']

            file_metadata = {
                'name': os.path.basename(file_path).replace('.csv', ''),
                'mimeType': 'application/vnd.google-apps.spreadsheet',
                'parents': [folder_id]
            }

            media = MediaFileUpload(filename=file_path, mimetype='text/csv')

            uploaded_file = self.service.files().create(body=file_metadata, 
                                                    media_body=media, 
                                                    fields='id').execute()

            print("Uploaded file ID: {}".format(uploaded_file.get('id')))
                        
        except HttpError as error:
            print("An error ocurred: {}".format(error))

    def delete_file(self, file_id):
        """Permanently delete a file, skipping the trash.

        Args:
            service: Drive API service instance.
            file_id: ID of the file to delete.
        """
        try:
            self.service.files().delete(fileId=file_id).execute()
        except HttpError as error:
            print("An error ocurred: {}".format(error))
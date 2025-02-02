from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import logging
import streamlit as st
import pandas as pd
import json
import os
import requests
from PIL import Image
from io import BytesIO
import numpy as np

scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive",
]


def get_sheet(sheetname: str):
    try:
        # Load the credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials1.json", scope
        )

        # Authorize the client
        client = gspread.authorize(creds)

        spreadsheet = client.open(sheetname)
        sheet = spreadsheet.worksheets()[0]

        return sheet

    except:
        # Load the credentials
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials3.json", scope
        )

        # Authorize the client
        client = gspread.authorize(creds)

        spreadsheet = client.open(sheetname)
        sheet = spreadsheet.worksheets()[0]
        return sheet


def get_data(sheetname: str) -> pd.DataFrame:
    try:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials2.json", scope
        )

        # Authorize the client
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheetname)
        sheet = spreadsheet.worksheets()[0]
        # Get all values from the worksheet
        data = sheet.get_all_values()

    except:
        creds = ServiceAccountCredentials.from_json_keyfile_name(
            "credentials3.json", scope
        )

        # Authorize the client
        client = gspread.authorize(creds)
        spreadsheet = client.open(sheetname)
        sheet = spreadsheet.worksheets()[0]
        # Get all values from the worksheet
        data = sheet.get_all_values()

    df = pd.DataFrame(data[1:], columns=data[0])

    fpath = sheetname + ".csv"
    if os.path.exists(fpath):
        os.remove(fpath)

    df.to_csv(fpath, index=False)
    # Convert to DataFrame
    return pd.read_csv(fpath)


@st.cache_data
def create_credentials() -> None:
    for i in range(0, 3):
        file_path = f"credentials{i + 1}.json"

        if not os.path.isfile(f"credentials{i + 1}.json"):
            data = {
                "type": st.secrets[f"credentials{i + 1}"]["type"],
                "project_id": st.secrets[f"credentials{i + 1}"]["project_id"],
                "private_key_id": st.secrets[f"credentials{i + 1}"]["private_key_id"],
                "private_key": st.secrets[f"credentials{i + 1}"]["private_key"],
                "client_email": st.secrets[f"credentials{i + 1}"]["client_email"],
                "client_id": st.secrets[f"credentials{i + 1}"]["client_id"],
                "auth_uri": st.secrets[f"credentials{i + 1}"]["auth_uri"],
                "token_uri": st.secrets[f"credentials{i + 1}"]["token_uri"],
                "auth_provider_x509_cert_url": st.secrets[f"credentials{i + 1}"][
                    "auth_provider_x509_cert_url"
                ],
                "client_x509_cert_url": st.secrets[f"credentials{i + 1}"][
                    "client_x509_cert_url"
                ],
                "universe_domain": st.secrets[f"credentials{i + 1}"]["universe_domain"],
            }

            with open(file_path, "w") as file:
                json.dump(data, file)


def upload_image(file_path, file_name, mime_type, type="bill"):
    """Insert new file to Google Drive.

    Args:
        file_path (str): The path to the file to be uploaded.
        file_name (str): The name to be given to the file on Google Drive.
        mime_type (str): The MIME type of the file.

    Returns:
        str: The ID of the uploaded file.
    """
    scope = [
        "https://www.googleapis.com/auth/drive.file",
    ]

    # Load the credentials
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials3.json", scope)

    try:
        # Create Drive API client
        service = build("drive", "v3", credentials=creds)

        file_metadata = {
            "name": file_name,
            "parents": (
                ["1_7khZLb0MNVydXasSZsKRzbsPzgoyBua"]
                if type == "bill"
                else ["1L74LBwba5afBJF6TyQRcR0EZ3XE6Rnth"]
            ),
        }
        media = MediaFileUpload(file_path, mimetype=mime_type)

        # Upload file
        file = (
            service.files()
            .create(body=file_metadata, media_body=media, fields="id")
            .execute()
        )
        logging.info(
            f'File ID: {file.get("id")}, Web View Link: {file.get("webViewLink")}'
        )
        return file.get("id"), file.get("webViewLink")

    except HttpError as error:
        logging.error(f"An error occurred: {error}")
        return None


def get_image(url: str) -> np.array:
    # Fetch the image
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = np.array(img)
    return img

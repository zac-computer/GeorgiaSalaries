import requests
import os
import zipfile
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DATA_SOURCE_URL = os.getenv("DATA_SOURCE_URL")

DATA_PATH = os.path.join(os.path.dirname(__file__), '..',  'data', 'processed', os.getenv("PROCESSED_DATA_FILE_NAME"))
RAW_DATA_DIR = os.path.join(os.path.join(os.path.dirname(__file__), '..', 'data', 'raw'))
RAW_ZIP_PATH = os.path.join(RAW_DATA_DIR, os.getenv("RAW_DATA_FILE_NAME"))


def download_data():
    response = requests.get(DATA_SOURCE_URL, stream=True)
    with open(RAW_ZIP_PATH, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

def unzip_data():
    with zipfile.ZipFile(RAW_ZIP_PATH, 'r') as zip_ref:
        zip_ref.extractall(RAW_DATA_DIR)

def parse_name(name):
    """
    Get the state employee's first & last name
    :param name: the name as provided in the NAME field
    :return: the employee's first & last name
    """
    pass
    
    
def process_data():
    # Assuming the .txt file has the same name without the .zip extension
    txt_file_path = RAW_ZIP_PATH.replace(".zip", ".txt")
    
    # Here, we'll use pandas for simplicity. Adjust as needed for your processing.
    df = pd.read_csv(txt_file_path, delimiter="\t", encoding='latin-1')  # Assuming tab-delimited. Adjust if different.
    df.to_csv(DATA_PATH, index=False)

def main():
    if not os.path.exists(RAW_ZIP_PATH):  # Only download if not already present
        response = input("Are you sure you want to download the data? (yes/no): ").strip().lower()
        if response not in ['yes', 'y']:
            print("Download aborted.")
            return
        download_data()
    if not os.path.exists(RAW_ZIP_PATH.replace(".zip", ".txt")):
        unzip_data()
    process_data()

if __name__ == "__main__":
    main()

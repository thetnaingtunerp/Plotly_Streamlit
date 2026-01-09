# pip install gspread google-auth
import gspread
import pandas as pd
from google.oauth2.service_account import Credentials

scopes = ["https://www.googleapis.com/auth/spreadsheets.readonly"]
creds = Credentials.from_service_account_file(
    "service_account.json", scopes=scopes
)

client = gspread.authorize(creds)

sheet = client.open("My Google Sheet").sheet1
df = pd.DataFrame(sheet.get_all_records())
print(df.head())
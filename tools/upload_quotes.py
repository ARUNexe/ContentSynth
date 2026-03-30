import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

cred = credentials.Certificate("secrets/firebase_cred_secret.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL")
})

ref = db.reference("/conversations")

def upload_quote(quote_id, dialogue1, dialogue2):
    quote_data = {
        "dialogue1": dialogue1,
        "dialogue2": dialogue2
    }
    print(f"Uploading quote  {quote_id} :  {quote_id} and {quote_data} to Firebase. ",end="\n")
    ref.child("source").child("{}".format(quote_id)).set(quote_data)
    print(f"Uploaded quote {quote_id} and {quote_data} to Firebase.",end="\n")

def upload_all_from_csv(csv_path="resources/csv/quotes.csv"):
    quotes_df = pd.read_csv(csv_path)
    for index, row in quotes_df.iterrows():
        upload_quote(
            quote_id=row['s.no'],
            dialogue1=row['person1'],
            dialogue2=row['person2']
        )

def add_control_node():
    control_data = {
        "total_quotes": 100,
        "current_index": 0
    }
    ref.child("control").set(control_data)


upload_all_from_csv("resources/csv/prx_sonar_resoning.csv")
# add_control_node()
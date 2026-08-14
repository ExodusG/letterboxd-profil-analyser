import pandas as pd
from src.db.queries.qr_errors import *

class ErrorService:
    def add_error_db(self,df):
        if df.empty:
                return
        # On garde uniquement les colonnes nécessaires
        df = df[["Name", "Year"]].rename(
            columns={
                "Name": "title",
                "Year": "year"
            }
        )
    
        # Nettoyage
        df["year"] = pd.to_numeric(
            df["year"],
            errors="coerce"
        )
    
        df = df.dropna(subset=["title", "year"])
    
        df["year"] = df["year"].astype(int)
    
        records = df.to_dict(orient="records")
        add_error(records);
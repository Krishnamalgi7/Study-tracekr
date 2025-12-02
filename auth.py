import pandas as pd
import uuid
import bcrypt

class Auth:
    def __init__(self, storage):
        self.storage = storage
        self.users_file = "users.csv"
        self.storage.ensure_file(self.users_file, ["user_id", "email", "hashed_password"])

    def _load_users_df(self):
        df = self.storage.read_csv(self.users_file)
        if df is None:
            df = pd.DataFrame(columns=["user_id", "email", "hashed_password"])
        return df

    def _save_users_df(self, df):
        self.storage.write_csv(self.users_file, df)

    def register(self, email: str, password: str):
        if not email or not password:
            return False
        df = self._load_users_df()
        if not df.empty and email.lower() in df["email"].str.lower().tolist():
            return False
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        user_id = str(uuid.uuid4())
        row = {"user_id": user_id, "email": email.strip(), "hashed_password": hashed.decode("utf-8")}
        self.storage.append_row(self.users_file, row)
        return True

    def login(self, email: str, password: str):
        if not email or not password:
            return None
        df = self._load_users_df()
        if df.empty:
            return None
        matches = df[df["email"].str.lower() == email.strip().lower()]
        if matches.empty:
            return None
        record = matches.iloc[0].to_dict()
        hashed = record.get("hashed_password", "").encode("utf-8")
        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), hashed)
        except Exception:
            ok = False
        if ok:
            return {"user_id": record["user_id"], "email": record["email"]}
        return None

    def get_user(self, user_id: str):
        df = self._load_users_df()
        if df.empty:
            return None
        matches = df[df["user_id"] == user_id]
        if matches.empty:
            return None
        rec = matches.iloc[0].to_dict()
        return {"user_id": rec["user_id"], "email": rec["email"]}

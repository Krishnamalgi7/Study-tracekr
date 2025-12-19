import pandas as pd
import uuid
import bcrypt
import re


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

    def validate_email(self, email: str):
        """Validate email format - must contain @"""
        if not email or '@' not in email:
            return False, "Email must contain @"

        # Basic email regex pattern
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(pattern, email):
            return False, "Invalid email format"

        return True, "Valid"

    def validate_password(self, password: str):
        """
        Validate password strength:
        - At least 8 characters
        - Contains at least one letter
        - Contains at least one number
        - Contains at least one special character
        """
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters"

        has_letter = re.search(r'[a-zA-Z]', password)
        has_number = re.search(r'\d', password)
        has_special = re.search(r'[!@#$%^&*(),.?":{}|<>]', password)

        if not has_letter:
            return False, "Password must contain at least one letter"
        if not has_number:
            return False, "Password must contain at least one number"
        if not has_special:
            return False, "Password must contain at least one special character (!@#$%^&*...)"

        return True, "Valid"

    def register(self, email: str, password: str):
        """Register with validation"""
        if not email or not password:
            return False, "Email and password are required"

        # Validate email
        email_valid, email_msg = self.validate_email(email)
        if not email_valid:
            return False, email_msg

        # Validate password
        pwd_valid, pwd_msg = self.validate_password(password)
        if not pwd_valid:
            return False, pwd_msg

        # Check if email already exists
        df = self._load_users_df()
        if not df.empty and email.lower() in df["email"].str.lower().tolist():
            return False, "Email already registered"

        # Create user
        password_bytes = password.encode("utf-8")
        hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
        user_id = str(uuid.uuid4())
        row = {"user_id": user_id, "email": email.strip(), "hashed_password": hashed.decode("utf-8")}
        self.storage.append_row(self.users_file, row)
        return True, "Account created successfully"

    def login(self, email: str, password: str):
        """Login with validation"""
        if not email or not password:
            return None, "Email and password are required"

        # Validate email format
        email_valid, email_msg = self.validate_email(email)
        if not email_valid:
            return None, email_msg

        df = self._load_users_df()
        if df.empty:
            return None, "Invalid credentials"

        matches = df[df["email"].str.lower() == email.strip().lower()]
        if matches.empty:
            return None, "Invalid credentials"

        record = matches.iloc[0].to_dict()
        hashed = record.get("hashed_password", "").encode("utf-8")

        try:
            ok = bcrypt.checkpw(password.encode("utf-8"), hashed)
        except Exception:
            ok = False

        if ok:
            return {"user_id": record["user_id"], "email": record["email"]}, "Login successful"

        return None, "Invalid credentials"

    def get_user(self, user_id: str):
        df = self._load_users_df()
        if df.empty:
            return None
        matches = df[df["user_id"] == user_id]
        if matches.empty:
            return None
        rec = matches.iloc[0].to_dict()
        return {"user_id": rec["user_id"], "email": rec["email"]}

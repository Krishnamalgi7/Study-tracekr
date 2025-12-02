import pandas as pd
import os

class Storage:
    def __init__(self, base_path):
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path, exist_ok=True)

    def _file_path(self, filename):
        return os.path.join(self.base_path, filename)

    def ensure_file(self, filename, headers):
        path = self._file_path(filename)
        if not os.path.exists(path):
            df = pd.DataFrame(columns=headers)
            df.to_csv(path, index=False)

    def ensure_all_files_exist(self):
        self.ensure_file("users.csv", ["user_id", "email", "hashed_password"])
        self.ensure_file("study_plans.csv", ["user_id", "subject", "goal", "planned_hours", "date"])
        self.ensure_file("study_logs.csv", ["user_id", "date", "subject", "hours_studied"])

    def read_csv(self, filename):
        path = self._file_path(filename)
        if not os.path.exists(path):
            return None
        try:
            return pd.read_csv(path)
        except Exception:
            return None

    def write_csv(self, filename, df):
        path = self._file_path(filename)
        df.to_csv(path, index=False)

    def append_row(self, filename, row_dict):
        df = self.read_csv(filename)
        if df is None or df.empty:
            df = pd.DataFrame(columns=row_dict.keys())
        df = pd.concat([df, pd.DataFrame([row_dict])], ignore_index=True)
        self.write_csv(filename, df)

    def update_csv(self, filename, df):
        self.write_csv(filename, df)

    def delete_row(self, filename, index):
        df = self.read_csv(filename)
        if df is None or index not in df.index:
            return
        df = df.drop(index)
        self.write_csv(filename, df)

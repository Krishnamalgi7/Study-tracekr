import pandas as pd
import os


class Storage:
    def __init__(self, data_dir="data"):
        self.data_dir = str(data_dir)
        os.makedirs(self.data_dir, exist_ok=True)

    def _get_path(self, filename):
        return os.path.join(self.data_dir, filename)

    def ensure_file(self, filename, columns):
        """Creates a CSV with specific column headers if it doesn't exist."""
        path = self._get_path(filename)
        if not os.path.exists(path):
            # Create DataFrame with specific columns
            df = pd.DataFrame(columns=columns)
            df.to_csv(path, index=False)

    def ensure_all_files_exist(self):
        """Creates basic study files with REQUIRED columns."""
        # We explicitly define the columns here so pandas doesn't crash later

        # 1. Study Logs (Fixes KeyError: 'hours_studied')
        self.ensure_file("study_logs.csv", [
            "user_id", "subject", "date", "hours_studied", "notes"
        ])

        # 2. Study Plans
        self.ensure_file("study_plans.csv", [
            "user_id", "subject", "goal_hours", "deadline", "status"
        ])

    def read_csv(self, filename):
        path = self._get_path(filename)
        if not os.path.exists(path):
            return pd.DataFrame()

        try:
            return pd.read_csv(path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame()
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            return pd.DataFrame()

    def write_csv(self, filename, df):
        path = self._get_path(filename)
        df.to_csv(path, index=False)

    def append_row(self, filename, row_dict):
        df = self.read_csv(filename)
        new_row_df = pd.DataFrame([row_dict])

        if df.empty:
            df = new_row_df
        else:
            # Handle empty columns or mismatches gracefully
            new_row_df = new_row_df.dropna(axis=1, how='all')
            df = pd.concat([df, new_row_df], ignore_index=True)

        self.write_csv(filename, df)
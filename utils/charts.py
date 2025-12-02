import pandas as pd
import plotly.express as px

def daily_chart(df):
    df["date"] = pd.to_datetime(df["date"])
    daily = df.groupby("date")["hours_studied"].sum().reset_index()
    return px.line(daily, x="date", y="hours_studied")

def subject_pie(df):
    subject_sum = df.groupby("subject")["hours_studied"].sum().reset_index()
    return px.pie(subject_sum, names="subject", values="hours_studied", hole=0.4)

def goals_vs_actual(plans, logs):
    merged = pd.merge(plans, logs, on=["user_id", "subject"], how="left")
    merged["hours_studied"] = merged["hours_studied"].fillna(0)
    grouped = merged.groupby("subject", as_index=False).agg({"planned_hours": "sum", "hours_studied": "sum"})
    return px.bar(grouped, x="subject", y=["planned_hours", "hours_studied"], barmode="group")

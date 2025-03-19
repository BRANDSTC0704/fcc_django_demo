from dash import dcc, html, Output, Input
import plotly.express as px
from django_plotly_dash import DjangoDash
from preprocessing import get_cleaned_work_hours
import pandas as pd

df = get_cleaned_work_hours()

weekly_app = DjangoDash("WeeklyDashboard")

weekly_app.layout = html.Div([
    dcc.DatePickerRange(
        id="weekly-date-picker",
        min_date_allowed=df["date"].min().date(),
        max_date_allowed=df["date"].max().date(),
        start_date=df["date"].min().date(),
        end_date=df["date"].max().date(),
        display_format="YYYY-MM-DD",
    ),
    dcc.Graph(id="weekly-plot"),
])

@weekly_app.callback(
    Output("weekly-plot", "figure"),
    [Input("weekly-date-picker", "start_date"), Input("weekly-date-picker", "end_date")]
)
def update_weekly_graph(start_date, end_date):
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if filtered_df.empty:
        return px.bar(title="No data")

    filtered_df["week"] = filtered_df["date"].dt.strftime("%Y-W%U")
    weekly_data = filtered_df.groupby("week", as_index=False)["difference"].sum()
    return px.bar(weekly_data, x="week", y="difference", title="Work Hours per Week")
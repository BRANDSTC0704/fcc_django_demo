from dash import dcc, html, Output, Input
import plotly.express as px
from django_plotly_dash import DjangoDash
from preprocessing import get_cleaned_work_hours
import pandas as pd

df = get_cleaned_work_hours()

monthly_app = DjangoDash("MonthlyDashboard")

monthly_app.layout = html.Div([
    dcc.DatePickerRange(
        id="monthly-date-picker",
        min_date_allowed=df["date"].min().date(),
        max_date_allowed=df["date"].max().date(),
        start_date=df["date"].min().date(),
        end_date=df["date"].max().date(),
        display_format="YYYY-MM-DD",
    ),
    dcc.Graph(id="monthly-plot"),
])

@monthly_app.callback(
    Output("monthly-plot", "figure"),
    [Input("monthly-date-picker", "start_date"), Input("monthly-date-picker", "end_date")]
)
def update_monthly_graph(start_date, end_date):
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)]
    if filtered_df.empty:
        return px.bar(title="No data")

    filtered_df["month"] = filtered_df["date"].dt.strftime("%Y-%m")
    monthly_data = filtered_df.groupby("month", as_index=False)["difference"].sum()
    return px.bar(monthly_data, x="month", y="difference", title="Work Hours per Month")

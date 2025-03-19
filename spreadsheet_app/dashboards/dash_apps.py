from dash import dcc, html
import dash
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash

# Weekly Dashboard
weekly_app = DjangoDash("WeeklyDashboard")  # Ensure correct name!

weekly_app.layout = html.Div([
    dcc.Graph(id="weekly-graph")
])

@weekly_app.callback(
    dash.Output("weekly-graph", "figure"),
    dash.Input("weekly-graph", "id")  # Placeholder input
)
def update_weekly_graph(_):
    df = pd.DataFrame({"Week": ["W1", "W2", "W3"], "Hours": [15, 25, 35]})
    fig = px.bar(df, x="Week", y="Hours", title="Weekly Work Hours")
    return fig

# Monthly Dashboard
monthly_app = DjangoDash("MonthlyDashboard")  # Ensure correct name!

monthly_app.layout = html.Div([
    dcc.Graph(id="monthly-graph")
])

@monthly_app.callback(
    dash.Output("monthly-graph", "figure"),
    dash.Input("monthly-graph", "id")  # Placeholder input
)
def update_monthly_graph(_):
    df = pd.DataFrame({"Month": ["Jan", "Feb", "Mar"], "Hours": [10, 20, 30]})
    fig = px.bar(df, x="Month", y="Hours", title="Monthly Work Hours")
    return fig

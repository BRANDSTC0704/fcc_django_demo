from dash import dcc, html, Output, Input, State
import dash
import pandas as pd
import plotly.express as px
from django_plotly_dash import DjangoDash
from .preprocessing import get_cleaned_work_hours
import io

df = get_cleaned_work_hours()

# Weekly Dashboard
weekly_app = DjangoDash("WeeklyDashboard", 
                        external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    ],)  # Ensure correct name!

#weekly_app.layout = html.Div([
#    dcc.Graph(id="weekly-graph")
#])

weekly_app.layout = html.Div(
    [
        # html.H1("Work Hours Dashboard", className="text-center"),
        # Date Picker
        html.Div(
            [
                dcc.DatePickerRange(
                    id="date-picker",
                    min_date_allowed=df["date"].min().date(),
                    max_date_allowed=df["date"].max().date(),
                    start_date=df["date"].min().date(),
                    end_date=df["date"].max().date(),
                    display_format="YYYY-MM-DD",
                )
            ],
            className="text-center mt-3",
        ),
        dcc.Graph(id="weekly-plot"),
        # dcc.Graph(id="monthly-plot"),
        dcc.Store(id="filtered-data"),  # Store filtered data
        html.Div(
            [
                html.Button(
                    "Excel-Download",
                    id="download-btn",
                    n_clicks=0,
                    className="btn btn-success",
                ),
                dcc.Download(id="download"),
            ],
            style={"textAlign": "center", "marginTop": "15px"},
        ),
    ]
)


@weekly_app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    State("filtered-data", "data"),  # Retrieve filtered data stored in a hidden Div
    prevent_initial_call=True,
)
def download_excel(n_clicks, json_data):
    if not n_clicks:  # Ensure callback runs only when button is clicked
        return dash.no_update

    if json_data is None:  # Handle case where no data is available
        return dash.no_update

    # Convert stored JSON back to DataFrame
    filtered_df = pd.read_json(io.StringIO(json_data))

    # Generate Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        filtered_df.to_excel(writer, sheet_name="Filtered Data", index=False)

    output.seek(0)  # Move cursor to the beginning
    return dcc.send_bytes(output.read(), filename="filtered_work_hours.xlsx")


@weekly_app.callback(
    [
        Output("weekly-plot", "figure"),
        Output("filtered-data", "data"),
    ],  # Store the filtered data
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")],
)
def update_graphs(start_date, end_date, df=df):
    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    # Ensure filtering worked
    if filtered_df.empty:
        return px.bar(title="No data"), px.bar(title="No data"), "{}"

    # Group Data by Week & Month
    filtered_df["week"] = filtered_df["date"].dt.strftime("%Y-W%U")
    filtered_df["month"] = filtered_df["date"].dt.strftime("%Y-%m")

    
    weekly_data = (
        filtered_df.groupby("week", as_index=False)["difference"]
        .sum()
        .reset_index(drop=True)
    )
    
    weekly_data.columns = ["week", "Total Hours"]
    # Weekly Figure
    weekly_fig = px.bar(
        weekly_data,
        x="week",
        y="Total Hours",
        title="Work Hours per Week",
        text=weekly_data["Total Hours"].astype(int),
    )
    weekly_fig.update_xaxes(type="category")
    weekly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Week: %{x} <br>Total Hours: %{y:.0f} Stunden",
    )
    weekly_fig.update_yaxes(range=[0, weekly_data["Total Hours"].max() + 5])
    
    return weekly_fig, filtered_df.to_json()
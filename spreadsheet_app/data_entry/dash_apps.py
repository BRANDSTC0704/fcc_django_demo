from dash import dcc, html, Output, Input, State
import pandas as pd
import io
import dash
from dash.dash_table import DataTable
from django_plotly_dash import DjangoDash
import plotly.express as px
from .models import WorkHours
from dash.exceptions import PreventUpdate
from .models import Employee, WorkCategory, WorkHours, ContainerCount, Protocollist


work_hours_data = WorkHours.objects.all()

# selected_start_date = request.GET.get("start_date")
# selected_end_date = request.GET.get("end_date")


def convert_time_difference(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours + minutes / 60  # Convert to float
    except ValueError:
        return 0.0  # Default in case of an error


# Convert to DataFrame
df = pd.DataFrame.from_records(
    work_hours_data.values("created_at", "start_time", "end_time")
)
# Convert 'date' to datetime
df["date"] = pd.to_datetime(df["created_at"], utc=True)

df["difference"] = [wh.difference for wh in work_hours_data]
df["difference"] = df["difference"].apply(lambda x: convert_time_difference(x))
df["difference"] = df["difference"].astype(float)  # Convert to numeric

# print(df['date'].min(), df['date'].max())

# Create Dash App
app = DjangoDash(
    "WorkHoursDashboard",
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    ],
)  # Unique name for each Dash app


app.layout = html.Div(
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
        dcc.Graph(id="monthly-plot"),
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

# Callback to generate Excel file
# print("✅ WorkHoursDashboard Loaded Successfully!")


@app.callback(
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


@app.callback(
    [
        Output("weekly-plot", "figure"),
        Output("monthly-plot", "figure"),
        Output("filtered-data", "data"),
    ],  # Store the filtered data
    [Input("date-picker", "start_date"), Input("date-picker", "end_date")],
)
def update_graphs(start_date, end_date):
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
    monthly_data = (
        filtered_df.groupby("month", as_index=False)["difference"]
        .sum()
        .reset_index(drop=True)
    )

    weekly_data.columns = ["week", "Total Hours"]
    monthly_data.columns = ["month", "Total Hours"]

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

    # Monthly Figure
    monthly_fig = px.bar(
        monthly_data,
        x="month",
        y="Total Hours",
        title="Work Hours per Month",
        text=monthly_data["Total Hours"].astype(int),
    )
    monthly_fig.update_xaxes(type="category")
    monthly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Month: %{x} <br>Total Hours: %{y:.0f} Stunden",
    )
    monthly_fig.update_yaxes(range=[0, monthly_data["Total Hours"].max() + 5])

    return weekly_fig, monthly_fig, filtered_df.to_json()

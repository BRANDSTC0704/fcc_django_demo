from dash import dcc, html, Output, Input, State
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from .preprocessing import get_cleaned_work_hours, get_cleaned_employee, date_allowed
import io
import datetime

min_date, max_date = date_allowed()

# Weekly Dashboard
weekly_app = DjangoDash(
    "WeeklyDashboard",
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    ],
)  # Ensure correct name!

# weekly_app.layout = html.Div([
#    dcc.Graph(id="weekly-graph")
# ])

weekly_app.layout = html.Div(
    [
        # html.H1("Work Hours Dashboard", className="text-center"),
        # Date Picker
        html.Div(
            [
                dcc.DatePickerSingle(id="week-picker",  
                                    display_format='YYYY-W',  # Display year and week number
                                    placeholder='Wochenwahl', 
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date, 
                                    first_day_of_week=1, 
                                    initial_visible_month=max_date,
                                    date=max_date)
            ],
            className="text-center mt-3",
        ),
        html.Div(id='date-range-output',  className="text-left mt-3",),
        
        dcc.Graph(id="employee_plot"),
        dcc.Graph(id="workhours_plot"),
        dcc.Store(id="json_data_workhours"),  # Store filtered data
        dcc.Store(id="json_data_employee"),  # Store filtered data
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


# Datefilter Week
@weekly_app.callback(
    # Output('output-container', 'children'),
    Output('date-range-output', 'children'),
    # Output('selected-range-display', 'children'), #Added output to display the range
    Input('week-picker', 'date')
)
def update_output(selected_date):
    if selected_date:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        year, week_num, day_of_week = selected_date.isocalendar()

        # Get the first day of the selected week (Monday)
        first_day_of_week = datetime.date.fromisocalendar(year, week_num, 1)
        last_day_of_week = first_day_of_week + datetime.timedelta(days=6)

        # Generate a list of dates for the entire week
        # week_dates = [first_day_of_week + datetime.timedelta(days=i) for i in range(7)]
        # date_strings = [date.strftime('%Y-%m-%d') for date in week_dates]

        return (
            # html.Div(f"Dates in Week {week_num}: {', '.join(date_strings)}"), 
            # html.Div(f"Start Date: {first_day_of_week.strftime('%Y-%m-%d')}, End Date: {last_day_of_week.strftime('%Y-%m-%d')}"), 
            html.Div(f"Datumsauswahl: {first_day_of_week.strftime('%d.%m.%Y')} - {last_day_of_week.strftime('%d.%m.%Y')}") #Return the display
           )
    else:
        return "Select a week to see dates."

# Excel-Download
@weekly_app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    State(
        "json_data_workhours", "data"
    ),  # Retrieve filtered data stored in a hidden Div
    State("json_data_employee", "data"), 
    prevent_initial_call=True,
)
def download_excel(n_clicks, json_data_workhours, json_data_employee):
    if not n_clicks:  # Ensure callback runs only when button is clicked
        return dash.no_update

    if json_data_workhours is None:  # Handle case where no data is available
        return dash.no_update

    # Convert stored JSON back to DataFrame
    filtered_df_wh = pd.read_json(io.StringIO(json_data_workhours))
    filtered_df_emp = pd.read_json(io.StringIO(json_data_employee))
    
    # Generate Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        filtered_df_wh.to_excel(writer, sheet_name="Betriebsstunden", index=False, header=True)
        filtered_df_emp.to_excel(writer, sheet_name="Arbeiterstunden", index=False, header=True)

    output.seek(0)  # Move cursor to the beginning
    return dcc.send_bytes(output.read(), filename="Wochenübersicht.xlsx")


# work hours_plot
@weekly_app.callback(
    [
        Output("workhours_plot", "figure"),
        Output("json_data_workhours", "data"),
    ],  # Store the filtered data
    [Input("week-picker", "date")],
)
def update_graphs_wh(selected_date):

    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    year, week_num, day_of_week = selected_date.isocalendar()

    start_date = datetime.date.fromisocalendar(year, week_num, 1)
    end_date = start_date + datetime.timedelta(days=6)

    df = get_cleaned_work_hours()

    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    # Ensure filtering worked
    if filtered_df.empty:
        return px.bar(title="No data"), px.bar(title="No data"), "{}"

    # Group Data by Week & Month
    filtered_df["week"] = filtered_df["date"].dt.strftime("%Y-W%U")

    weekly_data = (
        filtered_df.groupby("week", as_index=False)["difference"]
        .sum()
        .reset_index(drop=True)
    )
    weekly_data.columns = ["Woche", "Gesamtstunden"]
    # print(weekly_data)

    # Weekly Figure
    weekly_fig = px.bar(
        weekly_data,
        x="Woche",
        y="Gesamtstunden",
        title="Betriebsstunden pro Woche",
        text=weekly_data["Gesamtstunden"].astype(int),
    )
    weekly_fig.update_xaxes(type="category")
    weekly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Woche: %{x} <br>Gesamtstunden: %{y:.0f} Stunden",
    )
    weekly_fig.update_yaxes(range=[0, weekly_data["Gesamtstunden"].max() + 5])

    return weekly_fig, filtered_df.to_json()


# employee
@weekly_app.callback(
    [
        Output("employee_plot", "figure"),
        Output("json_data_employee", "data"),
    ],  # Store the filtered data
    [Input("week-picker", "date")],
)
def update_graphs_emp(selected_date):
    
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    year, week_num, day_of_week = selected_date.isocalendar()

    start_date = datetime.date.fromisocalendar(year, week_num, 1)
    end_date = start_date + datetime.timedelta(days=6)

    df = get_cleaned_employee()

    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    def convert_timestamp(timestamp):
        if pd.isna(timestamp):
            return None  # Handle NaN values

        if isinstance(timestamp, pd.Timestamp):
            # Already a Timestamp, convert to timezone-unaware datetime
            return timestamp.tz_localize(None)

        else:
            # Convert numerical timestamp to datetime object
            seconds = timestamp / 1000.0  # Convert milliseconds to seconds
            datetime_object = datetime.datetime.utcfromtimestamp(seconds).replace(tzinfo=None) #remove timezone.
            return datetime_object #return the datetime object directly, not a string

    df["work_start"] = df["work_start"].apply(convert_timestamp)
    df["work_end"] = df["work_end"].apply(convert_timestamp)
    
    # Explicitly convert to datetime64[ns]
    df["work_start"] = pd.to_datetime(df["work_start"])
    df["work_end"] = pd.to_datetime(df["work_end"])
    
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    # Ensure filtering worked
    if filtered_df.empty:
        return px.bar(title="No data"), px.bar(title="No data"), "{}"

    # Group Data by Week & Month
    filtered_df["week"] = filtered_df["date"].dt.strftime("%Y-W%U")

    weekly_data = (
        filtered_df.groupby(["week", "name"], as_index=False)["work_time"]
        .sum()
        .reset_index(drop=True)
    )

    weekly_data.columns = ["Woche", "Name", "Gesamtstunden"]
    # print(weekly_data)

    # Weekly Figure
    weekly_fig = go.Figure(layout=dict(template="plotly"))
    weekly_fig = px.bar(
        weekly_data,
        y="Woche",
        x="Gesamtstunden",
        color="Name",
        title="Arbeitsstunden pro Woche",
        orientation="h",
        barmode="group",
        text=round(weekly_data["Gesamtstunden"], 1),
    )
    weekly_fig.update_yaxes(type="category")
    weekly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Woche: %{x} <br>Gesamtstunden: %{x:.0f} Stunden",
    )
    weekly_fig.update_xaxes(range=[0, weekly_data["Gesamtstunden"].max() + 5])

    return weekly_fig, filtered_df.to_json()

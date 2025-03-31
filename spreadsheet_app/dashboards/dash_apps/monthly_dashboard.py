from dash import dcc, html, Output, Input, State
import dash
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from django_plotly_dash import DjangoDash
from .preprocessing import (get_cleaned_work_hours, get_cleaned_employee, 
                            date_allowed, get_cleaned_wcat, get_cleaned_cont, 
                            get_cleaned_prot)
import io
import datetime

min_date, max_date = date_allowed()

# Monthly Dashboard
monthly_app = DjangoDash(
    "MonthlyDashboard",
    external_stylesheets=[
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css"
    ],
)  # Ensure correct name!


monthly_app.layout = html.Div(
    [
        # html.H1("Work Hours Dashboard", className="text-center"),
        # Date Picker
        html.Div(
            [
                dcc.DatePickerSingle(id="month-picker",  
                                    display_format='YYYY-W',  # Display year and month number
                                    placeholder='Monatswahl', 
                                    min_date_allowed=min_date,
                                    max_date_allowed=max_date, 
                                    first_day_of_week=1, 
                                    initial_visible_month=max_date,
                                    date=max_date)
            ],
            className="text-center mt-3",
        ),
        html.H2(id='date-range-output',  className="text-center mt-3",),
        
        dcc.Graph(id="employee_plot"),
        dcc.Graph(id="workhours_plot"),
        dcc.Store(id="json_data_workhours"),  # Store filtered data
        dcc.Store(id="json_data_employee"),  # Store filtered data
        dcc.Store(id="json_data_wcat"),  # Store filtered data
        dcc.Store(id="json_data_cont"),  # Store filtered data
        dcc.Store(id="json_data_prot"),  # Store filtered data
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
        dcc.Graph(id="workcat_plot"),
        dcc.Graph(id="cont_plot"),
    ]
)


# Datefilter Month
@monthly_app.callback(
    Output('date-range-output', 'children'),
    Input('month-picker', 'date')
)
def update_output(selected_date):
    if selected_date:
        # Convert input to date object
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()

        # Extract year and month
        year, month = selected_date.year, selected_date.month

        # First and last day of the month
        first_day = datetime.date(year, month, 1)
        last_day = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

        return html.Div(f"Datumsauswahl: {first_day.strftime('%d.%m.%Y')} - {last_day.strftime('%d.%m.%Y')}")
    
    return "Select a month to see dates."

# Excel-Download
@monthly_app.callback(
    Output("download", "data"),
    Input("download-btn", "n_clicks"),
    State("json_data_workhours", "data"), 
    State("json_data_employee", "data"), 
    State("json_data_wcat", "data"), 
    State("json_data_cont", "data"), 
    State("json_data_prot", "data"), 
    prevent_initial_call=True,
)
def download_excel(n_clicks, json_data_workhours, json_data_employee, 
                   json_data_wcat, json_data_cont, json_data_prot):
    if not n_clicks:
        return dash.no_update

    if json_data_workhours is None:
        return dash.no_update

    # Convert JSON to DataFrame
    filtered_df_wh = pd.read_json(io.StringIO(json_data_workhours))
    filtered_df_emp = pd.read_json(io.StringIO(json_data_employee))
    filtered_df_wcat = pd.read_json(io.StringIO(json_data_wcat))
    filtered_df_cont = pd.read_json(io.StringIO(json_data_cont))
    filtered_df_prot = pd.read_json(io.StringIO(json_data_prot))
    
    filtered_df_wh["start_time"] = filtered_df_wh["start_time"].dt.strftime("%H:%M:%S") 
    filtered_df_wh["end_time"] = filtered_df_wh["end_time"].dt.strftime("%H:%M:%S") 
    
    # Generate Excel file
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter", datetime_format="yyyy-mm-dd hh:mm:ss") as writer:
        filtered_df_wh.to_excel(writer, sheet_name="Betriebsstunden", index=False, header=True)
        filtered_df_emp.to_excel(writer, sheet_name="Arbeiterstunden", index=False, header=True)
        filtered_df_wcat.to_excel(writer, sheet_name="Betriebskategorie_Detail", index=False, header=True)
        filtered_df_cont.to_excel(writer, sheet_name="Anzahl_Container", index=False, header=True)
        filtered_df_prot.to_excel(writer, sheet_name="Protokollist", index=False, header=True)

        workbook = writer.book
        date_format = workbook.add_format({'num_format': 'yyyy-mm-dd'})
        datetime_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss'})

        # Adjust column widths and format datetime correctly
        def adjust_columns(df, sheet):
            worksheet = writer.sheets[sheet]
            for i, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col)) + 2
                worksheet.set_column(i, i, max_length)

                if pd.api.types.is_datetime64_any_dtype(df[col]):
                    for row_num, value in enumerate(df[col]):
                        if pd.notna(value):  # Avoid NaN issues
                            if value.time() == pd.Timestamp("00:00:00").time():
                                worksheet.write_datetime(row_num + 1, i, value, date_format)  # Date only
                            else:
                                worksheet.write_datetime(row_num + 1, i, value, datetime_format)  # Full datetime

        adjust_columns(filtered_df_wh, "Betriebsstunden")
        adjust_columns(filtered_df_emp, "Arbeiterstunden")
        adjust_columns(filtered_df_wcat, "Betriebskategorie_Detail")
        adjust_columns(filtered_df_cont, "Anzahl_Container")
        adjust_columns(filtered_df_prot, "Protokollist")

    output.seek(0)
    return dcc.send_bytes(output.read(), filename="Monatsübersicht.xlsx")


# work hours_plot
@monthly_app.callback(
    [
        Output("workhours_plot", "figure"),
        Output("json_data_workhours", "data"),
    ],  # Store the filtered data
    [Input("month-picker", "date")],
)
def update_graphs_wh(selected_date):

    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    # Extract year and month
    year, month = selected_date.year, selected_date.month
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    df = get_cleaned_work_hours()

    # Convert start and end dates to datetime
    start_date = pd.to_datetime(start_date, utc=True)
    end_date = pd.to_datetime(end_date, utc=True)

    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    # Ensure filtering worked
    if filtered_df.empty:
        return px.bar(title="No data"), px.bar(title="No data"), "{}"

    # Group Data by Month
    filtered_df["month"] = filtered_df["date"].dt.strftime("%Y-%m")

    monthly_data = (
        filtered_df.groupby("month", as_index=False)["difference"]
        .sum()
        .reset_index(drop=True)
    )
    # print(monthly_data)
    monthly_data.columns = ["Monat", "Gesamtstunden"]
    
    # Monthly Figure
    monthly_fig = px.bar(
        monthly_data,
        x="Monat",
        y="Gesamtstunden",
        title="Betriebsstunden pro Monat",
        text=monthly_data["Gesamtstunden"].astype(int),
    )
    monthly_fig.update_xaxes(type="category")
    monthly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Monat: %{x} <br>Gesamtstunden: %{y:.0f} Stunden",
    )
    # monthly_fig.update_yaxes(range=[0, monthly_fig["Gesamtstunden"].max() + 5])
    
    # filtered_df["start_time"] = pd.to_datetime(start_date, utc=True)filtered_df["start_time"].dt.time
    # filtered_df["end_time"] = filtered_df["end_time"].dt.time
    filtered_df["date"] = filtered_df["date"].dt.date

    return monthly_fig, filtered_df.to_json()


# employee
@monthly_app.callback(
    [
        Output("employee_plot", "figure"),
        Output("json_data_employee", "data"),
    ],  # Store the filtered data
    [Input("month-picker", "date")],
)
def update_graphs_emp(selected_date):
    
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    # Extract year and month
    year, month = selected_date.year, selected_date.month
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

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
    df["work_start"] = pd.to_datetime(df["work_start"], format="%H:%M:%S")
    df["work_end"] = pd.to_datetime(df["work_end"], format="%H:%M:%S")
    
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    # Ensure filtering worked
    if filtered_df.empty:
        return px.bar(title="No data"), px.bar(title="No data"), "{}"

    # Group Data by  Month
    filtered_df["month"] = filtered_df["date"].dt.strftime("%Y-%m")

    monthly_data = (
        filtered_df.groupby(["month", "name"], as_index=False)["work_time"]
        .sum()
        .reset_index(drop=True)
    )

    monthly_data.columns = ["Monat", "Name", "Gesamtstunden"]
    # print(monthly_data)

    # Monthly Figure
    monthly_fig = go.Figure(layout=dict(template="plotly"))
    monthly_fig = px.bar(
        monthly_data,
        y="Monat",
        x="Gesamtstunden",
        color="Name",
        title="Arbeitsstunden pro Monat",
        orientation="h",
        barmode="group",
        text=round(monthly_data["Gesamtstunden"], 1),
    )
    monthly_fig.update_yaxes(type="category")
    monthly_fig.update_traces(
        texttemplate="%{text} Stunden",
        hovertemplate="Monat: %{x} <br>Gesamtstunden: %{x:.0f} Stunden",
    )
    monthly_fig.update_xaxes(range=[0, monthly_data["Gesamtstunden"].max() + 5])

    filtered_df["work_start"] = filtered_df["work_start"].dt.time
    filtered_df["work_end"] = filtered_df["work_end"].dt.time
    filtered_df["date"] = filtered_df["date"].dt.date

    return monthly_fig, filtered_df.to_json()

# work category
@monthly_app.callback(
    [
        Output("workcat_plot", "figure"),
        Output("json_data_wcat", "data"),
    ],  # Store the filtered data
    [Input("month-picker", "date")],
)
def update_graphs_wcat(selected_date):
    
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    # Extract year and month
    year, month = selected_date.year, selected_date.month
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    df = get_cleaned_wcat()

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

     
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date.date()) & (df["date"] <= end_date.date())].copy()
    # print(filtered_df)

    # Ensure filtering worked
    if filtered_df.empty:
        return px.line(title="No data"), px.line(title="No data"), "{}"
    
    plot_dat = pd.melt(filtered_df, id_vars='date', value_vars=["cleaning", "maintenance", "interruption"], 
                       var_name="Kategorie", value_name='Dauer')
    plot_dat['Kategorie'] = plot_dat['Kategorie'].map({'cleaning': "Reinigung",
                                    "maintenance": "Wartung/Reparatur", 
                                    'interruption': "Störung"})
    
    # print(plot_dat['date'].dtype)
    plot_dat['date'] = pd.to_datetime(plot_dat['date'], utc=True)
    # plot_dat['date'] = plot_dat['date'].dt.strftime("%Y-%m-%d")
    plot_dat['date'] = plot_dat['date'].dt.strftime("%d.%m.%Y")

    # Monthly Figure
    monthly_fig = go.Figure(layout=dict(template="plotly"))
    monthly_fig = px.scatter(
        plot_dat,
        y="Dauer",
        x="date",
        color="Kategorie",
        title="tägliche Aktivitäten",
        symbol="Kategorie"
    )
    monthly_fig.update_xaxes(tickformat="%Y-%m-%d")
    #monthly_fig.update_yaxes(type="category")
    #monthly_fig.update_traces(
    #    texttemplate="%{text} Stunden",
    #    hovertemplate="Monat: %{x} <br>Gesamtstunden: %{x:.0f} Stunden",
    #)
    #monthly_fig.update_xaxes(range=[0, monthly_data["Gesamtstunden"].max() + 5])

    return monthly_fig, filtered_df.to_json()


# container
@monthly_app.callback(
    [
        Output("cont_plot", "figure"),
        Output("json_data_cont", "data"),
    ],  # Store the filtered data
    [Input("month-picker", "date")],
)
def update_graphs_container(selected_date):
    
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    # Extract year and month
    year, month = selected_date.year, selected_date.month
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    df = get_cleaned_cont()

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

     
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date.date()) & (df["date"] <= end_date.date())].copy()
    # print(filtered_df)

    # Ensure filtering worked
    if filtered_df.empty:
        return px.line(title="No data"), px.line(title="No data"), "{}"
    
    plot_dat = pd.melt(filtered_df, id_vars='date', value_vars=["alu", "holz", "karton", "magnetschrott", "kanister"], 
                       var_name="Kategorie", value_name='Anzahl')
    plot_dat['Kategorie'] = plot_dat['Kategorie'].map({'alu': 'Alu Dosen (Kübel - 8,5 kg)',
                                    'holz': 'Holz (Container - 6 t)', 
                                    'karton': 'Karton (Container - 6 t)', 
                                    'magnetschrott': 'Magnetschrott (Container - 6 t)', 
                                    'kanister': 'Kanister (1 Container = 5 Ballen)'
                                    })
    
    # print(plot_dat['date'].dtype)
    plot_dat['date'] = pd.to_datetime(plot_dat['date'], utc=True)
    #plot_dat['date'] = plot_dat['date'].dt.strftime("%Y-%m-%d")
    plot_dat['date'] = plot_dat['date'].dt.strftime("%d.%m.%Y")
    # Monthly Figure
    monthly_fig = go.Figure(layout=dict(template="plotly"))
    monthly_fig = px.line(
        plot_dat,
        y="Anzahl",
        x="date",
        color="Kategorie",
        title="Container-Anzahl",
        symbol="Kategorie"
    )
    monthly_fig.update_xaxes(tickformat="%Y-%m-%d")
    #monthly_fig.update_yaxes(type="category")
    #monthly_fig.update_traces(
    #    texttemplate="%{text} Stunden",
    #    hovertemplate="Monat: %{x} <br>Gesamtstunden: %{x:.0f} Stunden",
    #)
    #monthly_fig.update_xaxes(range=[0, monthly_data["Gesamtstunden"].max() + 5])

    return monthly_fig, filtered_df.to_json()

# protocollist 
@monthly_app.callback(
    
    Output("json_data_prot", "data"),
    Input("month-picker", "date"),
)
def update_protocollist(selected_date):
    
    selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
    # Extract year and month
    year, month = selected_date.year, selected_date.month
    
    start_date = datetime.date(year, month, 1)
    end_date = datetime.date(year, month + 1, 1) - datetime.timedelta(days=1)

    df = get_cleaned_prot()

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
     
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1) - pd.Timedelta(seconds=1)
    # Filter Data
    filtered_df = df[(df["date"] >= start_date.date()) & (df["date"] <= end_date.date())].copy()
    # print(filtered_df)
 
    return filtered_df.to_json(orient="records")

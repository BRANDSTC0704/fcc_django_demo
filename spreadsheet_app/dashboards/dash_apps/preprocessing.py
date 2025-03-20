import pandas as pd
from data_entry.models import WorkHours
import plotly.express as px

def get_cleaned_work_hours():
    """Fetch and preprocess work hours data from the database."""
    work_hours_data = WorkHours.objects.all()
    
    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        work_hours_data.values("created_at", "start_time", "end_time")
    )

    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)

    df["difference"] = [wh.difference for wh in work_hours_data]
    df["difference"] = df["difference"].apply(lambda x: convert_time_difference(x))
    df["difference"] = df["difference"].astype(float)  # Convert to numeric

    return df

def convert_time_difference(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        return hours + minutes / 60  # Convert to float
    except ValueError:
        return 0.0  # Default in case of an error

def update_graphs(start_date, end_date, df, week_true_or_month_false=True):
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

    if week_true_or_month_false: 
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

    else: 
        monthly_data = (
            filtered_df.groupby("month", as_index=False)["difference"]
            .sum()
            .reset_index(drop=True)
        )
        monthly_data.columns = ["month", "Total Hours"]

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

        return monthly_fig, filtered_df.to_json()

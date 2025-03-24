import pandas as pd
from data_entry.models import (
    WorkHours,
    Employee,
    WorkCategory, 
    ContainerCount, 
    Protocollist
)


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


def get_cleaned_employee():
    employee_data = Employee.objects.all()

    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        employee_data.values(
            "created_at",
            "first_name",
            "surname",
            "attribut",
            "work_start",
            "work_end",
            "break_time",
        )
    )

    # print(df.dtypes)
    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    df["work_end"] = pd.to_datetime(df["work_end"], utc=True, format="%H:%M:%S")
    df["work_start"] = pd.to_datetime(df["work_start"], utc=True, format="%H:%M:%S")
    df["work_time"] = (df["work_end"] - df["work_start"]) / pd.Timedelta(hours=1)
    df["name"] = df["surname"] + " " + df["first_name"]

    return df


def date_allowed():
    df1 = get_cleaned_work_hours()
    df2 = get_cleaned_employee()

    mindates = [df1["date"].min().date(), df2["date"].min().date()]
    maxdates = [df1["date"].max().date(), df2["date"].max().date()]

    return (min(mindates), max(maxdates))

def get_cleaned_wcat():
    """Fetch and preprocess work hours data from the database."""
    work_cat_data = WorkCategory.objects.all()

    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        work_cat_data.values("created_at", "cleaning", "maintenance", "interruption")
    )

    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    df["date"] = df["date"].dt.date

    erg = df.groupby('date')[["cleaning", "maintenance", "interruption"]].sum().reset_index()

    return erg

def get_cleaned_cont():
    """Fetch and preprocess work hours data from the database."""
    work_cat_data = ContainerCount.objects.all()

    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        work_cat_data.values("created_at", "alu", "holz", "karton", "magnetschrott", "kanister")
    )
    
    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    df["date"] = df["date"].dt.date

    erg = df.groupby('date')[["alu", "holz", "karton", "magnetschrott", "kanister"]].sum().reset_index()

    return erg

def get_cleaned_prot():
    """Fetch and preprocess work hours data from the database."""
    prot_dat = Protocollist.objects.all()

    # Convert to DataFrame
    df = pd.DataFrame.from_records(
        prot_dat.values("created_at", 'protocollist')
    )
    
    # Convert 'date' to datetime
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    df["date"] = df["date"].dt.date

    return df

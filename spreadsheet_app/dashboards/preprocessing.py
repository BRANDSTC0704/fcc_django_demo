import pandas as pd
from data_entry.models import WorkHours

def get_cleaned_work_hours():
    """Fetch and preprocess work hours data from the database."""
    work_hours_data = WorkHours.objects.all()
    
    df = pd.DataFrame.from_records(
        work_hours_data.values("created_at", "start_time", "end_time", "difference")
    )
    df["date"] = pd.to_datetime(df["created_at"], utc=True)
    df["difference"] = df["difference"].astype(float)  # Convert to numeric

    return df

## data preprocessing for kuebel-dashboard 

import pandas as pd

from kuebelwaschen_him2.models import (
    KuebelArt,
    KuebelSession,
    KuebelEintrag
)


def convert_qs_to_df(qs): 
    # Convert Queryset to DataFrame
    df = pd.DataFrame.from_records(
         qs.values()
         )
    return df 


def get_kuebel_data(): 
    """Pulls ALL! the Kuebel-Data from database and combines it into one common dataframe. 
    
    Returns: 
        pd.DataFrame(): Contains data from type, session and detailed entries. 
        columns: 
            ['kuebel_eintrag_id', 'log_id', 'kuebel_art_id', 'sonstiges_h',
            'reinigung_h', 'waschen_h', 'waschen_count', 'instandh_h',
            'instandh_count', 'zerlegen_h', 'zerlegen_count', 'kuebel_name',
            'user_name_manuell', 'user_id', 'comments', 'created_at'],
        dtypes:
            kuebel_eintrag_id - int64, log_id -int64, 
            kuebel_art_id - int64, sonstiges_h - float64,
            reinigung_h - float64, waschen_h - float64,
            waschen_count - int64, instandh_h - float64,
            instandh_count - int64, zerlegen_h - float64,
            zerlegen_count - int64, kuebel_name - object,
            user_name_manuell - object, user_id - int64,
            comments - object, created_at - datetime64[ns, UTC]
    """

    kuebel_art_qs = KuebelArt.objects.all()
    kuebel_session_qs = KuebelSession.objects.all()
    kuebel_eintrag_qs = KuebelEintrag.objects.all()

    kuebel_art_df = convert_qs_to_df(kuebel_art_qs)
    kuebel_session_df = convert_qs_to_df(kuebel_session_qs)
    kuebel_eintrag_df = convert_qs_to_df(kuebel_eintrag_qs)

    kuebel_art_df.rename(columns={'id': 'kuebel_art_id'}, inplace=True)
    kuebel_session_df.rename(columns={'id': 'log_id'}, inplace=True)
    kuebel_eintrag_df.rename(columns={'id': 'kuebel_eintrag_id'}, inplace=True)

    # print(kuebel_art_df.head(2))
    # print(kuebel_session_df.head(2))
    # print(kuebel_eintrag_df.head(2))

    step1 = pd.merge(kuebel_eintrag_df, kuebel_art_df, on='kuebel_art_id', how='left')
    step2 = pd.merge(step1, kuebel_session_df, on='log_id', how='left')
    assert step2.shape[0] == kuebel_eintrag_df.shape[0], 'Beim Kuebel-Merging hat etwas nicht geklappt!'
    # print(step2)
    # print(step2.columns)
    # print(step2.dtypes)
    return(step2)


# def get_cleaned_work_hours():
#     """Fetch and preprocess work hours data from the database."""
#     work_hours_data = WorkHours.objects.all()

#     # Convert to DataFrame
#     df = pd.DataFrame.from_records(
#         work_hours_data.values("created_at", "start_time", "end_time")
#     )

#     # Convert 'date' to datetime
#     df["date"] = pd.to_datetime(df["created_at"], utc=True)

#     df["difference"] = [wh.difference for wh in work_hours_data]
#     df["difference"] = df["difference"].apply(lambda x: convert_time_difference(x))
#     df["difference"] = df["difference"].astype(float)  # Convert to numeric

#     return df


# def convert_time_difference(time_str):
#     try:
#         hours, minutes = map(int, time_str.split(":"))
#         return hours + minutes / 60  # Convert to float
#     except ValueError:
#         return 0.0  # Default in case of an error


# def get_cleaned_employee():
#     employee_data = Employee.objects.all()

#     # Convert to DataFrame
#     df = pd.DataFrame.from_records(
#         employee_data.values(
#             "created_at",
#             "first_name",
#             "surname",
#             "attribut",
#             "work_start",
#             "work_end",
#             "break_time",
#         )
#     )

#     # print(df.dtypes)
#     # Convert 'date' to datetime
#     df["date"] = pd.to_datetime(df["created_at"], utc=True)
#     df["work_end"] = pd.to_datetime(df["work_end"], utc=True, format="%H:%M:%S")
#     df["work_start"] = pd.to_datetime(df["work_start"], utc=True, format="%H:%M:%S")
#     df["work_time"] = (df["work_end"] - df["work_start"]) / pd.Timedelta(hours=1)
#     df["name"] = df["surname"] + " " + df["first_name"]

#     return df


# def date_allowed():
#     df1 = get_cleaned_work_hours()
#     df2 = get_cleaned_employee()

#     mindates = [df1["date"].min().date(), df2["date"].min().date()]
#     maxdates = [df1["date"].max().date(), df2["date"].max().date()]

#     return (min(mindates), max(maxdates))

# def get_cleaned_wcat():
#     """Fetch and preprocess work hours data from the database."""
#     work_cat_data = WorkCategory.objects.all()

#     # Convert to DataFrame
#     df = pd.DataFrame.from_records(
#         work_cat_data.values("created_at", "cleaning", "maintenance", "interruption")
#     )

#     # Convert 'date' to datetime
#     df["date"] = pd.to_datetime(df["created_at"], utc=True)
#     df["date"] = df["date"].dt.date

#     erg = df.groupby('date')[["cleaning", "maintenance", "interruption"]].sum().reset_index()

#     return erg

# def get_cleaned_cont():
#     """Fetch and preprocess work hours data from the database."""
#     work_cat_data = ContainerCount.objects.all()

#     # Convert to DataFrame
#     df = pd.DataFrame.from_records(
#         work_cat_data.values("created_at", "alu", "holz", "karton", "magnetschrott", "kanister")
#     )
    
#     # Convert 'date' to datetime
#     df["date"] = pd.to_datetime(df["created_at"], utc=True)
#     df["date"] = df["date"].dt.date

#     erg = df.groupby('date')[["alu", "holz", "karton", "magnetschrott", "kanister"]].sum().reset_index()

#     return erg

# def get_cleaned_prot():
#     """Fetch and preprocess work hours data from the database."""
#     prot_dat = Protocollist.objects.all()

#     # Convert to DataFrame
#     df = pd.DataFrame.from_records(
#         prot_dat.values("created_at", 'protocollist')
#     )
    
#     # Convert 'date' to datetime
#     df["date"] = pd.to_datetime(df["created_at"], utc=True)
#     df["date"] = df["date"].dt.date

#     return df

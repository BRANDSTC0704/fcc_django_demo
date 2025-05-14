## data preprocessing for kuebel-dashboard

import pandas as pd
import matplotlib

matplotlib.use("Agg")  # Use a non-GUI backend suitable for scripts and servers
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io
import base64
from django.db.models import F

from him2_referenzdaten.models import KuebelArt, Mitarbeiter, Betankung, Fahrzeug

from him2_kuebelwaschplatz.models import (
    KuebelSession,
    KuebelEintrag,
)


def convert_qs_to_df(qs):
    """Conversion from queryset to dataframe.

    Args:
        qs (Query set): A generic django query set.

    Returns:
        pd.DataFrame: The query set is transformed into a dataframe.
    """
    # Convert Queryset to DataFrame
    df = pd.DataFrame.from_records(qs.values())
    return df


def get_kuebel_data():
    """Pulls ALL! the Kuebel-Data from database and combines it into one common dataframe.

    Returns:
        pd.DataFrame(): Contains data from type, session and detailed entries.
        columns:
            ['kuebel_eintrag_id', 'log_id', 'kuebel_art_id', 'sonstiges_h',
            'reinigung_h', 'waschen_h', 'waschen_count', 'instandh_h',
            'instandh_count', 'zerlegen_h', 'zerlegen_count', 'name',
            'mitarbeiter', 'user_id', 'comments', 'created_at'],
        dtypes:
            kuebel_eintrag_id - int64, log_id -int64,
            kuebel_art_id - int64, sonstiges_h - float64,
            reinigung_h - float64, waschen_h - float64,
            waschen_count - int64, instandh_h - float64,
            instandh_count - int64, zerlegen_h - float64,
            zerlegen_count - int64, name - object,
            mitarbeiter - object, user_id - int64,
            comments - object, created_at - datetime64[ns, UTC]
    """

    kuebel_art_qs = KuebelArt.objects.all()
    kuebel_session_qs = (
        KuebelSession.objects.all()
        .select_related("user")
        .annotate(username=F("user__username"))
    )
    kuebel_eintrag_qs = KuebelEintrag.objects.all()
    # addendum: Mitarbeiter und Tankfahrzeug
    mitarbeiter_qs = Mitarbeiter.objects.all()
    tank_qs = Betankung.objects.all()
    fahrzeug_qs = Fahrzeug.objects.all()

    def convert_ids_to_int(df, colname_list=["id"]):
        """Convert columns with name id to int-datatype.

        Args:
            df (pd.DataFrame): dataframe containing column with name id.
            colname_list (list): list of columns to convert

        Returns:
            pd.DataFrame: Dataframe with converted id-column.
        """

        for i in colname_list:
            if i in df.columns:
                df[i] = df[i].fillna(0)  # fix missing values
                df[i] = df[i].astype(int)
        return df

    kuebel_art_df = convert_ids_to_int(convert_qs_to_df(kuebel_art_qs))
    kuebel_session_df = convert_ids_to_int(
        convert_qs_to_df(kuebel_session_qs), ["id", "tank_id"]
    )
    kuebel_eintrag_df = convert_ids_to_int(convert_qs_to_df(kuebel_eintrag_qs))
    mitarbeiter_df = convert_ids_to_int(convert_qs_to_df(mitarbeiter_qs))
    tank_df = convert_ids_to_int(convert_qs_to_df(tank_qs))
    fahrzeug_df = convert_ids_to_int(convert_qs_to_df(fahrzeug_qs))

    # print('kuebel_art_df - ', kuebel_art_df.columns)
    # print('kuebel_session_df - ', kuebel_session_df.columns)
    # print('kuebel_eintrag_df - ', kuebel_eintrag_df.columns)
    # print('mitarbeiter_df - ', mitarbeiter_df.columns)
    # print('tank_df - ', tank_df.columns)
    # print('fahrzeug_df - ', fahrzeug_df.columns)

    kuebel_art_df.rename(columns={"id": "kuebel_art_id"}, inplace=True)
    kuebel_session_df.rename(columns={"id": "log_id"}, inplace=True)
    kuebel_eintrag_df.rename(columns={"id": "kuebel_eintrag_id"}, inplace=True)
    mitarbeiter_df.rename(columns={"id": "mitarbeiter_id"}, inplace=True)
    tank_df.rename(columns={"id": "tank_id"}, inplace=True)
    fahrzeug_df.rename(columns={"id": "fahrzeug_id"}, inplace=True)

    # prep Mitarbeiter und Tank
    tank_fahrzeug_df = pd.merge(tank_df, fahrzeug_df, on="fahrzeug_id", how="left")
    tank_fahrzeug_df.rename(
        columns={"name": "fahrzeug_name", "user_id": "user_id_betankung"}, inplace=True
    )

    mitarbeiter_df["mitarbeiter"] = (
        mitarbeiter_df["first_name"] + " " + mitarbeiter_df["last_name"]
    )

    step1 = pd.merge(
        kuebel_eintrag_df,
        kuebel_art_df,
        on="kuebel_art_id",
        how="left",
        suffixes=["_kuebel_eintrag", "_kuebel_art"],
    )
    step2 = pd.merge(
        step1,
        kuebel_session_df,
        on="log_id",
        how="left",
        suffixes=["_step1", "_kuebel_session"],
    )
    step3 = pd.merge(
        step2,
        tank_fahrzeug_df,
        on="tank_id",
        how="left",
        suffixes=["_step2", "_tank_fahrzeug"],
    )
    last_step = pd.merge(
        step3,
        mitarbeiter_df,
        on="mitarbeiter_id",
        how="left",
        suffixes=["_step3", "_mitarbeiter"],
    )

    assert (
        last_step.shape[0] == kuebel_eintrag_df.shape[0]
    ), "Beim Kuebel-Merging hat etwas nicht geklappt!"

    # Berechnung Gesamtzahl Behälter
    last_step["Anzahl_gesamt"] = (
        last_step["waschen_count"]
        + last_step["instandh_count"]
        + last_step["zerlegen_count"]
    )
    # Berechnung Gesamtstunden
    last_step["Stunden_gesamt"] = (
        last_step["sonstiges_h"]
        + last_step["reinigung_h"]
        + last_step["waschen_h"]
        + last_step["instandh_h"]
        + last_step["zerlegen_h"]
    )

    return last_step


def plot_tages_werte_aktivitaet_anzahl(df):
    """Time Series Plot-Function for aggregated data view.
       Data is summed up per day, including activites and counts.

    Args:
        df (pd.DataFrame): DataFrame with raw data prior to aggregation.

    Returns:
        image_png: A static image with a plot.
    """
    if not df.empty:
        df.loc[:, "created_at"] = pd.to_datetime(df["created_at"])

        # Group by date and sum relevant activity columns
        grouped = df.groupby(df["created_at"].dt.date)[
            ["Anzahl_gesamt", "Stunden_gesamt"]
        ].sum()

        # Define a clean, color-friendly style
        plt.style.use("seaborn-v0_8-whitegrid")  # Light, readable theme

        # Create the figure and axis (single axis for both)
        fig, ax1 = plt.subplots(figsize=(8, 5))

        # --- Plot Activity Hours (Stunden_gesamt) on the left y-axis ---
        color_hours = "#1f77b4"  # Blue for hours
        ax1.plot(
            grouped.index,
            grouped["Stunden_gesamt"],
            label="Stunden [h]",
            color=color_hours,
        )
        ax1.set_xlabel("Datum [dd.mm.yy]")
        ax1.set_ylabel("Arbeitsstunden [h]", color=color_hours)
        ax1.tick_params(axis="y", labelcolor=color_hours)

        # German date formatting on x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%y"))

        # --- Create a second y-axis for Counts (Anzahl_gesamt) ---
        ax2 = ax1.twinx()
        color_counts = "#d62728"  # Red for counts
        ax2.plot(
            grouped.index,
            grouped["Anzahl_gesamt"],
            label="Anzahl [#]",
            color=color_counts,
        )
        ax2.set_ylabel("Anzahl Behälter [#]", color=color_counts)
        ax2.tick_params(axis="y", labelcolor=color_counts)

        # Set plot title and rotate x-axis labels
        ax1.set_title("Summe Aktivitäten pro Tag [h] & Behälteranzahl [#]", fontsize=14)
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

        # --- Add Legends ---
        ax1.legend(loc="upper left", bbox_to_anchor=(1.05, 1), borderaxespad=0.0)
        ax2.legend(loc="upper left", bbox_to_anchor=(1.05, 0.95), borderaxespad=0.0)

        # Change the style of the grid lines for ax2 to dashed
        for line in ax2.get_ygridlines():
            line.set_linestyle("--")  # Change to dashed lines

        # Adjust layout to avoid overlapping content
        plt.tight_layout()

        # Save plot to base64 string
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        image_png = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        return image_png


def plot_tages_werte_nach_aktivitaet(df):
    """Time Series Plot-Function for aggregated data view.
       Data is summed up per day, including detailed activites and counts.

    Args:
        df (pd.DataFrame): DataFrame with raw data prior to aggregation.

    Returns:
        image_png: A static image containing two figures.
    """

    if not df.empty:
        df.loc[:, "created_at"] = pd.to_datetime(df["created_at"])

        # Group by date and sum all relevant activity columns
        grouped = df.groupby(df["created_at"].dt.date)[
            ["waschen_h", "reinigung_h", "sonstiges_h", "instandh_h", "zerlegen_h"]
        ].sum()

        # Group by date and count occurrences for each count variable
        counts = df.groupby(df["created_at"].dt.date)[
            ["waschen_count", "instandh_count", "zerlegen_count"]
        ].sum()

        # Define a clean, color-friendly style
        plt.style.use("seaborn-v0_8-whitegrid")  # Light, readable theme

        # Create a figure with 2 subplots in one row (1x2 grid)
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

        # --- First Plot: Activity Hours ---
        color_map = {
            "waschen_h": "#1f77b4",
            "reinigung_h": "#ff7f0e",
            "sonstiges_h": "#2ca02c",
            "instandh_h": "#d62728",
            "zerlegen_h": "#9467bd",
        }

        for column in grouped.columns:
            ax1.plot(
                grouped.index,
                grouped[column],
                label=column.replace("_h", "").capitalize(),
                color=color_map.get(column),
            )

        # German date formatting on x-axis
        ax1.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%y"))
        ax1.set_title("Aktivitäten Tagessummen", fontsize=14)
        ax1.set_xlabel("Datum [dd.mm.yy]")
        ax1.set_ylabel("Stunden [h]")
        ax1.legend(
            title="Aktivität",
            loc="upper left",
            bbox_to_anchor=(1.05, 0.5),
            borderaxespad=0.0,
        )

        # --- Second Plot: Counts (for different activity counts) ---
        color_map_counts = {
            "waschen_count": "#1f77b4",
            "instandh_count": "#d62728",
            "zerlegen_count": "#9467bd",
        }

        for column in counts.columns:
            ax2.plot(
                counts.index,
                counts[column],
                label=column.replace("_count", "").capitalize(),
                color=color_map_counts.get(column),
            )
        ax2.xaxis.set_major_formatter(mdates.DateFormatter("%d.%m.%y"))
        ax2.set_title("Anzahl Behälter Tagessummen", fontsize=14)
        ax2.set_xlabel("Datum [dd.mm.yy]")
        ax2.set_ylabel("Anzahl [#]")
        ax2.legend(
            title="Ereignis",
            loc="upper left",
            bbox_to_anchor=(1.05, 0.5),
            borderaxespad=0.0,
        )

        # Rotate x-axis labels for both plots
        plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
        plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

        # Adjust layout to avoid overlapping content
        plt.tight_layout()

        # Save plot to base64 string
        buf = io.BytesIO()
        fig.savefig(buf, format="png")
        buf.seek(0)
        image_png = base64.b64encode(buf.getvalue()).decode("utf-8")
        buf.close()
        return image_png


def generate_excel_table(df):
    """Reorders DataFrame and saves it to IO-Buffer for download.

    Args:
        df (pd.Dataframe): Super-Dataset from Kübelwaschen.

    Returns:
        BytesIO: in-memory Byte Buffer of excel-file (formatted as excel-table).
    """
    if not df.empty:
        # Create an in-memory bytes buffer
        output = io.BytesIO()

        # print(df.columns)

        spalten = [
            "username",
            "mitarbeiter",
            "created_at",
            "daten_eingabe_von",
            "comments",
            "Anzahl_gesamt",
            "Stunden_gesamt",
            "sonstiges_h",
            "reinigung_h",
            "waschen_h",
            "instandh_h",
            "zerlegen_h",
            "name",
            "waschen_count",
            "instandh_count",
            "zerlegen_count",
            "fahrzeug_name",
            "bereich",
            "kostenstelle",
            "user_id",
            "log_id",
            "kuebel_eintrag_id",
            "kuebel_art_id",
            "mitarbeiter_id",
            "tank_id",
            "user_id_betankung",
        ]

        df_select = df[spalten]

        # Use Excel writer with buffer
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df_select.to_excel(
                writer, sheet_name="Rohdaten", startrow=1, header=False, index=False
            )
            # workbook = writer.book
            worksheet = writer.sheets["Rohdaten"]

            (max_row, max_col) = df_select.shape
            column_settings = [{"header": col} for col in df_select[spalten].columns]

            worksheet.add_table(
                0, 0, max_row, max_col - 1, {"columns": column_settings}
            )
            worksheet.set_column(0, max_col - 1, 12)
            worksheet.set_column(2, 2, 19)  # Date width

        # Rewind the buffer
        output.seek(0)
        return output

## data preprocessing for kuebel-dashboard 

import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Use a non-GUI backend suitable for scripts and servers
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import io, base64


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
    
    # Berechnung Gesamtzahl Behälter 
    step2['Anzahl_gesamt'] = step2['waschen_count'] + step2['instandh_count'] + step2['zerlegen_count']
    # Berechnung Gesamtstunden
    step2['Stunden_gesamt'] = step2['sonstiges_h'] + step2['reinigung_h'] + step2['waschen_h'] + step2['instandh_h'] + step2['zerlegen_h']
    
    return(step2)

def plot_tages_werte_aktivitaet_anzahl(df):
    df['created_at'] = pd.to_datetime(df['created_at'])

    # Group by date and sum relevant activity columns
    grouped = df.groupby(df['created_at'].dt.date)[
        ['Anzahl_gesamt', 'Stunden_gesamt']
    ].sum()

    # Define a clean, color-friendly style
    plt.style.use('seaborn-v0_8-whitegrid')  # Light, readable theme

    # Create the figure and axis (single axis for both)
    fig, ax1 = plt.subplots(figsize=(8, 5))

    # --- Plot Activity Hours (Stunden_gesamt) on the left y-axis ---
    color_hours = '#1f77b4'  # Blue for hours
    ax1.plot(grouped.index, grouped['Stunden_gesamt'], label='Stunden [h]', color=color_hours)
    ax1.set_xlabel("Datum [dd.mm.yy]")
    ax1.set_ylabel("Arbeitsstunden [h]", color=color_hours)
    ax1.tick_params(axis='y', labelcolor=color_hours)

    # German date formatting on x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    
    # --- Create a second y-axis for Counts (Anzahl_gesamt) ---
    ax2 = ax1.twinx()
    color_counts = '#d62728'  # Red for counts
    ax2.plot(grouped.index, grouped['Anzahl_gesamt'], label='Anzahl [#]', color=color_counts)
    ax2.set_ylabel("Anzahl Behälter [#]", color=color_counts)
    ax2.tick_params(axis='y', labelcolor=color_counts)

    # Set plot title and rotate x-axis labels
    ax1.set_title("Summe Aktivitäten pro Tag [h] & Behälteranzahl [#]", fontsize=14)
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)

    # --- Add Legends ---
    ax1.legend(loc='upper left', bbox_to_anchor=(1.05, 1), borderaxespad=0.)
    ax2.legend(loc='upper left', bbox_to_anchor=(1.05, 0.95), borderaxespad=0.)

    # Change the style of the grid lines for ax2 to dashed
    for line in ax2.get_ygridlines():
        line.set_linestyle('--')  # Change to dashed lines
        
    # Adjust layout to avoid overlapping content
    plt.tight_layout()

    # Save plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_png = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_png


def plot_tages_werte_nach_aktivitaet(df):

    df['created_at'] = pd.to_datetime(df['created_at'])

    # Group by date and sum all relevant activity columns
    grouped = df.groupby(df['created_at'].dt.date)[
        ['waschen_h', 'reinigung_h', 'sonstiges_h', 'instandh_h', 'zerlegen_h']
    ].sum()

    # Group by date and count occurrences for each count variable
    counts = df.groupby(df['created_at'].dt.date)[
        ['waschen_count', 'instandh_count', 'zerlegen_count']
    ].sum()

    # Define a clean, color-friendly style
    plt.style.use('seaborn-v0_8-whitegrid')  # Light, readable theme

    # Create a figure with 2 subplots in one row (1x2 grid)
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    # --- First Plot: Activity Hours ---
    color_map = {
        'waschen_h': '#1f77b4',
        'reinigung_h': '#ff7f0e',
        'sonstiges_h': '#2ca02c',
        'instandh_h': '#d62728',
        'zerlegen_h': '#9467bd'
    }

    for column in grouped.columns:
        ax1.plot(grouped.index, grouped[column], label=column.replace('_h', '').capitalize(), color=color_map.get(column))

    # German date formatting on x-axis
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    ax1.set_title("Aktivitäten Tagessummen", fontsize=14)
    ax1.set_xlabel("Datum [dd.mm.yy]")
    ax1.set_ylabel("Stunden [h]")
    ax1.legend(title="Aktivität", loc='upper left', bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)

    # --- Second Plot: Counts (for different activity counts) ---
    color_map_counts = {
        'waschen_count': '#1f77b4',
        'instandh_count': '#d62728',
        'zerlegen_count': '#9467bd'
    }

    for column in counts.columns:
        ax2.plot(counts.index, counts[column], label=column.replace('_count', '').capitalize(), color=color_map_counts.get(column))
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%d.%m.%y'))
    ax2.set_title("Anzahl Behälter Tagessummen", fontsize=14)
    ax2.set_xlabel("Datum [dd.mm.yy]")
    ax2.set_ylabel("Anzahl [#]")
    ax2.legend(title="Ereignis", loc='upper left', bbox_to_anchor=(1.05, 0.5), borderaxespad=0.)

    # Rotate x-axis labels for both plots
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45)
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45)

    # Adjust layout to avoid overlapping content
    plt.tight_layout()

    # Save plot to base64 string
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)
    image_png = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    return image_png
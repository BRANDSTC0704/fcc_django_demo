from django.shortcuts import render
from django.http import HttpResponse
from .forms import DateRangeForm
from .utils import get_kuebel_data, plot_tages_werte_nach_aktivitaet, plot_tages_werte_aktivitaet_anzahl, generate_excel_table
import pandas as pd
from django.utils.timezone import make_aware
from datetime import datetime, time, timedelta
from pytz import timezone 
from django.contrib.auth.decorators import login_required


@login_required
def grouped_dashboard(request):
    """View for dashboards. Includes tabular calculation and plots. Date filtering is used and then functions from utils.py are applied.

    Args:
        request (_type_): Request object. 

    Returns:
        View: Containing multiple elements. 
    """
    plot_base64 = None
    filtered_df = pd.DataFrame()

    # Calculate default dates
    today = datetime.today().date()
    start_date = today.replace(day=1)
    end_date = (today.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

    # Form: use initial only if GET is empty (first load)
    if request.GET:
        form = DateRangeForm(request.GET)
        if form.is_valid():
            start = make_aware(datetime.combine(form.cleaned_data['start_date'], time.min), timezone=timezone('Europe/Vienna'))
            end = make_aware(datetime.combine(form.cleaned_data['end_date'], time.max), timezone=timezone('Europe/Vienna'))
        else:
            start = end = None
    else:
        form = DateRangeForm(initial={'start_date': start_date, 'end_date': end_date})
        start = make_aware(datetime.combine(start_date, time.min), timezone=timezone('Europe/Vienna'))
        end = make_aware(datetime.combine(end_date, time.max), timezone=timezone('Europe/Vienna'))

    # Data filtering
    if start and end:
        df = get_kuebel_data()
        df['created_at'] = pd.to_datetime(df['created_at'])
        mask = (df['created_at'] >= start) & (df['created_at'] <= end)
        filtered_df = df.loc[mask]

         # Summarize the activity and counts
        activity_columns = ['sonstiges_h', 'reinigung_h', 'waschen_h', 'instandh_h', 'zerlegen_h', 'Stunden_gesamt']
        count_columns = ['waschen_count', 'instandh_count', 'zerlegen_count', 'Anzahl_gesamt']

        activity_sums = filtered_df[activity_columns].sum()
        count_sums = filtered_df[count_columns].sum()

        if 'download' in request.GET:
            filtered_df['created_at'] = filtered_df['created_at'].dt.tz_localize(None)
            output = generate_excel_table(filtered_df)
            response = HttpResponse(
                output,
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename="Kuebeleingaben_Details.xlsx"'
            return response


        plot1_base64 = plot_tages_werte_aktivitaet_anzahl(filtered_df)
        plot2_base64 = plot_tages_werte_nach_aktivitaet(filtered_df)


    return render(request, 'him2_dboard_kuebelwaschplatz/grouped_dashboard.html', {
        'form': form, # date widget 
        'plot1': plot1_base64, # totals time series 
        'plot2': plot2_base64, # time series per category 
        'activity_sums': activity_sums, # 
        'count_sums': count_sums,
    })

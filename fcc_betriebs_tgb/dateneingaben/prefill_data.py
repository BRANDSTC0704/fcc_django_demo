from .models import KuebelArt

def prefill_kuebel_art():
    defaults = [
        '120 L',
        '120 L Restmüll (sw)',
        '120 L Bio (braun)',
        '120 L Papier (rot)',
        '240 L',
        '240 L Restmüll (sw)',
        '240 L Bio (braun)',
        '240 L Papier (rot)',
        '660 L',
        '660 L Restmüll (sw)',
        '660 L Bio (braun)',
        '660 L Papier (rot)',
        '770 L',
        '1100 L',
        '1100 L Restmüll (sw)',
        '1100 L Bio (braun)',
        '1100 L Papier (rot)',
        'Fässer 60 L', 'Fässer 200 L', 'Tankpaletten', 
        'Altöltank', 'ASP', 'ASF'
    ]
    for name in defaults:
        obj, created = KuebelArt.objects.get_or_create(name=name)
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")

def run_all_prefills():
    print("Running data prefill scripts...")
    prefill_kuebel_art()
    print("Done.")


## EXECUTION WITH MANAGE.PY: 
# to be ran with django shell: 
# python manage.py shell then: 
# from dateneingaben.prefill_data import run_all_prefills
# run_all_prefills()
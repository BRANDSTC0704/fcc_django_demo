from him2_referenzdaten.models import (
    KuebelArt,
    PresseBallenTyp,
    Schicht,
    Fahrzeug,
    Mitarbeiter,
)
from him2_pressenlinie.models import AbhProdTyp, ZeitAktivitaetTyp

# Script to prepopulate reference data.
# updated 14.05 for new (unified) field names.


def prefill_ballen_art_pl():

    defaults = [
        ("Karton", 0.7),
        ("Papier", 0.8),
        ("Folien", 0.4),
        ("Folien 90/10", 0.4),
        ("Dosen", 0.35),
        ("Kübel Eimer", 0.4),
        ("Kanister", 0.35),
        ("Tetra", 0.5),
        ("Big Bags", 0.4),
        ("Papiersäcke", 0.95),
        ("Henkel Flaschen", 0.3),
        ("Stoßstangen", 0.4),
        ("GS", 0.35),
        ("Bildschirmgehäuse", 0.4),
        ("PVC-Streifen", 0.6),
        ("Pet Flaschen", 0.35),
        ("Henkel Folien", 0.4),
        ("Kleiderbügel", 0.45),
        ("PP-Bänder", 0.45),
        ("Siebüberlauf für WN", 0.8),
        ("Plastikkisten", 0.35),
        ("Plastikabfälle", 0.48),
        ("Baunetz", 0.4),
        ("Thermisch", 0.4),
        ("Nöm Kübel", 0.5),
    ]

    for name in defaults:
        obj, created = PresseBallenTyp.objects.get_or_create(
            name=name[0], gewicht=name[1]
        )
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")


def prefill_kuebel_art():
    defaults = [
        "120 L",
        # '120 L Restmüll (sw)',
        # '120 L Bio (braun)',
        # '120 L Papier (rot)',
        "240 L",
        # '240 L Restmüll (sw)',
        # '240 L Bio (braun)',
        # '240 L Papier (rot)',
        "660 L",
        # '660 L Restmüll (sw)',
        # '660 L Bio (braun)',
        # '660 L Papier (rot)',
        "770 L",
        "1100 L",
        # '1100 L Restmüll (sw)',
        # '1100 L Bio (braun)',
        # '1100 L Papier (rot)',
        "Fässer 60 L",
        "Fässer 200 L",
        "Tankpaletten",
        "Altöltank",
        "ASP",
        "ASF",
    ]
    for name in defaults:
        obj, created = KuebelArt.objects.get_or_create(name=name)
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")


def prefill_ballenpresse_abh_prod():
    defaults = ["Abholung", "Produktion"]
    for name in defaults:
        obj, created = AbhProdTyp.objects.get_or_create(name=name)
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")


def prefill_ballenpresse_schicht():
    defaults = [
        "Schicht 1",
        "Schicht 2",
    ]
    for name in defaults:
        obj, created = Schicht.objects.get_or_create(name=name)
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")


def prefill_ballenpresse_zeit_aktivitaeten():

    defaults = [
        "Arbeitsstunden",
        "Ballenpresse Laufzeit",
        "Störungszeiten",
        "Wartungszeit",
        "Reinigungszeit",
    ]
    for name in defaults:
        obj, created = ZeitAktivitaetTyp.objects.get_or_create(name=name)
        if created:
            print(f"Created: {name}")
        else:
            print(f"Exists: {name}")


def prefill_mitarbeiter():
    # first_name = models.CharField(max_length=40)
    # last_name = models.CharField(max_length=40)
    # funktion = models.CharField(max_length=40)
    # intern_extern = models.CharField(max_length=20)

    defaults = [
        ("Erich", "Reitprecht", "Prozessverantwortlicher", "intern"),
        ("", "Bachmayer", "", "extern"),
        ("", "Schwingenschrot", "", "extern"),
        ("Leopold", "Baum", "", "intern"),
        ("", "Sailer", "", "extern"),
        ("", "Weiss", "", "extern"),
        ("", "Hasani", "", "extern"),
        ("", "Saric", "", "extern"),
        ("", "Block", "", "extern"),
        ("Wolfgang", "Hahn", "", "intern"),
    ]

    for entry in defaults:
        obj, created = Mitarbeiter.objects.get_or_create(
            first_name=entry[0],
            last_name=entry[1],
            funktion=entry[2],
            intern_extern=[3],
        )
        if created:
            print(f"Created: {entry}")
        else:
            print(f"Exists: {entry}")


def prefill_fahrzeug():
    # name = models.CharField(max_length=30, unique=True)
    # bereich = models.CharField(max_length=30, unique=True)
    # kostenstelle = models.CharField(max_length=30, unique=True)

    defaults = [
        ("Linde 1 (Bj 2018)", "Sondermüll", "A0161976"),
        ("Linde 2 (Obi)", "Umladehalle/Freigelände", "A0161975"),
        ("Linde 3 (Bj 2019)", "Sondermüll", "A0161979"),
        ("Linde 4", "Umladehalle/Freigelände", "A0161612"),
        ("Linde 5", "Presse", "A0161970"),
        ("Radlader 924 G", "Umladehalle/Freigelände", "A0161969"),
        ("Radlader 908M", "Presse", "A0161610"),
        ("Bagger M322C", "Umladehalle/Freigelände", "A0161971"),
        ("Radlader 928M", "Umladehalle/Freigelände", "A0161946"),
    ]

    for entry in defaults:
        obj, created = Fahrzeug.objects.get_or_create(
            name=entry[0], bereich=entry[1], kostenstelle=entry[2]
        )
        if created:
            print(f"Created: {entry}")
        else:
            print(f"Exists: {entry}")


def run_all_prefills():
    print("Running data prefill scripts...")
    prefill_kuebel_art()
    prefill_ballen_art_pl()
    prefill_ballenpresse_abh_prod()
    prefill_ballenpresse_schicht()
    prefill_ballenpresse_zeit_aktivitaeten()
    prefill_mitarbeiter()
    prefill_fahrzeug()
    print("Done.")


## EXECUTION WITH MANAGE.PY:
# to be ran with django shell:
# python manage.py shell then:
# from prefill_data import run_all_prefills
# run_all_prefills()

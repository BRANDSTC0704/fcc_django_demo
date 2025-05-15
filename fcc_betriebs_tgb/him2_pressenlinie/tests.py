from datetime import timedelta

from django.test import TestCase
from django.contrib.auth.models import User
from django.db.utils import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.urls import reverse

# Create your tests here.
from him2_referenzdaten.models import (
    PresseBallenTyp,
    Schicht,
    Fahrzeug,
    Mitarbeiter,
    Betankung,
)
from .models import (
    ZeitAktivitaetTyp,
    AbhProdTyp,
    StundenEingabeSession,
    SchichtEingabeMitarbeiter,
    StundenEingabeDetails,
    Aktivitaet,
)
from .forms import PresseZeitSessionForm, PresseStundenEingabeForm, PresseAktivitaetForm


# Models
class PresseBallenTypModelTest(TestCase):
    """Tests for creating Presseballentypes.
    Fields: # name str, gewicht: float
    Args:
        TestCase (django.test.Testcase): Testcase parent class.
    """

    def test_create_presseballen(self):
        art = PresseBallenTyp.objects.create(name="neuer Ballen", gewicht=0)
        self.assertEqual(art.name, "neuer Ballen")

    def test_unique_presseballen_name(self):
        PresseBallenTyp.objects.create(name="Spezialballen", gewicht=0)
        with self.assertRaises(Exception):
            PresseBallenTyp.objects.create(name="Spezialballen", gewicht=0)

    def test_create_presseballen_gewicht(self):
        PresseBallenTyp.objects.create(name="gewichtstest_0", gewicht=0)
        PresseBallenTyp.objects.create(name="gewichtstest_100.5", gewicht=100.5)

        # must not be negative
        obj = PresseBallenTyp(name="Spezialballen", gewicht=-10)
        with self.assertRaises(ValidationError):
            obj.full_clean()  # This triggers validators
            obj.save()


class SchichtTest(TestCase):
    """Testcases for creating Schichts.
    Fields: # name str
    Args:
        TestCase (django.test.Testcase): Testcase parent class.
    """

    def test_create_schicht(self):
        art = Schicht.objects.create(name="Schicht 31")
        self.assertEqual(art.name, "Schicht 31")

    def test_unique_schicht_name(self):
        Schicht.objects.create(name="Schicht")
        with self.assertRaises(Exception):
            Schicht.objects.create(name="Schicht")

    def test_schicht_name_length(self):
        # max_length: 20
        with self.assertRaises(Exception):
            Schicht.objects.create(name="SchichtSchichtSchichtSchichtSchicht")


class FahrzeugTest(TestCase):

    def test_create_fahrzeug(self):
        art = Fahrzeug.objects.create(
            name="Fahrzeug", bereich="abc", kostenstelle="abc"
        )
        self.assertEqual(art.name, "Fahrzeug")

    def test_unique_fahrzeug_name(self):
        Fahrzeug.objects.create(name="Fahrzeug", bereich="abc", kostenstelle="abc1")
        with self.assertRaises(Exception):
            Schicht.objects.create(name="Fahrzeug", bereich="abc", kostenstelle="abc2")

    def test_unique_fahrzeug_kostenstelle(self):
        Fahrzeug.objects.create(name="Schicht", bereich="abc", kostenstelle="abc")
        with self.assertRaises(Exception):
            Schicht.objects.create(name="Schicht2", bereich="abc", kostenstelle="abc")


# class KuebelSessionModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="testuser")
#         self.session = KuebelSession.objects.create(
#             user=self.user, mitarbeiter="Responsible User"
#         )

#     def test_create_kuebel_session(self):
#         session = KuebelSession.objects.create(
#             user=self.user, mitarbeiter="Max Mustermann", comments="Initialer Testlauf"
#         )
#         self.assertEqual(session.user.username, "testuser")
#         self.assertEqual(session.mitarbeiter, "Max Mustermann")
#         self.assertEqual(session.comments, "Initialer Testlauf")
#         self.assertIsNotNone(session.created_at)

#     def test_created_at_auto_set(self):
#         # Ensure that created_at is not null
#         self.assertIsNotNone(self.session.created_at)

#         # Ensure that the created_at timestamp is not too far in the past or future
#         now = timezone.now()
#         self.assertTrue(self.session.created_at <= now)


# class KuebelEintragModelTest(TestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="eintraguser")
#         self.session = KuebelSession.objects.create(
#             user=self.user, mitarbeiter="Maria Musterfrau"
#         )
#         self.art = KuebelArt.objects.create(name="Kleiner Kübel")

#     def test_create_kuebel_eintrag(self):
#         eintrag = KuebelEintrag.objects.create(
#             log=self.session,
#             kuebel_art=self.art,
#             sonstiges_h=1.5,
#             reinigung_h=2.0,
#             waschen_h=0.5,
#             waschen_count=3,
#             instandh_h=1.0,
#             instandh_count=1,
#             zerlegen_h=0.8,
#             zerlegen_count=2,
#         )
#         self.assertEqual(eintrag.log, self.session)
#         self.assertEqual(eintrag.kuebel_art, self.art)
#         self.assertEqual(eintrag.waschen_count, 3)
#         self.assertEqual(eintrag.instandh_count, 1)


# class KuebelEintragModelTransactionTest(TransactionTestCase):

#     def setUp(self):
#         self.user = User.objects.create(username="testuser")
#         self.session = KuebelSession.objects.create(
#             user=self.user, mitarbeiter="Responsible Person"
#         )

#     def test_foreign_key_constraint_invalid_kuebel_art(self):
#         # We have a valid session, but kuebel_art_id=999 does not exist
#         eintrag = KuebelEintrag(
#             log=self.session, kuebel_art_id=999, sonstiges_h=1.0  # invalid FK
#         )
#         with self.assertRaises(IntegrityError):
#             eintrag.save()

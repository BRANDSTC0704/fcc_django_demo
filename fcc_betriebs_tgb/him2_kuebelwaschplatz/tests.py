from django.test import TestCase
from django.contrib.auth.models import User
from .models import KuebelSession, KuebelEintrag
from him2_referenzdaten.models import KuebelArt
from django.test import TransactionTestCase
from django.db.utils import IntegrityError
from .forms import KuebelEintragForm, KuebelSessionForm
from django.utils import timezone
from django.urls import reverse
from datetime import timedelta

# Models
class KuebelArtModelTest(TestCase):

    def test_create_kuebelart(self):
        art = KuebelArt.objects.create(kuebel_name="Großer Behälter")
        self.assertEqual(art.kuebel_name, "Großer Behälter")
        self.assertEqual(str(art), "Großer Behälter")

    def test_unique_kuebel_name(self):
        KuebelArt.objects.create(kuebel_name="Spezialbehälter")
        with self.assertRaises(Exception):
            KuebelArt.objects.create(kuebel_name="Spezialbehälter")


class KuebelSessionModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.session = KuebelSession.objects.create(
            user=self.user,
            user_name_manuell="Responsible User"
        )

    def test_create_kuebel_session(self):
        session = KuebelSession.objects.create(
            user=self.user,
            user_name_manuell="Max Mustermann",
            comments="Initialer Testlauf"
        )
        self.assertEqual(session.user.username, "testuser")
        self.assertEqual(session.user_name_manuell, "Max Mustermann")
        self.assertEqual(session.comments, "Initialer Testlauf")
        self.assertIsNotNone(session.created_at)
    
    def test_created_at_auto_set(self):
        # Ensure that created_at is not null
        self.assertIsNotNone(self.session.created_at)
        
        # Ensure that the created_at timestamp is not too far in the past or future
        now = timezone.now()
        self.assertTrue(self.session.created_at <= now)


class KuebelEintragModelTest(TestCase):

    def setUp(self):
        self.user = User.objects.create(username="eintraguser")
        self.session = KuebelSession.objects.create(
            user=self.user,
            user_name_manuell="Maria Musterfrau"
        )
        self.art = KuebelArt.objects.create(kuebel_name="Kleiner Kübel")

    def test_create_kuebel_eintrag(self):
        eintrag = KuebelEintrag.objects.create(
            log=self.session,
            kuebel_art=self.art,
            sonstiges_h=1.5,
            reinigung_h=2.0,
            waschen_h=0.5,
            waschen_count=3,
            instandh_h=1.0,
            instandh_count=1,
            zerlegen_h=0.8,
            zerlegen_count=2
        )
        self.assertEqual(eintrag.log, self.session)
        self.assertEqual(eintrag.kuebel_art, self.art)
        self.assertEqual(eintrag.waschen_count, 3)
        self.assertEqual(eintrag.instandh_count, 1)



class KuebelEintragModelTransactionTest(TransactionTestCase):

    def setUp(self):
        self.user = User.objects.create(username="testuser")
        self.session = KuebelSession.objects.create(
            user=self.user,
            user_name_manuell="Responsible Person"
        )

    def test_foreign_key_constraint_invalid_kuebel_art(self):
        # We have a valid session, but kuebel_art_id=999 does not exist
        eintrag = KuebelEintrag(
            log=self.session,
            kuebel_art_id=999,  # invalid FK
            sonstiges_h=1.0
        )
        with self.assertRaises(IntegrityError):
            eintrag.save()


# Forms 
class KuebelEintragFormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="formuser")
        self.session = KuebelSession.objects.create(user=self.user, user_name_manuell="Form User")
        self.art = KuebelArt.objects.create(kuebel_name="Großer Kübel")

    def test_form_valid_data(self):
        form = KuebelEintragForm(data={
            'log': self.session.id,
            'kuebel_art': self.art.id,
            'sonstiges_h': 2.5
        })
        self.assertTrue(form.is_valid())

    def test_form_missing_fields(self):
        form = KuebelEintragForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('kuebel_art', form.errors)  # This field must exist


class KuebelSessionFormTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create(username="formuser2")
        self.user_name_manuell = "Form User2"
        self.comments = "Kommentar"
        self.session = KuebelSession.objects.create(
            user=self.user,
            user_name_manuell=self.user_name_manuell,
            comments=self.comments
        )

    def test_form_valid_data(self):
        form = KuebelSessionForm(data={
            'user_name_manuell': self.user_name_manuell,
            'comments': self.comments
        })
        self.assertTrue(form.is_valid())
    
    def test_form_does_not_include_created_at_field(self):
        form = KuebelSessionForm(instance=self.session)
        
        # Check that 'created_at' is not in the form fields (should not be present)
        self.assertNotIn('created_at', form.fields)



# view 
class KuebelSessionViewTest(TestCase):

    def setUp(self):
        # Create a user and a kuebel_art object
        self.user = User.objects.create_user(username='testuser', password='password')

    def test_create_kuebel_session_invalid_created_at(self):
        # Log the user in
        self.client.login(user='testuser', password='password')

        # Submit the form with data, but do not include 'created_at'
        response = self.client.post(reverse('kuebel_aktivitaet'), data={
            'user_name_manuell': 'Test User',
            'comments': 'Test Comment',
        })

        if response.status_code == 200:
            # Check form errors to see why the form is not valid
            form = response.context.get('log_form')
            print("Form Errors:", form.errors)  # Print out form errors

            # Check if the KuebelSession object was created
            log = KuebelSession.objects.filter(user_name_manuell='Test User').first()
            self.assertIsNotNone(log, "KuebelSession object was not created.")

            # Ensure 'created_at' was set (it should be auto-generated)
            now = timezone.now()
            self.assertTrue(now - log.created_at < timedelta(seconds=2), "created_at was not set correctly.")
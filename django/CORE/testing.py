"""
Shared helpers for the test suite.

Every app's tests.py builds on SPDTestCase so users, roles and logins are
created the same way everywhere. Run the whole suite from this folder with:

    python manage.py test
"""
import io
import shutil
import tempfile

from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings

from PIL import Image

from AUTHENTICATE.models import Brother_Profile, Role

PASSWORD = 'Test-Password-123'

# Uploaded files go to a throwaway folder instead of the real media directory
TEST_MEDIA_ROOT = tempfile.mkdtemp(prefix='spd-test-media-')


def png_upload(name='photo.png', size=(600, 400)):
    """A real PNG file, for testing image uploads."""
    buffer = io.BytesIO()
    Image.new('RGB', size, 'red').save(buffer, format='PNG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/png')


# A fast password hasher keeps the suite quick; it is only used inside tests
@override_settings(MEDIA_ROOT=TEST_MEDIA_ROOT,
                   PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'])
class SPDTestCase(TestCase):

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEST_MEDIA_ROOT, ignore_errors=True)

    def make_member(self, username, *roles, first=None, last=None, pclass=None, profile=True):
        """Create a user with a Brother_Profile holding the given role names."""
        user = User.objects.create_user(username, email=f'{username}@example.com', password=PASSWORD)
        if profile:
            brother = Brother_Profile.objects.create(
                user=user,
                firstName=first or username.capitalize(),
                lastName=last or 'Tester',
                pclass=pclass,
            )
            brother.roles.set([Role.objects.get_or_create(name=r)[0] for r in roles])
        return user

    def login(self, user):
        self.client.force_login(user)
        return self.client

    def messages_for(self, response):
        return [str(m) for m in get_messages(response.wsgi_request)]

    def assertRedirectsToLogin(self, response):
        self.assertEqual(response.status_code, 302)
        self.assertIn('/auth/login', response['Location'])

    def assertDenied(self, response):
        """Role-protected pages redirect away instead of rendering."""
        self.assertEqual(response.status_code, 302)

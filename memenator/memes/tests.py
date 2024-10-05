from django.test import TestCase

from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework.test import APIRequestFactory
from rest_framework import status
from django.contrib.auth.models import User
from .models import MemeTemplate, Meme
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from .serializers import MemeCreateSerializer


class MemeAPITestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Create a meme template and a meme for testing
        self.template = MemeTemplate.objects.create(
            name="Test Template",
            image_url="https://i.imgur.com/UJ7UAVW.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )
        self.meme = Meme.objects.create(
            template=self.template,
            top_text="Top Text",
            bottom_text="Bottom Text",
            created_by=self.user
        )

    def test_create_meme(self):
        url = reverse('meme-list')  
        data = {
            'template': self.template.id,
            'top_text': 'Custom Top Text',
            'bottom_text': 'Custom Bottom Text'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['top_text'], 'Custom Top Text')
        self.assertEqual(response.data['bottom_text'], 'Custom Bottom Text')

    def test_create_meme_with_default_text(self):
        """If top_text or bottom_text is empty, it should use template's default values."""
        url = reverse('meme-list')
        data = {
            'template': self.template.id,
            'top_text': '',
            'bottom_text': ''
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # Ensure the default template texts are used when fields are empty
        self.assertEqual(response.data['top_text'], self.template.default_top_text)
        self.assertEqual(response.data['bottom_text'], self.template.default_bottom_text)

    def test_get_random_meme(self):
        url = reverse('meme-random')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id', response.data)
        self.assertIn('template', response.data)

    def test_get_random_meme_no_memes(self):
        Meme.objects.all().delete()  # Remove all memes
        url = reverse('meme-random')  
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


    



class MemeSerializerTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.template = MemeTemplate.objects.create(
            name="Test Template",
            image_url="https://i.imgur.com/UJ7UAVW.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )

    def test_meme_serializer_valid(self):
        data = {
            'template': self.template.id,
            'top_text': 'Some top text',
            'bottom_text': 'Some bottom text',
        }
        serializer = MemeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

    def test_meme_serializer_invalid(self):
        data = {
            'template': '',
            'top_text': 'Some top text',
            'bottom_text': 'Some bottom text',
        }
        serializer = MemeCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('template', serializer.errors)

    def test_meme_serializer_missing_top_text(self):
        data = {
            'template': self.template.id,
            'top_text': '',  
            'bottom_text': 'Some bottom text',
        }
        serializer = MemeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())  

    def test_meme_serializer_missing_bottom_text(self):
        data = {
            'template': self.template.id,
            'top_text': 'Some top text',
            'bottom_text': '',  
        }
        serializer = MemeCreateSerializer(data=data)
        self.assertTrue(serializer.is_valid())

class MemeModelTestCase(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.template = MemeTemplate.objects.create(
            name="Test Template",
            image_url="https://i.imgur.com/UJ7UAVW.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )

    def test_meme_creation(self):
        meme = Meme.objects.create(
            template=self.template,
            top_text="Top Text",
            bottom_text="Bottom Text",
            created_by=self.user
        )
        self.assertEqual(str(meme), f"{self.template.name} meme")

    def test_meme_creation_default_text(self):
        # Use the MemeCreateSerializer to create the meme
        data = {
            'template': self.template.id,  # Pass the id instead of the instance
            'top_text': '',  # Leave empty to trigger default
            'bottom_text': '',  # Leave empty to trigger default
        }

        # Create a mock request with a user
        factory = APIRequestFactory()
        request = factory.post('/memes/', data, format='json')
        request.user = self.user  # Set the user in the request

        serializer = MemeCreateSerializer(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        meme = serializer.save()

        # Check that the meme inherits the default text from the template
        self.assertEqual(meme.top_text, self.template.default_top_text)
        self.assertEqual(meme.bottom_text, self.template.default_bottom_text)

class MemeViewTestCase(APITestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        # Create a meme template and a meme for testing
        self.template = MemeTemplate.objects.create(
            name="Test Template",
            image_url="https://i.imgur.com/UJ7UAVW.png",
            default_top_text="Default Top",
            default_bottom_text="Default Bottom"
        )
        self.meme = Meme.objects.create(
            template=self.template,
            top_text="Top Text",
            bottom_text="Bottom Text",
            created_by=self.user
        )

    def test_create_meme_invalid_data(self):
        url = reverse('meme-list')
        data = {
            'template': '',  # Invalid template
            'top_text': '',
            'bottom_text': ''
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_can_get_memes(self):
        """Unauthenticated users can view memes (GET), but cannot create (POST)."""
        # Remove authentication for GET request
        self.client.credentials()  
        url = reverse('meme-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_post_requires_authentication(self):
        """Test that creating a meme (POST) requires authentication."""
        self.client.credentials()  # Remove authentication
        url = reverse('meme-list')
        data = {
            'template': self.template.id,
            'top_text': 'New Meme',
            'bottom_text': 'Funny Bottom Text'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_meme_detail(self):
        url = reverse('meme-detail', args=[self.meme.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['top_text'], 'Top Text')

    def test_get_meme_not_found(self):
        url = reverse('meme-detail', args=[999])  # Non-existing meme
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


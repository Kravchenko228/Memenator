from django.shortcuts import render
from PIL import Image, ImageDraw, ImageFont
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MemeTemplate, Meme, Rating
from .serializers import MemeTemplateSerializer, MemeSerializer, MemeCreateSerializer, RatingSerializer
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.conf import settings
from rest_framework.decorators import api_view
from rest_framework import status
import random
from imgurpython import ImgurClient
import os
from io import BytesIO


class MemePagination(PageNumberPagination):
    page_size = 10

class MemeTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MemeTemplate.objects.all()
    serializer_class = MemeTemplateSerializer

class MemeViewSet(viewsets.ModelViewSet):
    queryset = Meme.objects.all().order_by('-creation_date')
    serializer_class = MemeSerializer
    pagination_class = MemePagination

    def get_serializer_class(self):
        if self.action == 'create':
            return MemeCreateSerializer
        return MemeSerializer

    def get_permissions(self):
        if self.action in ['create', 'rate']:
            return [IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def rate(self, request, pk=None):
        meme = self.get_object()
        score = request.data.get('score')
        user = request.user
        if not score or not (1 <= int(score) <= 5):
            return Response({'error': 'Invalid score. Must be between 1 and 5.'}, status=status.HTTP_400_BAD_REQUEST)

        rating, created = Rating.objects.update_or_create(
            meme=meme, user=user,
            defaults={'score': score}
        )
        return Response({'status': 'rating set', 'score': score})

    @action(detail=False)
    def random(self, request):
        meme = Meme.objects.order_by('?').first()
        if meme is None:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = self.get_serializer(meme)
        return Response(serializer.data)


    @action(detail=False)
    def top(self, request):
        top_memes = Meme.objects.annotate(average_rating=Avg('rating__score')).order_by('-average_rating')[:10]
        serializer = self.get_serializer(top_memes, many=True)
        return Response(serializer.data)

#Bonus
FUNNY_PHRASES = [
    "When life gives you lemons, make memes!",
    "I'm not lazy, I'm on energy-saving mode.",
    "404: Not found",
    "I followed my heart, it led me to the fridge.",
    "This is fine.",
    "I can't even...",
    "Me trying to understand 2020.",
    "I'm not arguing, I'm just explaining why I'm right."
]

# Initialize Imgur Client
client_id = settings.IMGUR_CLIENT_ID
client_secret = settings.IMGUR_CLIENT_SECRET
imgur_client = ImgurClient(client_id, client_secret)

@api_view(['GET'])
def surprise_me_meme(request):
    """
    Returns a meme with random text and uploads it to Imgur.
    """
    # Select a random meme template
    meme_template = MemeTemplate.objects.order_by('?').first()
    if meme_template is None:
        return Response({"detail": "No meme template found"}, status=404)

    # Select a random phrase
    top_text = random.choice(FUNNY_PHRASES)
    bottom_text = random.choice(FUNNY_PHRASES)

    # Download the image from the URL
    response = requests.get(meme_template.image_url)
    if response.status_code != 200:
        return Response({"detail": "Failed to download image from URL"}, status=400)

    img = Image.open(BytesIO(response.content))

    # Add text to the image
    draw = ImageDraw.Draw(img)
    
    # Load font
    font_path = os.path.join(settings.MEDIA_ROOT, 'moovieStar.ttf')  # Ensure the font exists
    font = ImageFont.truetype(font_path, 40)

    # Add top text
    draw.text((50, 50), top_text, font=font, fill="white")

    # Add bottom text
    draw.text((50, img.size[1] - 100), bottom_text, font=font, fill="white")

    # Save the modified image to a buffer
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)

    # Upload the modified image to Imgur
    with open('generated_meme.jpg', 'wb') as f:
        f.write(buffer.read())
    uploaded_image = imgur_client.upload_from_path('generated_meme.jpg', anon=True)

    # Return the URL of the uploaded meme
    meme_url = uploaded_image['link']
    return Response({"meme_url": meme_url})


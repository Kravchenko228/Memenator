from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import MemeTemplate, Meme, Rating
from .serializers import MemeTemplateSerializer, MemeSerializer, MemeCreateSerializer, RatingSerializer
from django.db.models import Avg
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination


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


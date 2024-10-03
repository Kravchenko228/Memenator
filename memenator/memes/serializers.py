from rest_framework import serializers
from .models import MemeTemplate, Meme, Rating


class MemeTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = MemeTemplate
        fields = ['id', 'name', 'image_url', 'default_top_text', 'default_bottom_text']

class MemeSerializer(serializers.ModelSerializer):
    template = MemeTemplateSerializer(read_only=True)
    created_by = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Meme
        fields = ['id', 'template', 'top_text', 'bottom_text', 'created_by', 'creation_date']

class MemeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meme
        fields = ['template', 'top_text', 'bottom_text']

    def create(self, validated_data):
        request = self.context.get('request')
        template = validated_data.get('template')

        top_text = validated_data.get('top_text', template.default_top_text)
        bottom_text = validated_data.get('bottom_text', template.default_bottom_text)

        meme = Meme.objects.create(
            created_by=request.user, 
            template=template, 
            top_text=top_text, 
            bottom_text=bottom_text
        )
        return meme


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['meme', 'user', 'score', 'created_at']
        

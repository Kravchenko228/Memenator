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
    top_text = serializers.CharField(allow_blank=True, required=False)
    bottom_text = serializers.CharField(allow_blank=True, required=False)

    class Meta:
        model = Meme
        fields = ['template', 'top_text', 'bottom_text']

    def validate(self, data):
        """
        Custom validation to allow blank values and replace them with the default template text.
        """
        template = data.get('template')

        # Use default text from template if top_text or bottom_text is blank or None
        if not data.get('top_text'):
            data['top_text'] = template.default_top_text
        if not data.get('bottom_text'):
            data['bottom_text'] = template.default_bottom_text

        return data

    def create(self, validated_data):
        request = self.context.get('request')
        meme = Meme.objects.create(
            created_by=request.user,
            template=validated_data.get('template'),
            top_text=validated_data.get('top_text'),
            bottom_text=validated_data.get('bottom_text')
        )
        return meme


    def create(self, validated_data):
        request = self.context.get('request')
        meme = Meme.objects.create(
            created_by=request.user,
            template=validated_data.get('template'),
            top_text=validated_data.get('top_text'),
            bottom_text=validated_data.get('bottom_text')
        )
        return meme




class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['meme', 'user', 'score', 'created_at']
        

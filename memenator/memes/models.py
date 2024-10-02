from django.db import models
from django.contrib.auth.models import User


class MemeTemplate(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    image_url = models.URLField()
    default_top_text = models.CharField(max_length=100)
    default_bottom_text = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Meme(models.Model):
    id = models.AutoField(primary_key=True)
    template = models.ForeignKey(MemeTemplate, on_delete=models.CASCADE)
    top_text = models.CharField(max_length=100)
    bottom_text = models.CharField(max_length=100)
    image_url = models.URLField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    creation_date = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        return f"{self.template.name} meme"

class Rating(models.Model):
    id = models.AutoField(primary_key=True)
    meme = models.ForeignKey(Meme, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    #Score 
    SCORE_CHOICES = [
        (1, '1'),
        (2, '2'),
        (3, '3'),
        (4, '4'),
        (5, '5'),
    ]
    score = models.PositiveSmallIntegerField(choices=SCORE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['meme', 'user']

    def __str__(self):
        return f"{self.meme} rated {self.score} by {self.user}"

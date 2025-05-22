from dj_rest_auth.registration.serializers import RegisterSerializer
from dj_rest_auth.serializers import LoginSerializer
from rest_framework import serializers
from articles.models import ArticleLike, ArticleView, ArticleScrap, NewsArticle
from articles.serializers import NewsArticleSerializer, SimpleNewsArticleSerializer
from .models import User

class CustomRegisterSerializer(RegisterSerializer):
    username = None

    date_of_birth = serializers.DateField()
    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ['email', 'date_of_birth', 'first_name', 'last_name']

    def save(self, request):
        user = super().save(request)
        user.date_of_birth = self.data.get('date_of_birth')
        user.first_name = self.data.get('first_name')
        user.last_name = self.data.get('last_name')
        user.save()
        return user

class CustomLoginSerializer(LoginSerializer):
    username = None
    email = serializers.EmailField(required=True)

    def validate(self, attrs):
        attrs['email'] = attrs['email'].lower()
        return super().validate(attrs)

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'date_of_birth', 'is_active', 'created_at', 'updated_at']

class UserLikedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleLike
        fields = ['article', 'liked_at']

class UserViewedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleView
        fields = ['article', 'viewed_at']

class UserScrappedArticleSerializer(serializers.ModelSerializer):
    article = SimpleNewsArticleSerializer(read_only=True)
    class Meta:
        model = ArticleScrap
        fields = ['article', 'scrapped_at']

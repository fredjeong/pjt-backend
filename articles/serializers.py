from rest_framework import serializers
from .models import NewsArticles, ArticleLike, ArticleView, ArticleScrap

# 뉴스 기사 아이디로 기사 조회하는 시리얼라이저
class NewsArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticles
        fields = '__all__'

class SimpleNewsArticlesSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsArticles
        fields = ['id', 'title']

# 좋아요 시리얼라이저
class ArticleLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleLike
        fields = '__all__'

# 조회수 시리얼라이저
class ArticleViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleView
        fields = '__all__'

# 스크랩 시리얼라이저
class ArticleScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArticleScrap
        fields = '__all__'
        

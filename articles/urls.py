from django.urls import path, include
from .views import NewsArticlesAPIView, related_articles_by_cosine

urlpatterns = [
    path('<int:pk>/', NewsArticlesAPIView, name='get_article'),
    path('<int:pk>/related/', related_articles_by_cosine, name='related-articles'),
]
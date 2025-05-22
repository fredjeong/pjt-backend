from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.article_list, name='article-list'),
    path('<int:pk>/', views.article_detail, name='get_article'),
    path('<int:pk>/related/', views.related_articles, name='related-articles'),
    path('api/search/', views.search_articles, name='search-articles'),
]
from django.shortcuts import render

# Create your views here.

from rest_framework import viewsets
from .models import NewsArticles, ArticleLike, ArticleView, ArticleScrap
from .serializers import NewsArticlesSerializer, SimpleNewsArticlesSerializer, ArticleLikeSerializer, ArticleViewSerializer, ArticleScrapSerializer
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
import numpy as np
from utils import parse_embedding, cosine_similarity
from accounts.models import User

@api_view(['GET'])
def NewsArticlesAPIView(request, pk):
    try:
        article = NewsArticles.objects.get(pk=pk)
    except NewsArticles.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=404)
    serializer = NewsArticlesSerializer(article)
    return Response(serializer.data)

@api_view(['GET'])
def related_articles_by_cosine(request, pk):
    try:
        article = NewsArticles.objects.get(pk=pk)
    except NewsArticles.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=404)

    base_emb = parse_embedding(article.content_embedding)
    all_articles = NewsArticles.objects.exclude(pk=pk)
    similarities = []

    for article in all_articles:
        try:
            emb = parse_embedding(article.content_embedding)
            sim = cosine_similarity(base_emb, emb)
            similarities.append((sim, article))
        except Exception:
            continue

    # 유사도 내림차순 정렬 후 상위 5개
    sorted_articles = sorted(similarities, key=lambda x: x[0], reverse=True)
    
    if len(sorted_articles) < 5:
        top_related = sorted_articles
    else:
        top_related = sorted_articles[:5]
    
    top_articles = [a for _, a in top_related]
    data = SimpleNewsArticlesSerializer(top_articles, many=True).data
    
    return Response(data)


from django.shortcuts import render

# Create your views here.

from rest_framework import status
from .models import NewsArticle, ArticleLike, ArticleView, ArticleScrap
from .serializers import NewsArticleSerializer, SimpleNewsArticleSerializer, ArticleLikeSerializer, ArticleViewSerializer, ArticleScrapSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
import numpy as np
from utils import parse_embedding, cosine_similarity
from accounts.models import User
from django.conf import settings
from elasticsearch import Elasticsearch

"""
전체 기사 목록 조회
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def article_list(request):
    articles = NewsArticle.objects.all()
    serializer = SimpleNewsArticleSerializer(articles, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


"""
기사 pk를 통해 조회 기사 상세 내용 조회
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def article_detail(request, pk):
    try:
        article = get_object_or_404(NewsArticle, pk=pk)
        serializer = NewsArticleSerializer(article, context={'request': request})
        
        # 조회수, 좋아요수, 스크랩수 추가
        response_data = serializer.data
        response_data['view_count'] = ArticleView.objects.filter(article=article).count()
        response_data['like_count'] = ArticleLike.objects.filter(article=article).count()
        response_data['scrap_count'] = ArticleScrap.objects.filter(article=article).count()
        
        return Response(response_data, status=status.HTTP_200_OK)
    
    except NewsArticle.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)


"""
연관 기사 추천
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def related_articles(request, pk):
    try:
        article = get_object_or_404(NewsArticle, pk=pk)
    except NewsArticle.DoesNotExist:
        return Response({'detail': '해당 기사가 존재하지 않습니다.'}, status=status.HTTP_404_NOT_FOUND)

    base_emb = parse_embedding(article.content_embedding)
    all_articles = NewsArticle.objects.exclude(pk=pk)
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
    data = SimpleNewsArticleSerializer(top_articles, many=True).data
    
    return Response(data, status=status.HTTP_200_OK)


"""
기사 검색 
"""
@api_view(['GET'])
@permission_classes([AllowAny])
def search_articles(request):
    query = request.GET.get('q', '')
    
    if not query:
        return Response({'results': []})
    
    try:
        # Elasticsearch 클라이언트 설정
        es = Elasticsearch(
            [f"http://{settings.ES_CONFIG['host']}:{settings.ES_CONFIG['port']}"],
            basic_auth=(settings.ES_CONFIG['user'], settings.ES_CONFIG['password']),
            verify_certs=settings.ES_CONFIG['use_ssl']
        )
        
        # 검색 쿼리 실행
        search_query = {
            "query": {
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "content", "summary^2", "keywords^2"],
                    "type": "most_fields"
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "content": {},
                    "summary": {}
                }
            },
            "size": 20
        }
        
        # Elasticsearch 검색 실행
        search_results = es.search(index=settings.ES_CONFIG['index'], body=search_query)
        
        # 검색 결과 형식화
        results = []
        for hit in search_results['hits']['hits']:
            source = hit['_source']
            
            # 하이라이트 처리
            highlights = {}
            if 'highlight' in hit:
                for field, highlighted_fragments in hit['highlight'].items():
                    highlights[field] = "...".join(highlighted_fragments)
            
            # PostgreSQL ID를 가져와서 해당 기사 정보 조회
            try:
                article_id = hit['_id']
                article = NewsArticle.objects.get(id=article_id)
                serializer = NewsArticleSerializer(article)
                article_data = serializer.data
                article_data['highlights'] = highlights
                article_data['score'] = hit['_score']
                results.append(article_data)
            except NewsArticle.DoesNotExist:
                # Elasticsearch에는 있지만 PostgreSQL에는 없는 경우
                result = {
                    'id': hit['_id'],
                    'title': source.get('title', ''),
                    'content': source.get('content', ''),
                    'summary': source.get('summary', ''),
                    'writer': source.get('writer', ''),
                    'write_date': source.get('write_date', ''),
                    'category': source.get('category', ''),
                    'url': source.get('url', ''),
                    'keywords': source.get('keywords', []),
                    'highlights': highlights,
                    'score': hit['_score']
                }
                results.append(result)
        
        return Response({'results': results})
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

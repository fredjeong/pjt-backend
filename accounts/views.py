from dj_rest_auth.registration.views import RegisterView
from dj_rest_auth.views import LoginView
from .serializers import CustomRegisterSerializer, CustomLoginSerializer
# from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import User
from articles.models import ArticleLike, ArticleView, ArticleScrap, NewsArticles
from .serializers import (
    UserProfileSerializer,
    UserLikedArticlesSerializer,
    UserViewedArticlesSerializer,
    UserScrappedArticlesSerializer,
    SimpleNewsArticlesSerializer,
)
from rest_framework.decorators import api_view
from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes
from utils import parse_embedding, cosine_similarity
import numpy as np

# Create your views here.
class CustomRegisterAPIView(RegisterView):
    serializer_class = CustomRegisterSerializer
    
    def create_jwt_response(self, user):
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'message': '회원가입이 성공하였습니다.'
        }
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            user = serializer.save(request)
            return Response(self.create_jwt_response(user), status=status.HTTP_201_CREATED)
        except ValidationError as e:
            # 회원가입 실패 시 커스텀 메시지 반환
            return Response(
                {
                    "message": "회원가입에 실패하였습니다.",
                    "detail": e.detail  # 에러 상세 정보도 같이 반환
                },
                status=status.HTTP_400_BAD_REQUEST
            )

class CustomLoginAPIView(LoginView):
    serializer_class = CustomLoginSerializer
    
    def create_jwt_response(self, user):
        refresh = RefreshToken.for_user(user)
        user_data = UserProfileSerializer(user).data
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': user_data,
            'message': '로그인이 성공하였습니다.'
        }
    
    def post(self, request, *args, **kwargs):
        try:
            response = super().post(request, *args, **kwargs)
            user = self.user
            return Response(self.create_jwt_response(user), status=status.HTTP_200_OK)
        except AuthenticationFailed as e:
            return Response({
                'message': '로그인에 실패하였습니다.',
                'detail': str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def UserDetailWithArticlesAPIView(request, pk):
    user = get_object_or_404(User, pk=pk)
    user_data = UserProfileSerializer(user).data
    liked_articles = ArticleLike.objects.filter(user=user)
    viewed_articles = ArticleView.objects.filter(user=user)
    scrapped_articles = ArticleScrap.objects.filter(user=user)
    return Response({
        'user': user_data,
        'liked_articles': UserLikedArticlesSerializer(liked_articles, many=True).data,
        'viewed_articles': UserViewedArticlesSerializer(viewed_articles, many=True).data,
        'scrapped_articles': UserScrappedArticlesSerializer(scrapped_articles, many=True).data,
    }, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def recommend_articles_for_user(request, user_pk):
    try:
        user = User.objects.get(pk=user_pk)
    except User.DoesNotExist:
        return Response({'detail': '해당 유저가 존재하지 않습니다.'}, status=404)

    # 최근 상호작용 기사 10개씩 가져오기 (중복 제거)
    viewed_ids = list(ArticleView.objects.filter(user=user).order_by('-viewed_at').values_list('article_id', flat=True)[:10])
    liked_ids = list(ArticleLike.objects.filter(user=user).order_by('-created_at').values_list('article_id', flat=True)[:10])
    scrapped_ids = list(ArticleScrap.objects.filter(user=user).order_by('-scrapped_at').values_list('article_id', flat=True)[:10])
    interacted_ids = list(set(viewed_ids + liked_ids + scrapped_ids))

    if not interacted_ids:
        return Response({'detail': '추천을 위한 상호작용 기록이 없습니다.'}, status=200)

    # 임베딩 평균 구하기
    embeddings = []
    for article_id in interacted_ids:
        try:
            article = NewsArticles.objects.get(pk=article_id)
            emb = parse_embedding(article.content_embedding)
            embeddings.append(emb)
        except Exception:
            continue

    if not embeddings:
        return Response({'detail': '임베딩 정보가 없습니다.'}, status=200)

    mean_emb = np.mean(embeddings, axis=0)

    # 유저가 상호작용하지 않은 기사만 추천 대상으로
    exclude_ids = set(interacted_ids)
    candidates = NewsArticles.objects.exclude(pk__in=exclude_ids)
    similarities = []
    for article in candidates:
        try:
            emb = parse_embedding(article.content_embedding)
            sim = cosine_similarity(mean_emb, emb)
            similarities.append((sim, article))
        except Exception:
            continue

    # 유사도 내림차순 정렬 후 상위 5개
    sorted_articles = sorted(similarities, key=lambda x: x[0], reverse=True)
    top_articles = [a for _, a in sorted_articles[:5]]
    data = SimpleNewsArticlesSerializer(top_articles, many=True).data

    return Response(data)

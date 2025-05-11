from django.urls import path, include
from .views import CustomRegisterAPIView, CustomLoginAPIView, UserDetailWithArticlesAPIView, recommend_articles_for_user

urlpatterns = [
    path('signup/', CustomRegisterAPIView.as_view(), name='signup'),
    path('login/', CustomLoginAPIView.as_view(), name='login'),
    
    # dj_rest_auth의 기본 뷰(로그아웃, 회원정보 등)는 아래에서 처리
    path('', include('dj_rest_auth.urls')),
    # path('dj-rest-auth/registration/', include('dj_rest_auth.registration.urls')),
    path('<int:pk>/', UserDetailWithArticlesAPIView, name='user-detail-with-articles'),
    path('<int:user_pk>/recommended/', recommend_articles_for_user, name='recommend-articles-for-user'),
]
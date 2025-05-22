from django.urls import path, include
from . import views

urlpatterns = [
    # 회원가입 및 로그인 관련
    path('signup/', views.custom_register.as_view(), name='signup'),
    path('login/', views.custom_login.as_view(), name='login'),
    
    # dj_rest_auth의 기본 뷰(로그아웃, 회원정보 등)는 아래에서 처리
    path('', include('dj_rest_auth.urls')),
    
    # 유저 정보 상세 조회
    path('<int:pk>/', views.user_details, name='user-detail-with-articles'),
    
    # 유저 추천 기사 조회
    path('<int:user_pk>/recommended/', views.recommended_articles, name='recommend-articles-for-user'),

    # 유저 기사 조회 기록 저장
    path('article/view/', views.record_article_view, name='record-article-view'),

    # 유저 기사 좋아요 기록 저장
    path('article/like/', views.toggle_article_like, name='toggle-article-like'),

    # 유저 기사 스크랩 기록 저장
    path('article/scrap/', views.toggle_article_scrap, name='toggle-article-scrap'),

    # 프론트에서 좋아요 여부 확인 필요하여 작성
    path("article/check-like/", views.check_article_like),
    

    # # 대시보드 관련 API
    # path("dashboard/stats/", views.get_dashboard_stats),
    # path("dashboard/keywords/", views.get_keyword_frequency),
    # path("dashboard/weekly-reads/", views.get_weekly_reads),
    # path("dashboard/favorites/", views.get_favorite_articles),
]

from django.contrib import admin
from .models import NewsArticles, ArticleLike, ArticleView, ArticleScrap

# Register your models here.
admin.site.register(NewsArticles)
admin.site.register(ArticleLike)
admin.site.register(ArticleView)
admin.site.register(ArticleScrap)

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameUserViewSet, ItemViewSet, SkillViewSet, StatsViewSet

router = DefaultRouter()
router.register('users', GameUserViewSet, basename='user')
router.register('items', ItemViewSet, basename='item')
router.register('skills', SkillViewSet, basename='skill')
router.register('stats', StatsViewSet, basename='stats')

urlpatterns = [
    path('', include(router.urls)),
]

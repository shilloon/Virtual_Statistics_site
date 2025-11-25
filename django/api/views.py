from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from stats.models import GameUser, PlayerStats, Item, Skill, ItemUsage, SkillUsage
from .serializers import(
    GameUserSerializer,
    GameUserDetailSerializer,
    ItemSerializer,
    SkillSerializer,
    PlayerStatsSerializer
)

# Create your views here.
class GameUserViewSet(viewsets.ReadOnlyModelViewSet):
    """게임 유저 API"""
    queryset = GameUser.objects.all()
    serializer_class = GameUserSerializer

    def get_serializer_class(self):
        """상세 조회시 다른 Serializer 사용"""
        if self.action == 'retrieve':
            return GameUserDetailSerializer
        return GameUserSerializer
    
    @action(detail=False, methods=['get'])
    def top_rankers(self, request):
        """상위 랭킹 유저 조회"""
        limit = int(request.query_params.get('limit', 100))
        tier = request.query_params.get('tier', None)

        queryset = GameUser.objects.select_related('stats')

        if tier and tier != 'ALL':
            queryset = queryset.filter(tier=tier)

        top_users = queryset.order_by('-ranking_score')[:limit]
        serializer = self.get_serializer(top_users, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods = ['get'])
    def tier_stats(self, request):
        """티어별 통계"""
        tier = request.query_params.get('tier', None)

        if tier:
            users = GameUser.objects.filter(tier=tier)
        else:
            users = GameUser.objects.all()

        # 티어별 집계
        tier_data = {}
        for tier_choice in GameUser.TIER_CHOICES:
            tier_code = tier_choice[0]
            tier_users = users.filter(tier = tier_code)

            tier_data[tier_code] = {
                'count': tier_users.count(),
                'avg_level' : tier_users.aggregate(Avg('level'))['level__avg'] or 0,
                'avg_ranking_score' : tier_users.aggregate(Avg('ranking_score'))['ranking_score__avg'] or 0,
            }
        
        return Response(tier_data)
    
class ItemViewSet(viewsets.ReadOnlyModelViewSet):
    """아이템 API"""
    queryset = Item.objects.all()
    serializer_class = ItemSerializer

    @action(detail=False, methods=['get'])
    def popular_items(self, request):
        """인기 아이템 (사용 빈도 기준)"""
        item_type = request.query_params.get('type', None)
        tier = request.query_params.get('tier', None)
        limit = int(request.query_params.get('limit', 10))

        # 기본 쿼리
        queryset = Item.objects.annotate(
            total_usage = Count('item_usages')
        )

        # 필터링
        if item_type:
            queryset = queryset.filter(item_type = item_type)
        
        # 특정 티어 유저들의 아이템 사용만 잡계
        if tier:
            queryset = queryset.filter(
                item_usages__player_stats__user__tier=tier
            ).annotate(
                tier_usage = Count('item_usages')
            ).order_by('-tier_usage')[:limit]
        else:
            queryset = queryset.order_by('-total_usage')[:limit]

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """스킬 API"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    @action(detail=False, methods=['get'])
    def popular_skills(self, request):
        """인기 스킬 (사용 빈도 기준)"""
        skill_type = request.query_params.get('type', None)
        tier = request.query_params.get('tier', None)
        limit = int(request.query_params.get('limit', 10))

        # 기본 쿼리
        queryset = Skill.objects.annotate(
            total_usage = Count('skill_usages')
        )

        # 필터링
        if skill_type:
            queryset = queryset.filter(skill_type=skill_type)

        # 특정 티어 유저들의 스킬 사용만 집계
        if tier:
            queryset = queryset.filter(
                skill_usages__player_stats__user__tier=tier
            ).annotate(
                tier_usage = Count('skill_usages')
            ).order_by('-tier_usage')[:limit]
        else:
            queryset = queryset.order_by('-total_usage')[:limit]
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
class StatsViewSet(viewsets.ViewSet):
    """통계 분석 API"""

    @action(detail=False, methods=['get'])
    def top_players_items(self, request):
        """상위 랭커들이 많이 사용하는 아이템"""
        top_percent = int(request.query_params.get('top_percent', 10))

        # 상위 N% 유저 계산
        total_users = GameUser.objects.count()
        top_count = int(total_users * top_percent / 100)

        top_users = GameUser.objects.order_by('-ranking_score')[:top_count]

        # 해당 유저들의 아이템 사용 집계
        popular_items = Item.objects.filter(
            item_usages__player_stats__user__in = top_users
        ).annotate(
            usage_count = Count('item_usages')
        ).order_by('-usage_count')[:20]

        serializer = ItemSerializer(popular_items, many=True)
        return Response({
            'top_percent': top_percent,
            'top_user_count' : top_count,
            'items' : serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def top_players_skills(self, request):
        """상위 랭커들이 가장 많이 사용하는 스킬"""
        top_percent = int(request.query_params.get('top_percent', 10))

        # 상위 N% 유저 계산
        total_users = GameUser.objects.count()
        top_count = int(total_users * top_percent / 100)

        top_users = GameUser.objects.order_by('-ranking_score')[:top_count]

        # 해당 유저들의 스킬 사용 집계
        popular_skills = Skill.objects.filter(
            skill_usages__player_stats__user__in = top_users
        ).annotate(
            usage_count = Count('skill_usages')
        ).order_by('-usage_count')[:20]

        serializer = SkillSerializer(popular_skills, many=True)
        return Response({
            'top_percent' : top_percent,
            'top_user_count' : top_count,
            'skills' : serializer.data
        })


        
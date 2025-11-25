from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Avg, Q
from django.db import connection
from stats.models import GameUser, PlayerStats, Item, Skill, ItemUsage, SkillUsage
from .serializers import(
    GameUserSerializer,
    GameUserDetailSerializer,
    ItemSerializer,
    SkillSerializer,
    PlayerStatsSerializer
)
import time


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
        start = time.time()

        item_type = request.query_params.get('type', None)
        tier = request.query_params.get('tier', None)
        limit = int(request.query_params.get('limit', 10))

        with connection.cursor() as cursor:
            if tier and tier != 'ALL':
                sql = """
                    SELECT 
                        i.id,
                        i.name,
                        i.item_type,
                        i.description,
                        i.price,
                        SUM(iu.usage_count) as total_usage
                    FROM stats_item i
                    INNER JOIN stats_itemusage iu ON i.id = iu.item_id
                    INNER JOIN stats_playerstats ps ON iu.player_stats_id = ps.id
                    INNER JOIN stats_gameuser u ON ps.user_id = u.id
                    WHERE u.tier = %s
                """
                params = [tier]
                
                if item_type:
                    sql += " AND i.item_type = %s"
                    params.append(item_type)
                
                sql += """
                    GROUP BY i.id, i.name, i.item_type, i.description, i.price
                    ORDER BY total_usage DESC
                    LIMIT %s
                """
                params.append(limit)
            else:
                # 전체 조회
                sql = """
                    SELECT 
                        i.id,
                        i.name,
                        i.item_type,
                        i.description,
                        i.price,
                        SUM(iu.usage_count) as total_usage
                    FROM stats_item i
                    LEFT JOIN stats_itemusage iu ON i.id = iu.item_id
                """
                params = []
                
                if item_type:
                    sql += " WHERE i.item_type = %s"
                    params.append(item_type)
                
                sql += """
                    GROUP BY i.id, i.name, i.item_type, i.description, i.price
                    ORDER BY total_usage DESC
                    LIMIT %s
                """
                params.append(limit)
            
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        elapsed = time.time() - start
        print(f"popular_items 실행시간: {elapsed:.3f}초, 결과: {len(results)}개")
        
        return Response(results)


class SkillViewSet(viewsets.ReadOnlyModelViewSet):
    """스킬 API"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

    @action(detail=False, methods=['get'])
    def popular_skills(self, request):
        """인기 스킬 (사용 빈도 기준)"""
        start = time.time()

        skill_type = request.query_params.get('type', None)
        tier = request.query_params.get('tier', None)
        limit = int(request.query_params.get('limit', 10))

        with connection.cursor() as cursor:
            if tier and tier != 'ALL':
                sql = """
                    SELECT 
                        s.id,
                        s.name,
                        s.skill_type,
                        s.description,
                        s.cooldown,
                        SUM(su.usage_count) as total_usage
                    FROM stats_skill s
                    INNER JOIN stats_skillusage su ON s.id = su.skill_id
                    INNER JOIN stats_playerstats ps ON su.player_stats_id = ps.id
                    INNER JOIN stats_gameuser u ON ps.user_id = u.id
                    WHERE u.tier = %s
                """
                params = [tier]
                
                if skill_type:
                    sql += " AND s.skill_type = %s"
                    params.append(skill_type)
                
                sql += """
                    GROUP BY s.id, s.name, s.skill_type, s.description, s.cooldown
                    ORDER BY total_usage DESC
                    LIMIT %s
                """
                params.append(limit)
            else:
                sql = """
                    SELECT 
                        s.id,
                        s.name,
                        s.skill_type,
                        s.description,
                        s.cooldown,
                        SUM(su.usage_count) as total_usage
                    FROM stats_skill s
                    LEFT JOIN stats_skillusage su ON s.id = su.skill_id
                """
                params = []
                
                if skill_type:
                    sql += " WHERE s.skill_type = %s"
                    params.append(skill_type)
                
                sql += """
                    GROUP BY s.id, s.name, s.skill_type, s.description, s.cooldown
                    ORDER BY total_usage DESC
                    LIMIT %s
                """
                params.append(limit)
            
            cursor.execute(sql, params)
            columns = [col[0] for col in cursor.description]
            results = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        elapsed = time.time() - start
        print(f"popular_skills 실행시간: {elapsed:.3f}초, 결과: {len(results)}개")
        
        return Response(results)
    
class StatsViewSet(viewsets.ViewSet):
    """통계 분석 API"""

    @action(detail=False, methods=['get'])
    def top_players_items(self, request):
        """상위 랭커들이 많이 사용하는 아이템"""
        start = time.time()
        top_percent = int(request.query_params.get('top_percent', 10))

        # 상위 N% 유저 계산
        total_users = GameUser.objects.count()
        top_count = int(total_users * top_percent / 100)

        with connection.cursor() as cursor:
            sql = """
                SELECT
                    i.id,
                    i.name,
                    i.item_type,
                    i.description,
                    i.price,
                    COUNT(iu.id) as usage_count
                FROM stats_item i
                LEFT JOIN stats_itemusage iu ON i.id = iu.item_id
                LEFT JOIN stats_playerstats ps ON iu.player_stats_id = ps.id
                LEFT JOIN stats_gameuser u ON ps.user_id = u.id
                WHERE u.id IN (
                    SELECT id FROM stats_gameuser
                    ORDER BY ranking_score DESC
                    LIMIT %s
                )
                GROUP BY i.id, i.name, i.item_type, i.description, i.price
                ORDER BY usage_count DESC
                LIMIT 20
            """
            cursor.execute(sql, [top_count])
            columns = [col[0] for col in cursor.description]
            items = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        elapsed = time.time() - start
        print(f"top_players_items 실행시간: {elapsed:.3f}초")

        return Response({
            'top_percent': top_percent,
            'top_user_count' : top_count,
            'items' : items
        })
    
    @action(detail=False, methods=['get'])
    def top_players_skills(self, request):
        """상위 랭커들이 가장 많이 사용하는 스킬"""
        start = time.time()
        top_percent = int(request.query_params.get('top_percent', 10))

        # 상위 N% 유저 계산
        total_users = GameUser.objects.count()
        top_count = int(total_users * top_percent / 100)

        with connection.cursor() as cursor:
            sql = """
                SELECT
                    s.id,
                    s.name,
                    s.skill_type,
                    s.description,
                    s.cooldown,
                    COUNT(su.id) as usage_count
                FROM stats_skill s
                LEFT JOIN stats_skillusage su ON s.id = su.skill_id
                LEFT JOIN stats_playerstats ps ON su.player_stats_id = ps.id
                LEFT JOIN stats_gameuser u ON ps.user_id = u.id
                WHERE u.id IN(
                    SELECT id FROM stats_gameuser
                    ORDER BY ranking_score DESC
                    LIMIT %s
                )
                GROUP BY s.id, s.name, s.skill_type, s.description, s.cooldown
                ORDER BY usage_count DESC
                LIMIT 20
            """

            cursor.execute(sql, [top_count])
            columns = [col[0] for col in cursor.description]
            skills = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        elapsed = time.time() - start
        print(f"top_players_skills 실행시간: {elapsed:.3f}초")

        return Response({
            'top_percent' : top_percent,
            'top_user_count' : top_count,
            'skills' : skills
        })


        
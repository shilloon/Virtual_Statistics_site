from rest_framework import serializers
from stats.models import GameUser, PlayerStats, Item, Skill, ItemUsage, SkillUsage

class ItemSerializer(serializers.ModelSerializer):
    """아이템 정보"""

    total_usage = serializers.IntegerField(read_only=True, default = 0)

    class Meta:
        model = Item
        fields = ['id', 'name', 'item_type', 'description', 'price', 'total_usage']

class SkillSerializer(serializers.ModelSerializer):
    """스킬 정보"""
    total_usage = serializers.IntegerField(read_only=True, default = 0)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'skill_type', 'description', 'cooldown', 'total_usage']

class ItemUsageSerializer(serializers.ModelSerializer):
    """아이템 사용 기록"""
    item = ItemSerializer(read_only=True)

    class Meta:
        model = ItemUsage
        fields = ['item', 'usage_count', 'last_used']

class SkillUsageSerializer(serializers.ModelSerializer):
    """스킬 사용 기록"""
    skill = SkillSerializer(read_only=True)

    class Meta:
        model = SkillUsage
        fields = ['skill', 'usage_count', 'last_used']

class PlayerStatsSerializer(serializers.ModelSerializer):
    """플레이어 상세 통계"""
    item_usages = ItemUsageSerializer(many=True, read_only =True)
    skill_usages = SkillUsageSerializer(many=True, read_only=True)

    class Meta:
        model = PlayerStats
        fields = ['total_games', 'wins', 'losses', 'win_rate', 'play_time', 'item_usages', 'skill_usages']

class GameUserSerializer(serializers.ModelSerializer):
    """게임 유저 기본 정보"""
    win_rate = serializers.SerializerMethodField()

    class Meta:
        model = GameUser
        fields = ['id', 'nickname', 'level', 'tier', 'ranking_score', 'created_at', 'win_rate']
    
    def get_win_rate(self, obj):
        """승룰 계산"""
        try:
            stats = obj.stats
            if stats.total_games > 0:
                return round((stats.wins / stats.total_games) * 100, 2)
        except:
            pass
        return 0.0
    
class GameUserDetailSerializer(serializers.ModelSerializer):
    """게임 유저 상세 정보"""
    stats = PlayerStatsSerializer(read_only=True)

    class Meta:
        model = GameUser
        fields = ['id', 'nickname', 'level', 'tier', 'ranking_score', 'created_at', 'stats']
        
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
# Create your models here.

class GameUser(models.Model):
    """게임 유저 기본 정보"""
    TIER_CHOICES = [
        ('BRONZE', '브론즈'),
        ('SILVER', '실버'),
        ('GOLD', '골드'),
        ('PLATINUM', '플래티넘'),
        ('DIAMOND', '다이아몬드'),
        ('MASTER', '마스터'),
        ('GRANDMASTER', '그랜드마스터'),
    ]

    nickname = models.CharField(max_length=50, unique = True, verbose_name = '닉네임')
    level = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name='레벨')
    tier = models.CharField(max_length = 20, choices=TIER_CHOICES, verbose_name = '티어')
    ranking_score = models.IntegerField(default = 0, verbose_name='랭킹 점수')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-ranking_score']
        verbose_name = '게임 유저'
        verbose_name_plural = '게임 유저들'
        indexes = [
            models.Index(fields = ['-ranking_score']),
            models.Index(fields = ['tier']),
        ]

    def __str__(self):
        return f'{self.nickname} ({self.tier})'

class Item(models.Model):
    """게임 아이템"""
    ITEM_TYPE_CHOICES= [
        ('WEAPON', '무기'),
        ('ARMOR', '방어구'),
        ('ACCESSORY', '악세서리'),
        ('CONSUMABLE', '소모품'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name = '아이템 이름')
    item_type = models.CharField(max_length = 20, choices=ITEM_TYPE_CHOICES, verbose_name = '아이템 타입')
    description = models.TextField(blank=True, verbose_name='설명')
    price = models.IntegerField(default = 0, verbose_name = '가격')

    class Meta:
        verbose_name = '아이템'
        verbose_name_plural = '아이템'
    
    def __str__(self):
        return self.name
    
class Skill(models.Model):
    """게임 스킬"""
    SKILL_TYPE_CHOICES = [
        ('ACTIVE', '액티브'),
        ('PASSIVE', '패시브'),
        ('ULTIMATE', '궁극기'),
    ]

    name = models.CharField(max_length=100, unique=True, verbose_name = '스킬 이름')
    skill_type = models.CharField(max_length = 20, choices = SKILL_TYPE_CHOICES, verbose_name='스킬 타입')
    description = models.TextField(blank=True, verbose_name = '설명')
    cooldown = models.IntegerField(default = 0, verbose_name = '쿨다운(초)')

    class Meta:
        verbose_name = '스킬'
        verbose_name_plural = '스킬'

    def __str__(self):
        return self.name

class PlayerStats(models.Model):
    """유저별 통계 정보"""
    user = models.OneToOneField(GameUser, on_delete=models.CASCADE, related_name='stats')
    total_games = models.IntegerField(default = 0, verbose_name = '총 게임 수')
    wins = models.IntegerField(default = 0, verbose_name = '승리')
    losses = models.IntegerField(default = 0, verbose_name = '패배')
    win_rate = models.FloatField(default=0.0, verbose_name='승률')
    play_time = models.IntegerField(default = 0, verbose_name='플레이 시간(분)')

    items = models.ManyToManyField(Item, through = 'ItemUsage', related_name='users')
    skills = models.ManyToManyField(Skill, through = 'SkillUsage', related_name='users')

    class Meta:
        verbose_name = '플레이어 통계'
        verbose_name_plural = '플레이어 통계'

    def calculate_win_rate(self):
        if self.total_games > 0:
            self.win_rate = (self.wins / self.total_games) * 100
        return self.win_rate
    
    def save(self, *args, **kwargs):
        self.calculate_win_rate()
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.user.nickname}의 통계'

class ItemUsage(models.Model):
    """아이템 사용 기록"""
    player_stats = models.ForeignKey(PlayerStats, on_delete=models.CASCADE, related_name='item_usages')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='item_usages')
    usage_count = models.IntegerField(default = 0, verbose_name = '사용 횟수')
    last_used = models.DateTimeField(auto_now=True, verbose_name='마지막 사용')

    class Meta:
        verbose_name = '아이템 사용 기록'
        verbose_name_plural = '아이템 사용 기록'
        unique_together = ['player_stats', 'item']
        indexes = [
            models.Index(fields = ['player_stats', 'usage_count']),
            models.Index(fields = ['item', 'usage_count']),
        ]

    def __str__(self):
        return f'{self.player_stats.user.nickname} - {self.item.name} ({self.usage_count}회)'

class SkillUsage(models.Model):
    """스킬 사용 기록 (중간 테이블)"""
    player_stats = models.ForeignKey(PlayerStats, on_delete=models.CASCADE, related_name='skill_usages')
    skill = models.ForeignKey(Skill, on_delete=models.CASCADE, related_name='skill_usages')
    usage_count = models.IntegerField(default = 0, verbose_name = '사용 횟수')
    last_used = models.DateTimeField(auto_now = True, verbose_name = '마지막 사용')

    class Meta:
        verbose_name = '스킬 사용 기록'
        verbose_name_plural = '스킬 사용 기록'
        unique_together = ['player_stats', 'skill']
        indexes = [
            models.Index(fields = ['player_stats', 'usage_count']),
            models.Index(fields = ['skill', 'usage_count'])
        ]

    def __str__(self):
        return f'{self.player_stats.user.nickname} - {self.skill.name} ({self.usage_count}회)'
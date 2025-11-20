from django.contrib import admin
from .models import GameUser, PlayerStats, Item, Skill
# Register your models here.

@admin.register(GameUser)
class GameUserAdmin(admin.ModelAdmin):
    list_display = ['nickname',  'level', 'tier', 'ranking_score', 'created_at']
    list_filter = ['tier', 'level']
    search_fields = ['nickname']
    ordering = ['-ranking_score']

@admin.register(PlayerStats)
class PlayerStatsAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_games', 'wins', 'losses', 'win_rate']
    list_filter = ['total_games']
    search_fields = ['user__nickname']
    readonly_fields = ['win_rate']

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'item_type', 'price']
    list_filter = ['item_type']
    search_fields = ['name']

@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'skill_type', 'cooldown']
    list_filter = ['skill_type']
    search_fields = ['name']


from django.core.management.base import BaseCommand
from django.db import transaction, connection
from django.conf import settings
import random
import time
from stats.models import GameUser, PlayerStats, Item, Skill, ItemUsage, SkillUsage
from faker import Faker

BATCH_SIZE = 500
USER_SIZE = 5000

class Command(BaseCommand):
    help = '테스트용 게임 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=USER_SIZE,
            help='생성할 유저 수 (기본값: USER_SIZE)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=BATCH_SIZE,
            help='bulk_create에 사용할 배치 크기 (기본값: BATCH_SIZE)'
        )
    
    def handle(self, *args, **options):
        fake = Faker('ko_KR')
        num_users = options['users']
        batch_size = options['batch_size']

        self.stdout.write('게임 데이터 생성을 시작합니다.')

        # 성능 측정 시작
        start_time = time.time()
        start_queries = len(connection.queries) if settings.DEBUG else 0

        # 아이템 생성
        self.stdout.write('아이템 생성 중.....')
        items = self.create_items()

        # 스킬 생성
        self.stdout.write('스킬 생성 중.....')
        skills = self.create_skills()

        # 유저 생성
        self.stdout.write(f'{num_users}명의 유저 생성 중 .....')
        created_users = self.create_users(fake, num_users, batch_size)

        # 아이템/스킬 사용 기록 생성
        self.stdout.write('아이템/스킬 사용 기록 생성 중.....')
        self.create_usage_records(created_users, items, skills, batch_size)

        # 성능 측정 종료
        end_time = time.time()
        end_queries = len(connection.queries) if settings.DEBUG else 0

        # 결과 출력
        elapsed_time = end_time - start_time
        total_queries = end_queries - start_queries if settings.DEBUG else 'N/A'

        self.stdout.write('\n' + '=' * 70)
        self.stdout.write(self.style.SUCCESS('성능 측정 결과'))
        self.stdout.write('=' * 70)
        self.stdout.write(f' 실행 시간: {elapsed_time:.2f}초')
        self.stdout.write(f' 생성된 유저: {num_users}명')
        self.stdout.write(f' 초당 처리: {num_users/elapsed_time:.1f}개/초')
        self.stdout.write(f' DB 쿼리 수: {total_queries}') 
        self.stdout.write(self.style.SUCCESS(f'성공적으로 {num_users}명의 유저 데이터를 생성했습니다.'))
        self.stdout.write('=' * 70)

    def create_items(self):
        """게임 데이터 생성"""
        item_data = [
        
            # 무기
            ('불타는 대검', 'WEAPON', '화염 속성 대검', 3500),
            ('서리한 활', 'WEAPON', '얼음 속성 활', 3200),
            ('천둥의 지팡이', 'WEAPON', '번개 속성 지팡이', 3800),
            ('암살자의 단검', 'WEAPON', '치명타 확률 증가', 2800),
            
            # 방어구
            ('강철 갑옷', 'ARMOR', '물리 방어력 증가', 2500),
            ('마법사 로브', 'ARMOR', '마법 방어력 증가', 2300),
            ('가시 갑옷', 'ARMOR', '반사 피해', 2800),
            
            # 액세서리
            ('힘의 반지', 'ACCESSORY', '공격력 증가', 1500),
            ('지혜의 목걸이', 'ACCESSORY', '마나 증가', 1400),
            ('민첩의 귀걸이', 'ACCESSORY', '공격속도 증가', 1600),
            
            # 소모품
            ('체력 물약', 'CONSUMABLE', 'HP 회복', 50),
            ('마나 물약', 'CONSUMABLE', 'MP 회복', 50),
        
        ]

        items = []
        for name, item_type, description, price in item_data:
            item, _ = Item.objects.get_or_create(
                name = name,
                defaults = {
                    'item_type' : item_type,
                    'description' : description,
                    'price' : price
                }
            )
            items.append(item)

        return items
    
    def create_skills(self):
        """게임 스킬 생성"""
        skill_data = [

            # 액티브 스킬
            ('화염구', 'ACTIVE', '적에게 화염 피해', 5),
            ('얼음 화살', 'ACTIVE', '적을 느리게 만듦', 4),
            ('번개 강타', 'ACTIVE', '범위 전기 피해', 8),
            ('치유', 'ACTIVE', '아군 HP 회복', 10),
            
            # 패시브 스킬
            ('강인함', 'PASSIVE', '최대 HP 20% 증가', 0),
            ('신속', 'PASSIVE', '이동속도 15% 증가', 0),
            ('집중', 'PASSIVE', '치명타 확률 10% 증가', 0),
            
            # 궁극기
            ('운석 낙하', 'ULTIMATE', '거대한 운석 소환', 120),
            ('시간 정지', 'ULTIMATE', '모든 적 행동 정지', 180),
            ('광폭화', 'ULTIMATE', '모든 능력치 2배 증가', 150),

        ]
        
        skills = []
        for name, skill_type, description, cooldown in skill_data:
            skill, _ = Skill.objects.get_or_create(
                name = name,
                defaults = {
                    'skill_type' : skill_type,
                    'description' : description,
                    'cooldown' : cooldown
                }
            )
            skills.append(skill)
        
        return skills
    
    @transaction.atomic
    def create_users(self, fake, num_users, batch_size):
        """게임 유저 생성"""
        tiers = [
            'BRONZE', 'SILVER',
            'GOLD', 'PLATINUM',
            'DIAMOND', 'MASTER',
            'GRANDMASTER'
        ]
        tier_weights = [30, 25, 20, 15, 7, 2.5, 0.5] # 티어별 분포

        existing_nicknames = set(GameUser.objects.values_list('nickname', flat=True))
        users = []

        for i in range(num_users):
            # 고유 닉네임 생성
            while True:
                nickname = f"{fake.first_name()}{random.randint(100, 9999)}"
                if nickname not in existing_nicknames:
                    existing_nicknames.add(nickname)
                    break

            # 티어 선택 (weight 적용)
            tier = random.choices(tiers, weights=tier_weights)[0]
            tier_index =tiers.index(tier)
            level = random.randint(max(1, tier_index * 10), min(100, (tier_index + 1) * 15))
            ranking_score = random.randint(tier_index * 1000, (tier_index + 1) * 1500)

            # GameUser 인스턴스만 생성 (DB 저장 X)
            user = GameUser(
                nickname = nickname,
                level = level,
                tier = tier,
                ranking_score = ranking_score
            )
            users.append(user)
        
        self.stdout.write('1단계 : GameUser 객체 메모리 생성 완료')

        # GameUser 일괄 삽입
        created_users = GameUser.objects.bulk_create(users, batch_size=batch_size)
        self.stdout.write(f'2단계: GameUser {num_users}명 DB 일괄 삽입 완료')

        # PlayerStats 객체 메모리 생성
        stats_create = []
        for user in created_users:
            total_games = random.randint(50, 500)
            wins = int(total_games * random.uniform(0.3, 0.7))
            losses = total_games - wins

            # PlayerStats 인스턴스 생성
            stats = PlayerStats(
                user = user,
                total_games=total_games,
                wins=wins,
                losses = losses,
                play_time=total_games * random.randint(20, 40)
            )
            stats_create.append(stats)
        
        self.stdout.write('3단계: PlayerStats 객체 메모리 생성 완료')
        
        PlayerStats.objects.bulk_create(stats_create, batch_size=batch_size)
        self.stdout.write('4단계: PlayerStats {num_users}개 DB 일괄 삽입 완료')
    
        return created_users
    
    @transaction.atomic
    def create_usage_records(self, users, items, skills, batch_size):
        """아이템/스킬 사용 기록 생성 (개선 버전)"""
        user_ids = [user.id for user in users]
        stats_dict = {stats.user_id: stats for stats in PlayerStats.objects.filter(user_id__in=user_ids)}
        
        # 티어 배수 사전 정의
        tier_multiplier = {
            'BRONZE': 1.0,
            'SILVER': 1.2,
            'GOLD': 1.5,
            'PLATINUM': 1.8,
            'DIAMOND': 2.2,
            'MASTER': 2.5,
            'GRANDMASTER': 3.0
        }
        
        # 아이템/스킬 ID 리스트 미리 추출
        item_ids = [item.id for item in items]
        skill_ids = [skill.id for skill in skills]
        
        item_usages = []
        skill_usages = []
        
        # 배치 단위로 처리 (메모리 최적화)
        for i in range(0, len(users), batch_size):
            batch_users = users[i:i + batch_size]
            batch_item_usages = []
            batch_skill_usages = []
            
            for user in batch_users:
                player_stats = stats_dict.get(user.id)
                if not player_stats:
                    continue
                
                multiplier = tier_multiplier.get(user.tier, 1.0)
                
                # 아이템 사용 기록
                num_items = random.randint(3, 7)
                selected_item_indices = random.sample(range(len(items)), min(num_items, len(items)))
                
                for idx in selected_item_indices:
                    usage_count = int(random.randint(10, 200) * multiplier)
                    batch_item_usages.append(
                        ItemUsage(
                            player_stats=player_stats,
                            item=items[idx],
                            usage_count=usage_count
                        )
                    )
                
                # 스킬 사용 기록
                num_skills = random.randint(3, 6)
                selected_skill_indices = random.sample(range(len(skills)), min(num_skills, len(skills)))
                
                for idx in selected_skill_indices:
                    usage_count = int(random.randint(20, 300) * multiplier)
                    batch_skill_usages.append(
                        SkillUsage(
                            player_stats=player_stats,
                            skill=skills[idx],
                            usage_count=usage_count
                        )
                    )
            
            # 배치 단위로 DB 삽입
            if batch_item_usages:
                ItemUsage.objects.bulk_create(batch_item_usages, batch_size=batch_size)
            if batch_skill_usages:
                SkillUsage.objects.bulk_create(batch_skill_usages, batch_size=batch_size)
            
            self.stdout.write(f'진행: {min(i + batch_size, len(users))}/{len(users)} 유저 처리 완료')
        
        self.stdout.write(self.style.SUCCESS('ItemUsage 및 SkillUsage 생성 완료'))
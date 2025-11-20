from django.core.management.base import BaseCommand
from django.db import transaction
import random
from stats.models import GameUser, PlayerStats, Item, Skill
from faker import Faker

class Command(BaseCommand):
    help = '테스트용 게임 데이터를 생성합니다'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            type=int,
            default=1000,
            help='생성할 유저 수 (기본값: 1000)'
        )
    
    def handle(self, *args, **options):
        fake = Faker('ko_KR')
        num_users = options['users']

        self.stdout.write('게임 데이터 생성을 시작합니다.')

        # 아이템 생성
        self.stdout.write('아이템 생성 중.....')
        items = self.create_items()

        # 스킬 생성
        self.stdout.write('스킬 생성 중.....')
        skills = self.create_skills()

        # 유저 생성
        self.stdout.write(f'{num_users}명의 유저 생성 중 .....')
        users = self.create_users(fake, num_users)

        self.stdout.write(self.style.SUCCESS(f'성공적으로 {num_users}명의 유저 데이터를 생성했습니다'))

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
    def create_users(self, fake, num_users):
        """게임 유저 생성"""
        tiers = [
            'BRONZE', 'SILVER',
            'GOLD', 'PLATINUM',
            'DIAMOND', 'MASTER',
            'GRANDMASTER'
        ]
        tier_weights = [30, 25, 20, 15, 7, 2.5, 0.5] # 티어별 분포

        users = []
        existing_nicknames = set(GameUser.objects.values_list('nickname', flat=True))

        for i in range(num_users):
            # 고유 닉네임 생성
            while True:
                nickname = f"{fake.first_name()}{random.randint(100, 9999)}"
                if nickname not in existing_nicknames:
                    existing_nicknames.add(nickname)
                    break

            # 티어 선택 (weight 적용)
            tier = random.choices(tiers, weights=tier_weights)[0]

            # 티어에 따른 레벨과 랭킹 점수 조정
            tier_index = tiers.index(tier)
            level = random.randint(
                max(1, tier_index * 10),
                min(100, (tier_index + 1) * 15)
            )
            ranking_score = random.randint(
                tier_index * 1000,
                (tier_index + 1) * 1500
            )

            user = GameUser.objects.create(
                nickname=nickname,
                level=level,
                tier=tier,
                ranking_score=ranking_score
            )

            # PlayerStats 생성
            total_games = random.randint(50, 500)
            wins = int(total_games * random.uniform(0.3, 0.7))
            losses = total_games - wins

            PlayerStats.objects.create(
                user=user,
                total_games=total_games,
                wins=wins,
                losses=losses,
                play_time=total_games * random.randint(20, 40)
            )

            users.append(user)

            if(i + 1) % 10 == 0:
                self.stdout.write(f'생성 완료: {i + 1}/{num_users}')

        return users
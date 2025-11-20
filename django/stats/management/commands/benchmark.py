import time
import matplotlib.pyplot as plt
from django.core.management.base import BaseCommand
from django.db.models import Count
from stats.models import Item, ItemUsage, PlayerStats, GameUser
import random

class Command(BaseCommand):
    help = 'Python 연산 vs DB Aggregation 성능 비교 및 시각화'

    def handle(self, *args, **kwargs):
        self.stdout.write("데이터 확인 중...")
        
        # 1. 데이터가 너무 적으면 차이가 안 나므로 더미 데이터 생성 (없을 경우)
        if Item.objects.count() < 1000:
            self.stdout.write("테스트를 위한 대량의 더미 데이터를 생성합니다... (시간이 좀 걸립니다)")
            self.create_dummy_data()
        else:
            self.stdout.write(f"기존 데이터 사용 (Items: {Item.objects.count()}개)")

        self.stdout.write("-" * 50)
        self.stdout.write("벤치마크 시작!")

        # --- [CASE 1] 비효율적인 방식 (Python Level) ---
        self.stdout.write("1. Python 레벨 연산 (Sorted + Loop) 실행 중...")
        start_time = time.time()
        
        # 모든 객체를 메모리에 가져옴
        items = Item.objects.all()
        # Python 리스트로 변환 후, lambda를 통해 각 아이템마다 count() 쿼리 발생 (N+1 문제 재현)
        # 주의: 이 방식은 아이템 1000개면 1001번의 쿼리가 나갑니다.
        sorted_items = sorted(items, key=lambda x: x.item_usages.count(), reverse=True)
        
        python_duration = time.time() - start_time
        self.stdout.write(f"   -> 소요 시간: {python_duration:.4f}초")

        # --- [CASE 2] 효율적인 방식 (DB Aggregation) ---
        self.stdout.write("2. DB Aggregation (Annotate) 실행 중...")
        start_time = time.time()
        
        # DB에서 계산을 끝내고 결과만 가져옴 (쿼리 1방)
        queryset = Item.objects.annotate(
            usage_count=Count('item_usages')
        ).order_by('-usage_count')
        # 평가를 강제하기 위해 list로 변환
        result_list = list(queryset)
        
        db_duration = time.time() - start_time
        self.stdout.write(f"   -> 소요 시간: {db_duration:.4f}초")

        # --- [결과 시각화] ---
        self.stdout.write("-" * 50)
        self.create_graph(python_duration, db_duration)
        
        ratio = python_duration / db_duration
        self.stdout.write(self.style.SUCCESS(f"결과: DB 연산이 Python 연산보다 약 {ratio:.1f}배 빠릅니다!"))
        self.stdout.write(self.style.SUCCESS("결과 그래프가 'benchmark_result.png'로 저장되었습니다."))

    def create_graph(self, py_time, db_time):
        """matplotlib을 이용해 비교 그래프 생성"""
        methods = ['Python Logic\n(N+1 Problem)', 'DB Aggregation\n(Annotate)']
        times = [py_time, db_time]
        colors = ['#ff9999', '#66b3ff'] # 빨강(느림), 파랑(빠름)

        plt.figure(figsize=(10, 6))
        bars = plt.bar(methods, times, color=colors)
        
        # 그래프 꾸미기
        plt.title('Performance Comparison: Python vs DB Aggregation', fontsize=16)
        plt.ylabel('Execution Time (Seconds)', fontsize=12)
        
        # 막대 위에 시간 표시
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2.0, height,
                     f'{height:.4f} sec', ha='center', va='bottom', fontsize=12, fontweight='bold')

        plt.savefig('benchmark_result.png')
        plt.close()

    def create_dummy_data(self):
        """테스트용 데이터 대량 생성"""
        # 아이템 1000개 생성
        items = [Item(name=f'Test Item {i}', item_type='sword') for i in range(1000)]
        Item.objects.bulk_create(items)
        
        # 유저 및 스탯 생성
        user = GameUser.objects.create(user='bench_tester', tier='GOLD')
        stats = PlayerStats.objects.create(user=user)
        
        # 아이템 사용 기록 20,000개 생성 (랜덤 분배)
        all_items = list(Item.objects.all())
        usages = []
        for _ in range(20000):
            usages.append(ItemUsage(player_stats=stats, item=random.choice(all_items)))
        
        ItemUsage.objects.bulk_create(usages)
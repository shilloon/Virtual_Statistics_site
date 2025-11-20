from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.conf import settings
from django.db import connection
import time
from stats.models import GameUser, PlayerStats

class Command(BaseCommand):
    help = '두 방식의 성능을 비교합니다'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=5000, help='테스트할 유저 수')
        parser.add_argument('--batch-size', type=int, default=500, help='bulk_create에 사용할 batch_size')

    def handle(self, *args, **options):
        num_users = options['users']
        batch_size = options['batch_size']

        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.WARNING('Django ORM 성능 비교 테스트'))
        self.stdout.write('=' * 80)
        self.stdout.write(f'테스트 규모: {num_users}명의 유저 생성')
        self.stdout.write(f'비교 커맨드: generate_fake_data_old_way vs. generate_fake_data_bulk_version')
        self.stdout.write('=' * 80 + '\n')

        results = {}

        # 기존 방식 테스트
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 1] 기존 방식 (하나씩 create) 시작'))
        self.stdout.write('-' * 80)

        # 기존 데이터 삭제
        GameUser.objects.all().delete()

        start_time = time.time()
        start_queries = len(connection.queries) if settings.DEBUG else 0
        call_command('generate_fake_data_old_way', users=num_users)
        end_time = time.time()
        end_queries = len(connection.queries) if settings.DEBUG else 0

        old_way_time = end_time - start_time
        old_way_count = GameUser.objects.count()
        old_queries = end_queries - start_queries if settings.DEBUG else 'N/A'

        results['old'] = {
            'time' : old_way_time,
            'count' : old_way_count,
            'per_second': old_way_count / old_way_time if old_way_time > 0 else 0,
            'queries' : old_queries
        }

        #  개선된 방식 테스트
        self.stdout.write(self.style.HTTP_INFO('\n[TEST 2] 개선된 방식 (bulk_create) 시작'))
        self.stdout.write('-' * 80)
        
        # 기존 데이터 삭제
        GameUser.objects.all().delete()

        start_time = time.time()
        start_queries = len(connection.queries) if settings.DEBUG else 0
        call_command('generate_fake_data_bulk_version', users=num_users, batch_size=batch_size)
        end_time = time.time()
        end_queries = len(connection.queries) if settings.DEBUG else 0

        bulk_way_time = end_time - start_time
        bulk_way_count = GameUser.objects.count()
        bulk_queries = end_queries - start_queries if settings.DEBUG else 'N/A'

        results['bulk'] = {

            'time': bulk_way_time,
            'count': bulk_way_count,
            'per_second' : bulk_way_count / bulk_way_time if bulk_way_time > 0 else 0,
            'queries' : bulk_queries

        }

        # 최종 결과 비교
        self.print_final_comparison(results, num_users)


    def print_final_comparison(self, results, num_users):
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(self.style.SUCCESS(' 최종 비교 결과'))
        self.stdout.write('=' * 80)
        
        # 성능 향상 계산
        if results['old']['time'] > 0 and results['bulk']['time'] > 0:
            improvement = results['old']['time'] / results['bulk']['time']
            time_saved = results['old']['time'] - results['bulk']['time']
            
            # 테이블 형식 출력
            data = [
                ['방식', ' 실행 시간 (초)', ' 처리량 (개/초)', ' 쿼리 수'],
                [' 기존 (create)', f'{results["old"]["time"]:.3f}', f'{results["old"]["per_second"]:.1f}', f'{results["old"]["queries"]}'],
                [' Bulk (bulk_create)', f'{results["bulk"]["time"]:.3f}', f'{results["bulk"]["per_second"]:.1f}', f'{results["bulk"]["queries"]}']
            ]
            
            # 테이블 출력 로직 (간단화)
            col_widths = [max(len(str(item)) for item in col) for col in zip(*data)]
            format_str = ' | '.join(['{:<' + str(width) + '}' for width in col_widths])
            
            self.stdout.write('\n' + format_str.format(*data[0]))
            self.stdout.write('-' * 80)
            self.stdout.write(format_str.format(*data[1]))
            self.stdout.write(format_str.format(*data[2]))
            self.stdout.write('-' * 80)
            
            # 요약
            self.stdout.write(f'\n' + self.style.WARNING(' 성능 향상 요약:'))
            self.stdout.write(f'  **Bulk Create 방식**이 기존 방식 대비 **{improvement:.1f}배** 빠름!')
            self.stdout.write(f'  총 **{time_saved:.3f}초** 절약 (유저 {num_users}명 기준)')

        else:
            self.stdout.write(self.style.ERROR("시간 측정이 제대로 되지 않았습니다. 유저 수를 늘려보세요."))
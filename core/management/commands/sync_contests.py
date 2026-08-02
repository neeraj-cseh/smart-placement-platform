import requests
from django.core.management.base import BaseCommand
from django.utils.dateparse import parse_datetime
from django.utils import timezone
from core.models import CodingContest

class Command(BaseCommand):
    help = 'Fetches external coding contests from Kontests API and updates the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.NOTICE('Starting contest sync...'))
        
        try:
            response = requests.get('https://kontests.net/api/v1/all', timeout=5)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Failed to fetch from Kontests API: {e}. Falling back to dynamic generator for demonstration...'))
            now = timezone.now()
            data = [
                {
                    "name": "LeetCode Weekly Contest (Auto-Sync)",
                    "url": "https://leetcode.com/contest/",
                    "start_time": (now + timezone.timedelta(days=2)).isoformat(),
                    "end_time": (now + timezone.timedelta(days=2, hours=1, minutes=30)).isoformat(),
                    "duration": "5400",
                    "site": "LeetCode"
                },
                {
                    "name": "Codeforces Round (Div. 2) Auto",
                    "url": "https://codeforces.com/contests",
                    "start_time": (now + timezone.timedelta(hours=5)).isoformat(),
                    "end_time": (now + timezone.timedelta(hours=7)).isoformat(),
                    "duration": "7200",
                    "site": "CodeForces"
                },
                {
                    "name": "HackerRank Month of Code",
                    "url": "https://www.hackerrank.com/contests",
                    "start_time": (now - timezone.timedelta(days=1)).isoformat(),
                    "end_time": (now + timezone.timedelta(days=6)).isoformat(),
                    "duration": "604800",
                    "site": "HackerRank"
                }
            ]

        supported_platforms = {
            'LeetCode': 'LeetCode',
            'CodeForces': 'Codeforces',
            'CodeForces::Gym': 'Codeforces',
            'HackerRank': 'HackerRank',
            'AtCoder': 'AtCoder',
            'CodeChef': 'CodeChef'
        }

        # Keep track of updated/created ones to potentially clear out dead ones
        processed_urls = []
        created_count = 0
        updated_count = 0

        for item in data:
            site = item.get('site')
            if site not in supported_platforms:
                continue

            platform_name = supported_platforms[site]
            name = item.get('name')
            url = item.get('url')
            
            # Kontests API provides times in ISO format but sometimes they are invalid or empty
            start_time_str = item.get('start_time')
            end_time_str = item.get('end_time')
            
            try:
                start_time = parse_datetime(start_time_str)
                end_time = parse_datetime(end_time_str)
                
                # If naive, assume UTC
                if start_time and timezone.is_naive(start_time):
                    start_time = timezone.make_aware(start_time, timezone.utc)
                if end_time and timezone.is_naive(end_time):
                    end_time = timezone.make_aware(end_time, timezone.utc)
            except Exception:
                continue
                
            if not start_time or not end_time:
                continue

            duration_seconds = float(item.get('duration', 0))
            duration_minutes = int(duration_seconds / 60)
            
            # Don't add extremely long ongoing contests (like permanent practice ones > 30 days)
            if duration_minutes > 43200:
                continue

            # Update or create
            contest, created = CodingContest.objects.update_or_create(
                external_url=url,
                defaults={
                    'title': name,
                    'platform': platform_name,
                    'start_time': start_time,
                    'end_time': end_time,
                    'duration_minutes': duration_minutes,
                    'description': f"Global {platform_name} competition. Follow the link to register and participate.",
                    'is_active': True
                }
            )
            
            processed_urls.append(url)
            if created:
                created_count += 1
            else:
                updated_count += 1

        # Optional: Archive past external contests that are older than 30 days
        thirty_days_ago = timezone.now() - timezone.timedelta(days=30)
        archived_count = CodingContest.objects.filter(
            external_url__isnull=False, 
            end_time__lt=thirty_days_ago
        ).delete()[0]

        self.stdout.write(self.style.SUCCESS(
            f'Sync complete! Created: {created_count}, Updated: {updated_count}, Archived: {archived_count}'
        ))

import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingContest

def seed_external_contests():
    print("Seeding external marketplace contests...")
    
    # Clear existing
    CodingContest.objects.all().delete()
    
    now = timezone.now()
    
    contests = [
        {
            "title": "LeetCode Weekly Contest 400",
            "description": "Compete in the milestone LeetCode Weekly Contest 400! Solve 4 algorithmic challenges.",
            "start_time": now + timedelta(days=2),
            "end_time": now + timedelta(days=2, hours=1, minutes=30),
            "duration_minutes": 90,
            "platform": "LeetCode",
            "external_url": "https://leetcode.com/contest/"
        },
        {
            "title": "Codeforces Round 950 (Div. 2)",
            "description": "Codeforces rating round for Division 2 participants.",
            "start_time": now + timedelta(hours=5),
            "end_time": now + timedelta(hours=7),
            "duration_minutes": 120,
            "platform": "Codeforces",
            "external_url": "https://codeforces.com/contests"
        },
        {
            "title": "HackerRank Week of Code 38",
            "description": "A week-long coding marathon with one new challenge each day.",
            "start_time": now - timedelta(days=1),
            "end_time": now + timedelta(days=6),
            "duration_minutes": 10080, # 7 days
            "platform": "HackerRank",
            "external_url": "https://www.hackerrank.com/contests"
        },
        {
            "title": "PrepSmart Internal Qualifier",
            "description": "Solve advanced algorithm questions to qualify for the PrepSmart Elite tier.",
            "start_time": now + timedelta(days=5),
            "end_time": now + timedelta(days=5, hours=2),
            "duration_minutes": 120,
            "platform": "PrepSmart",
            "external_url": None
        },
        {
            "title": "LeetCode Biweekly Contest 131",
            "description": "Past biweekly contest on LeetCode.",
            "start_time": now - timedelta(days=4),
            "end_time": now - timedelta(days=4, hours=1, minutes=30),
            "duration_minutes": 90,
            "platform": "LeetCode",
            "external_url": "https://leetcode.com/contest/past/"
        },
        {
            "title": "AtCoder Beginner Contest 350",
            "description": "Great for beginners to get into competitive programming.",
            "start_time": now - timedelta(days=10),
            "end_time": now - timedelta(days=10, hours=1, minutes=40),
            "duration_minutes": 100,
            "platform": "AtCoder",
            "external_url": "https://atcoder.jp/contests/"
        }
    ]
    
    for c_data in contests:
        CodingContest.objects.create(**c_data)
        
    print("Contests seeded successfully!")

if __name__ == '__main__':
    seed_external_contests()

import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingContest, CodingProblem

def seed():
    CodingContest.objects.all().delete()
    
    now = timezone.now()
    
    # -------------------------------------
    # ONGOING CONTESTS (Start in the past, End in the future)
    # -------------------------------------
    CodingContest.objects.create(
        title="LeetCode Weekly Contest 410",
        description="Join thousands of developers in the official LeetCode Weekly Contest.",
        start_time=now - timedelta(minutes=45),
        end_time=now + timedelta(minutes=45),
        duration_minutes=90,
        is_active=True,
        platform="LeetCode",
        external_url="https://leetcode.com/contest/"
    )
    
    CodingContest.objects.create(
        title="PrepSmart Internal Qualifier",
        description="Solve 4 algorithmic challenges to qualify for the next interview sprint.",
        start_time=now - timedelta(minutes=10),
        end_time=now + timedelta(minutes=110),
        duration_minutes=120,
        is_active=True,
        platform="PrepSmart"
    )

    # -------------------------------------
    # UPCOMING CONTESTS (Start in the future)
    # -------------------------------------
    CodingContest.objects.create(
        title="Codeforces Round 950 (Div. 2)",
        description="Rated for Div. 2 participants. 6 problems, 2 hours.",
        start_time=now + timedelta(seconds=15), # Starts very soon to test the UI shift!
        end_time=now + timedelta(hours=2),
        duration_minutes=120,
        is_active=True,
        platform="Codeforces",
        external_url="https://codeforces.com/contests"
    )
    
    CodingContest.objects.create(
        title="LeetCode Biweekly Contest 135",
        description="Compete globally in the biweekly contest.",
        start_time=now + timedelta(days=2, hours=10),
        end_time=now + timedelta(days=2, hours=11, minutes=30),
        duration_minutes=90,
        is_active=True,
        platform="LeetCode",
        external_url="https://leetcode.com/contest/"
    )
    
    CodingContest.objects.create(
        title="PrepSmart Weekly Sprint",
        description="University-wide coding sprint matching top product company coding patterns.",
        start_time=now + timedelta(days=5),
        end_time=now + timedelta(days=5, hours=2),
        duration_minutes=120,
        is_active=True,
        platform="PrepSmart"
    )

    # -------------------------------------
    # PAST CONTESTS (End in the past)
    # -------------------------------------
    for i in range(1, 6):
        CodingContest.objects.create(
            title=f"LeetCode Weekly Contest {410 - i}",
            description="Past LeetCode contest.",
            start_time=now - timedelta(days=7 * i, hours=1),
            end_time=now - timedelta(days=7 * i, minutes=30),
            duration_minutes=90,
            is_active=True,
            platform="LeetCode",
            external_url="https://leetcode.com/contest/"
        )

    for i in range(1, 3):
        CodingContest.objects.create(
            title=f"PrepSmart Sprint #{48 - i}",
            description="Past internal sprint.",
            start_time=now - timedelta(days=14 * i, hours=2),
            end_time=now - timedelta(days=14 * i),
            duration_minutes=120,
            is_active=True,
            platform="PrepSmart"
        )
        
    print(f"Seeded {CodingContest.objects.count()} contests successfully!")

if __name__ == "__main__":
    seed()

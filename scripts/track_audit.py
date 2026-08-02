import django, os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from core.models import Topic, Track

print("=== TRACK -> TOPICS MAPPING ===")
for track in Track.objects.all():
    topics = Topic.objects.filter(track=track, is_active=True)
    print("Track: %s (%d topics)" % (track.name, topics.count()))
    for t in topics:
        print("  slug=%s" % t.slug)

print()
print("=== ALL ACTIVE SLUGS ===")
for t in Topic.objects.filter(is_active=True).order_by('slug'):
    print("  %s" % t.slug)

print()
print("Total: %d" % Topic.objects.filter(is_active=True).count())

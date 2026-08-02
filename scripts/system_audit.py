"""
Full system audit — corrected for custom User model.
"""
import django, os, sys, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import Topic, TopicSection, Question, TopicRevision, TopicVisualization

factory = RequestFactory()
u = User.objects.first()
if not u:
    print("CRITICAL: No users in database")
    sys.exit(1)
print(f"Using user: {u.email}")

# ── 1. Journey API ───────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("1. JOURNEY API")
print("=" * 60)

from core.views import PrepTopicJourneyView
req = factory.get('/prep/topic-journey/')
req.user = u

all_journey_slugs = []
try:
    view = PrepTopicJourneyView()
    view.request = req
    resp = view.get(req)
    data = json.loads(resp.content)
    for track in data.get('tracks', []):
        tname = track.get('name', 'unknown')
        nodes = track.get('nodes', [])
        print(f"\n  Track: {tname} ({len(nodes)} topics)")
        for node in nodes:
            slug = node.get('slug', '')
            all_journey_slugs.append(slug)
            exists = Topic.objects.filter(slug=slug, is_active=True).exists()
            status = "OK  " if exists else "MISS"
            print(f"    [{status}] {slug}")
except Exception as e:
    print(f"  JOURNEY API ERROR: {e}")
    import traceback
    traceback.print_exc()

# ── 2. Topic Detail API ──────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("2. TOPIC DETAIL API")
print("=" * 60)

from core.views import PrepTopicDetailView

broken = []
working = []

for slug in all_journey_slugs:
    req2 = factory.get(f'/prep/topic/{slug}/')
    req2.user = u
    try:
        view2 = PrepTopicDetailView()
        view2.request = req2
        resp2 = view2.get(req2, slug=slug)
        status = resp2.status_code
        d = json.loads(resp2.content)
        if status == 200:
            secs = len(d.get('sections', []))
            qs = len(d.get('questions', []))
            has_vis = 'visualization' in d and d['visualization']
            has_rev = 'revision' in d and d['revision']
            working.append(slug)
            flags = []
            if secs == 0: flags.append("!NO_SECS")
            if qs == 0:   flags.append("!NO_QS")
            if not has_vis: flags.append("!NO_VIS")
            if not has_rev: flags.append("!NO_REV")
            flag_str = " ".join(flags) if flags else ""
            print(f"  OK   {slug:45} secs={secs} qs={qs} {flag_str}")
        else:
            broken.append((slug, status, d.get('error', str(d))[:60]))
            print(f"  FAIL {slug:45} [{status}] {d.get('error', str(d))[:60]}")
    except Exception as e:
        broken.append((slug, 'EXC', str(e)[:80]))
        print(f"  ERR  {slug:45} {str(e)[:80]}")

# ── 3. frontend API client setup ─────────────────────────────────────────────
print("\n" + "=" * 60)
print("3. FRONTEND API CLIENT CHECK")
print("=" * 60)

api_client_path = "frontend-react/src/api/client.js"
if os.path.exists(api_client_path):
    with open(api_client_path) as f:
        content = f.read()
    if 'baseURL' in content or 'BASE_URL' in content or 'localhost' in content:
        print("  OK — api/client.js exists with base URL")
    else:
        print("  WARN — api/client.js exists but no clear base URL")
else:
    print(f"  FAIL — {api_client_path} NOT FOUND")

# ── 4. Data completeness ─────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("4. DATABASE COMPLETENESS (all active topics)")
print("=" * 60)

all_topics = Topic.objects.filter(is_active=True).order_by('slug')
total = all_topics.count()
no_sections = 0
no_questions = 0
no_revision = 0
no_visualizer = 0

for t in all_topics:
    secs = TopicSection.objects.filter(topic=t).count()
    qs = Question.objects.filter(topic=t).count()
    has_rev = TopicRevision.objects.filter(topic=t).exists()
    has_vis = TopicVisualization.objects.filter(topic=t).exists()
    if secs == 0: no_sections += 1
    if qs == 0: no_questions += 1
    if not has_rev: no_revision += 1
    if not has_vis: no_visualizer += 1

print(f"  Total active topics:    {total}")
print(f"  Topics with 0 sections: {no_sections}")
print(f"  Topics with 0 questions:{no_questions}")
print(f"  Topics with no revision:{no_revision}")
print(f"  Topics with no visualiz:{no_visualizer}")

# ── Summary ──────────────────────────────────────────────────────────────────
print("\n" + "=" * 60)
print("AUDIT SUMMARY")
print("=" * 60)
print(f"  Journey slugs:     {len(all_journey_slugs)}")
print(f"  Working APIs:      {len(working)}")
print(f"  BROKEN APIs:       {len(broken)}")
if broken:
    print("\n  BROKEN ENDPOINTS:")
    for s, code, msg in broken:
        print(f"    [{code}] /prep/topic/{s}/ — {msg}")
print()
if len(broken) == 0:
    print("  >>> ALL TOPIC APIs WORKING <<<")
else:
    print(f"  >>> {len(broken)} BROKEN ENDPOINTS NEED FIXING <<<")

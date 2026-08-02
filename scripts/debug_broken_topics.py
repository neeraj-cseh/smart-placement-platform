import django, os, sys, traceback
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
from core.models import Topic, TopicSection, TopicVisualization, TopicRevision, Question, CodingProblem, CodeSubmission, UserTopicProgress, TopicDependency
from django.db.models import Count, Q

u = User.objects.first()
print("User:", u.email)

broken_slugs = ['coding-interview-strategy', 'company-research', 'time-speed-distance']

for slug in broken_slugs:
    print("\n=== Testing:", slug, "===")
    try:
        topic = Topic.objects.get(slug=slug, is_active=True)
        print("  Topic found:", topic.name)
        
        # 1. Sections
        sections = list(TopicSection.objects.filter(topic=topic).order_by('order', 'id'))
        print("  Sections:", len(sections))
        
        # 2. Visualization
        vis_data = None
        if hasattr(topic, 'visualization'):
            vis = topic.visualization
            vis_data = {"id": vis.id, "title": vis.title, "visualization_type": vis.visualization_type, "config_data": vis.config_data}
        print("  Visualization:", bool(vis_data))
        
        # 3. Revision
        rev_data = None
        if hasattr(topic, 'revision'):
            rev = topic.revision
            rev_data = {"id": rev.id, "key_takeaways": rev.key_takeaways, "cheat_sheet_markdown": rev.cheat_sheet_markdown}
        print("  Revision:", bool(rev_data))
        
        # 4. Questions
        questions = list(Question.objects.filter(topic=topic).order_by('id'))
        print("  Questions:", len(questions))
        
        # 5. Coding problems (the suspected crash point)
        from core.views import ensure_coding_problems_mock_data
        ensure_coding_problems_mock_data()
        problems = CodingProblem.objects.all()
        topic_name = topic.name.lower()
        print("  Topic name:", topic_name)
        
        matched_problems = []
        solved_ids = CodeSubmission.objects.filter(user=u, status="Accepted").values_list("problem_id", flat=True).distinct()
        
        for p in problems:
            is_match = False
            for t_tag in p.topics:
                if t_tag.lower() in topic_name or topic_name in t_tag.lower():
                    is_match = True
                    break
            if is_match:
                matched_problems.append(p.title)
        
        print("  Matched problems:", len(matched_problems))
        
        # 6. Dependencies
        prereqs = TopicDependency.objects.filter(topic=topic)
        print("  Prereqs:", prereqs.count())
        
        print("  ALL OK")
        
    except Exception as e:
        print("  CRASH:", type(e).__name__, str(e))
        traceback.print_exc()

print("\n=== TEST COMPLETE ===")

import django, os, sys, traceback, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

# Test with each user
for email in ['student@prepsmart.dev', 'neeraj.2002@gmail.com', 'admin@gmail.com']:
    u = User.objects.filter(email=email).first()
    if not u:
        continue
    print("=== User:", email, "===")
    
    from core.bootstrap import ensure_user_preparation_data
    try:
        ensure_user_preparation_data(u)
        print("  ensure_user_preparation_data: OK")
    except Exception as e:
        print("  ensure_user_preparation_data CRASH:", e)
        traceback.print_exc()
        continue
    
    # Test ai-context view
    from core.models import Topic, TopicSection, UserTopicProgress, UserAnswer, TopicDependency, CodeSubmission
    from django.db.models import Count, Q
    
    for slug in ['number-systems', 'coding-interview-strategy', 'company-research']:
        try:
            topic = Topic.objects.get(slug=slug)
            
            # The exact ai-context logic
            completed_topics = Topic.objects.filter(
                user_progress__user=u,
                user_progress__is_completed=True
            ).values_list('name', flat=True)
            
            prereqs = TopicDependency.objects.filter(topic=topic)
            
            weaknesses = []
            low_accuracy = UserAnswer.objects.filter(user=u).values(
                'question__topic__name'
            ).annotate(
                total=Count('id'),
                correct=Count('id', filter=Q(is_correct=True))
            )
            for lat in low_accuracy:
                total = lat['total']
                correct = lat['correct']
                accuracy = (correct / total) if total else 1.0
                if accuracy < 0.6:
                    weaknesses.append(lat['question__topic__name'])
            
            # The problematic query
            failed_subs = CodeSubmission.objects.filter(user=u).exclude(status="Accepted").values(
                'problem__topics'
            ).annotate(count=Count('id'))
            for fs in failed_subs:
                tags = fs['problem__topics']
                if isinstance(tags, list):
                    for tag in tags:
                        if tag not in weaknesses:
                            weaknesses.append(tag)
            
            print("  ai-context [%s]: OK (weaknesses=%d)" % (slug, len(weaknesses)))
            
        except Exception as e:
            print("  ai-context [%s] CRASH: %s" % (slug, e))
            traceback.print_exc()
    
    # Test journey view for this user
    try:
        from core.models import Track, Question as Q_model
        from django.db.models import Count
        tracks = Track.objects.all()
        progress_lookup = {p.topic_id: p for p in UserTopicProgress.objects.filter(user=u)}
        
        for track in tracks:
            topics = list(track.topics.filter(is_active=True).order_by('id'))
            for topic in topics:
                # Check the order field
                order_val = getattr(topic, 'order', None)
        print("  journey queries: OK")
    except Exception as e:
        print("  journey CRASH:", e)
        traceback.print_exc()

print("\nDone")

import os
import sys
import django
import json

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from core.models import TopicVisualization, Topic

def run():
    print("Migrating visualizer data to config_data JSON...")

    # 1. Sliding Window
    sw_vis = TopicVisualization.objects.filter(visualization_type='sliding-window')
    sw_config = {
        "topic": "Sliding Window",
        "seeded": True,
        "array": [2, 1, 5, 1, 3, 2],
        "k": 3,
        "steps": [
            {"left": 0, "right": 2, "sum": 8, "maxSum": 8, "desc": "Initialize window of size K=3. Sum of [2, 1, 5] = 8."},
            {"left": 1, "right": 3, "sum": 7, "maxSum": 8, "desc": "Slide right: subtract idx 0 (2), add idx 3 (1). Sum of [1, 5, 1] = 7."},
            {"left": 2, "right": 4, "sum": 9, "maxSum": 9, "desc": "Slide right: subtract idx 1 (1), add idx 4 (3). Sum of [5, 1, 3] = 9. New MAX!"},
            {"left": 3, "right": 5, "sum": 6, "maxSum": 9, "desc": "Slide right: subtract idx 2 (5), add idx 5 (2). Sum of [1, 3, 2] = 6."},
            {"left": 3, "right": 5, "sum": 6, "maxSum": 9, "desc": "✅ Done! Maximum sum subarray of size 3 is 9."}
        ]
    }
    for vis in sw_vis:
        vis.config_data = sw_config
        vis.save()

    # 2. Linked List Cycle
    ll_vis = TopicVisualization.objects.filter(visualization_type='linked-list-cycle')
    ll_config = {
        "topic": "Linked List Cycle",
        "seeded": True,
        "nodes": [3, 2, 0, -4],
        "steps": [
            {"slowIdx": 0, "fastIdx": 0, "desc": "Slow & Fast both start at head (val: 3)."},
            {"slowIdx": 1, "fastIdx": 2, "desc": "Slow → node 1 (val: 2). Fast → node 2 (val: 0). Two steps."},
            {"slowIdx": 2, "fastIdx": 1, "desc": "Slow → node 2 (val: 0). Fast wraps cycle → node 1 (val: 2)."},
            {"slowIdx": 3, "fastIdx": 3, "desc": "✅ MEET at node 3 (val: -4). Cycle confirmed! Floyd's algorithm works."}
        ]
    }
    for vis in ll_vis:
        vis.config_data = ll_config
        vis.save()

    # 3. Graph DFS
    graph_vis = TopicVisualization.objects.filter(visualization_type='graph-dfs')
    graph_config = {
        "topic": "Graph DFS",
        "seeded": True,
        "nodes": ["A", "B", "C", "D", "E"],
        "steps": [
            {"active": "A", "visited": ["A"], "structure": ["B", "C"], "desc": "Visit A. Push neighbors B, C to stack."},
            {"active": "C", "visited": ["A", "C"], "structure": ["B", "E"], "desc": "Pop C (LIFO). Visit C. Push E."},
            {"active": "E", "visited": ["A", "C", "E"], "structure": ["B"], "desc": "Pop E. Visit E. No new neighbors."},
            {"active": "B", "visited": ["A", "C", "E", "B"], "structure": ["D"], "desc": "Pop B. Visit B. Push D."},
            {"active": "D", "visited": ["A", "C", "E", "B", "D"], "structure": [], "desc": "✅ Pop D. Visit D. Stack empty — DFS complete!"}
        ]
    }
    for vis in graph_vis:
        vis.config_data = graph_config
        vis.save()

    # 4. Logical Puzzles
    logical_vis = TopicVisualization.objects.filter(visualization_type='logical-puzzle')
    logical_config = {
        "topic": "Logical Puzzles",
        "seeded": True,
        "positions": ["1st", "2nd", "3rd", "4th", "5th"],
        "people": ["Alice", "Bob", "Carol", "Dave", "Eve"],
        "colors": ["#3b82f6", "#8b5cf6", "#10b981", "#fb923c", "#ef4444"],
        "finalOrder": [2, 0, 4, 1, 3],
        "clues": [
            "Clue 1: Alice is not in position 1 or 5.",
            "Clue 2: Bob is immediately after Alice.",
            "Clue 3: Carol is before Dave.",
            "Clue 4: Eve sits exactly in the middle (3rd).",
            "Solution: Carol → Alice → Eve → Bob → Dave ✅"
        ]
    }
    for vis in logical_vis:
        vis.config_data = logical_config
        vis.save()
    
    # 5. Aptitude Profit
    apt_vis = TopicVisualization.objects.filter(visualization_type='aptitude-profit')
    for vis in apt_vis:
        vis.config_data = {"topic": "Profit & Loss", "seeded": True}
        vis.save()

    # 6. Generic Concept Fallbacks
    generic_vis = TopicVisualization.objects.filter(visualization_type='generic')
    for vis in generic_vis:
        steps = []
        # Try to parse from the "learn" section of the topic
        learn_sec = vis.topic.sections.filter(section_type='learn').first()
        if learn_sec and learn_sec.content_markdown:
            lines = [l.strip() for l in learn_sec.content_markdown.split('\\n') if l.strip().startswith('- ') or l.strip().startswith('* ') or l.strip()[:2].isdigit()]
            for l in lines[:5]:
                clean_l = l.lstrip('-* 1234567890.').strip()
                if clean_l:
                    steps.append(clean_l)
        
        if not steps:
            steps = [
                'Identify the core pattern or constraint',
                'Choose the optimal data structure / algorithm',
                'Implement with proper edge case handling',
                'Verify time and space complexity',
                'Test with sample inputs from interview problems'
            ]
        
        vis.config_data = {
            "topic": vis.topic.name,
            "seeded": True,
            "steps": steps
        }
        vis.save()

    print(f"Updated {TopicVisualization.objects.count()} visualizers with structured data.")

if __name__ == '__main__':
    run()

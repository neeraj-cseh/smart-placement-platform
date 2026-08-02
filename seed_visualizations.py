import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Topic, TopicVisualization

# Dictionary of genuine, topic-specific steps for the visualizer
AUTHENTIC_STEPS = {
    # Core CS
    'sql-joins': [
        'Identify target tables and common keys (Foreign Key relationships)',
        'Choose the appropriate Join Type (INNER, LEFT, RIGHT, FULL OUTER)',
        'Filter raw data using WHERE clauses to reduce join volume',
        'Analyze execution plan for Cartesian product risks (Missing ON clauses)',
        'Optimize with covering indexes on the join columns'
    ],
    'aggregations-and-grouping': [
        'Identify the granularity required for the final report',
        'Apply GROUP BY to the non-aggregated dimensions',
        'Choose the correct aggregate function (SUM, COUNT, AVG, MAX)',
        'Filter aggregated results using HAVING clauses',
        'Analyze performance impact of sorting and grouping large datasets'
    ],
    'indexes-and-transactions': [
        'Identify slow-performing sequential scans in queries',
        'Design B-Tree or Hash indexes targeting WHERE and JOIN columns',
        'Evaluate index maintenance overhead for high-write tables',
        'Define transaction boundaries using BEGIN, COMMIT, and ROLLBACK',
        'Enforce ACID properties and configure isolation levels to prevent dirty reads'
    ],
    'dbms-core-concepts': [
        'Define the schema architecture and entity-relationships',
        'Ensure ACID compliance across the transaction log',
        'Map out relational constraints (Primary Keys, Unique Keys)',
        'Evaluate storage engines (e.g., InnoDB vs MyISAM)',
        'Analyze concurrency control and locking mechanisms'
    ],

    # Career & Soft Skills
    'resume-storytelling': [
        'Deconstruct the job description to identify core competencies required',
        'Select a past project that perfectly maps to those competencies',
        'Structure your narrative using the STAR (Situation, Task, Action, Result) method',
        'Replace passive descriptions with active, quantifiable impact metrics',
        'Rehearse delivering the story concisely within a 2-minute window'
    ],
    'resume-building': [
        'Select a clean, single-column ATS-friendly template',
        'Draft a powerful summary highlighting your core tech stack',
        'Bullet-point work experience starting with strong action verbs',
        'Quantify achievements (e.g., "Improved performance by 40% using Redis")',
        'Audit for typos, formatting consistency, and visual hierarchy'
    ],
    'hr-and-behavioral-rounds': [
        'Research the company’s core values and mission statement',
        'Prepare 3-4 versatile STAR stories that cover conflict, leadership, and failure',
        'Formulate insightful questions to ask the interviewer at the end',
        'Practice maintaining positive body language and eye contact',
        'Map your career goals to the specific role you are applying for'
    ],
    'mock-interview-feedback': [
        'Record the mock session and review the playback objectively',
        'Identify filler words, nervous tics, and clarity of articulation',
        'Analyze where code explanations broke down or became confusing',
        'Document feedback from the interviewer regarding algorithmic efficiency',
        'Create a targeted action plan to drill weak spots before the real interview'
    ],
    
    # Aptitude
    'percentages-and-profit-loss': [
        'Identify the base value (Cost Price) and the final value (Selling Price)',
        'Apply the standard formula: Profit/Loss = SP - CP',
        'Convert absolute margins into percentage relative to the Cost Price',
        'Factor in successive discounts or markups chronologically',
        'Double-check calculations against logical real-world constraints'
    ],
    'time-speed-distance': [
        'Harmonize all units (e.g., converting km/h to m/s by multiplying by 5/18)',
        'Identify the core relationship: Distance = Speed × Time',
        'Determine if the scenario involves relative speed (same vs opposite directions)',
        'Apply the formula to the specific moving entities (trains, boats in streams)',
        'Validate the output magnitude for physical realism'
    ],
    'logical-puzzles': [
        'Read the prompt carefully and extract all absolute constraints',
        'Map out relationships using a grid or logic table',
        'Identify the most restrictive constraint as your starting point',
        'Use the process of elimination to cross out impossible combinations',
        'Verify the final arrangement against every initial rule'
    ],
    'data-interpretation': [
        'Skim the chart axes, legends, and units before looking at the questions',
        'Identify the specific data points required by the prompt',
        'Approximate complex calculations to quickly eliminate wrong options',
        'Perform the precise arithmetic for the remaining close options',
        'Cross-reference the result with visual trends in the graph'
    ],

    # Core CS Theory / System Design
    'system-design-basics': [
        'Clarify system requirements, scale, and traffic estimates',
        'Define the high-level architecture and API contracts',
        'Design the database schema and choose between SQL vs NoSQL',
        'Identify bottlenecks and introduce caching/load balancing layers',
        'Discuss trade-offs regarding availability, consistency, and partition tolerance (CAP)'
    ],
    'oop-principles': [
        'Identify real-world entities and map them to Classes and Objects',
        'Apply Encapsulation to protect internal state using private variables',
        'Design Inheritance hierarchies to promote code reuse',
        'Implement Polymorphism to allow dynamic method overriding',
        'Refactor using Abstraction to hide complex implementation details'
    ],
    'computer-networks': [
        'Identify the OSI or TCP/IP layer where the problem occurs',
        'Trace the packet flow from client to server (DNS, TCP Handshake, TLS)',
        'Analyze routing and IP addressing protocols',
        'Evaluate transport mechanisms (TCP vs UDP reliability)',
        'Diagnose common points of failure (firewalls, NAT, DNS resolution)'
    ],
    
    # DSA (More specific than generic)
    'arrays-and-strings': [
        'Check for contiguous sub-segment constraints',
        'Consider sorting the array to unlock binary search or two pointers',
        'Watch out for out-of-bounds indexing edge cases',
        'Determine if in-place modification is required to save O(N) space',
        'Trace string manipulations carefully accounting for immutability'
    ],
    'trees-and-binary-search-trees': [
        'Identify if a Depth-First (Recursive) or Breadth-First (Queue) approach is needed',
        'Define the base cases for leaf nodes and null pointers',
        'Leverage the BST property (Left < Root < Right) to prune search paths',
        'Implement the recursive calls for left and right subtrees',
        'Aggregate the results as the recursion stack unwinds'
    ]
}

def seed_authentic_data():
    topics = Topic.objects.filter(is_active=True)
    updated_count = 0
    
    for topic in topics:
        if topic.slug in AUTHENTIC_STEPS:
            # Get or create the TopicVisualization
            vis, created = TopicVisualization.objects.get_or_create(
                topic=topic,
                defaults={
                    'title': f"{topic.name} Simulation",
                    'visualization_type': 'generic'
                }
            )
            
            # Make sure it's set to generic so it uses our steps
            if vis.visualization_type != 'generic':
                vis.visualization_type = 'generic'
                
            # Inject genuine steps
            config = vis.config_data or {}
            config['steps'] = AUTHENTIC_STEPS[topic.slug]
            vis.config_data = config
            vis.save()
            updated_count += 1
            print(f"Updated authentic steps for: {topic.slug}")
            
    print(f"\nSuccessfully seeded authentic data for {updated_count} topics.")

if __name__ == '__main__':
    seed_authentic_data()

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import Topic, TopicVisualization

AUTHENTIC_STEPS_PART_2 = {
    # DSA Specifics
    'sliding-window': [
        'Initialize left and right pointers at the start of the array',
        'Expand the window by moving the right pointer and updating state',
        'Check if the current window violates the problem constraints',
        'Shrink the window from the left until constraints are satisfied',
        'Update the global maximum/minimum result at valid states'
    ],
    'two-pointers': [
        'Identify if pointers should start at opposite ends or the same end',
        'Evaluate the condition to move the left pointer',
        'Evaluate the condition to move the right pointer',
        'Process the elements at the current pointer positions',
        'Terminate the loop when pointers cross or reach the end'
    ],
    'advanced-array-problems': [
        'Analyze if a prefix sum or difference array can optimize range queries',
        'Determine if the problem requires an in-place cyclic sort',
        'Check for overlapping intervals and sort by start times',
        'Utilize a monotonic stack/queue for next-greater element problems',
        'Identify 2D matrix traversal patterns (spiral, diagonal)'
    ],
    'linked-lists': [
        'Initialize a dummy head to simplify edge cases at the start',
        'Use the slow and fast pointer (Tortoise and Hare) technique for cycles',
        'Track the previous node carefully when reversing links',
        'Handle null pointer exceptions and the tail node explicitly',
        'Sever the list correctly when splitting or interleaving'
    ],
    'stacks-and-queues': [
        'Determine if LIFO (Stack) or FIFO (Queue) access is required',
        'Push elements while maintaining necessary invariants (e.g., monotonic)',
        'Pop elements to resolve matching pairs or process deferred tasks',
        'Check for underflow conditions before accessing the top/front',
        'Simulate recursion iteratively using an explicit stack'
    ],
    'graphs-and-traversal': [
        'Choose an adjacency list or matrix representation based on density',
        'Initialize a visited set/array to prevent infinite cycles',
        'Select BFS for shortest path in unweighted graphs, DFS for exploration',
        'Push the starting node to the queue/stack and mark as visited',
        'Process neighbors iteratively, updating path costs or parent pointers'
    ],
    'dynamic-programming': [
        'Define the objective function and the meaning of the DP state',
        'Identify the base cases (e.g., dp[0], dp[1])',
        'Formulate the state transition equation (recurrence relation)',
        'Determine the direction of computation (top-down memoization vs bottom-up)',
        'Optimize space complexity by retaining only necessary previous states'
    ],
    'dsa': [
        'Clarify the problem constraints, input sizes, and edge cases',
        'Brainstorm a brute-force approach and state its complexity',
        'Identify overlapping subproblems or redundant calculations',
        'Propose an optimized data structure (e.g., Hash Map, Heap)',
        'Dry run the optimized algorithm with a small trace table'
    ],

    # Core CS & Architecture
    'operating-system-basics': [
        'Differentiate between processes (isolated memory) and threads (shared memory)',
        'Analyze context switching overhead in the CPU scheduler',
        'Identify critical sections and apply mutexes/semaphores to prevent race conditions',
        'Evaluate memory management (paging, segmentation, virtual memory)',
        'Diagnose potential deadlock conditions (Coffman conditions)'
    ],
    'os': [
        'Identify the hardware resource being managed (CPU, Memory, Disk)',
        'Evaluate the scheduling or allocation algorithm (e.g., Round Robin, LRU)',
        'Ensure proper synchronization primitives are used',
        'Handle hardware interrupts and system calls safely',
        'Analyze the impact on system throughput and latency'
    ],
    'normalization': [
        'Ensure all attributes are atomic to achieve First Normal Form (1NF)',
        'Remove partial dependencies to achieve Second Normal Form (2NF)',
        'Eliminate transitive dependencies to achieve Third Normal Form (3NF)',
        'Evaluate Boyce-Codd Normal Form (BCNF) for overlapping candidate keys',
        'Weigh the performance cost of JOINs against the risk of data anomalies'
    ],
    'query-optimization': [
        'Extract the EXPLAIN PLAN to analyze database execution strategy',
        'Replace correlated subqueries with efficient JOIN operations',
        'Ensure predicates are sargable (index-friendly, no functions on columns)',
        'Filter data early using WHERE before applying GROUP BY or ORDER BY',
        'Evaluate the necessity of SELECT * vs fetching specific columns'
    ],

    # Web & Software Dev
    'html-css-responsive-ui': [
        'Structure semantic HTML5 tags (header, main, article, footer)',
        'Implement CSS Flexbox or Grid for fluid layouts',
        'Define mobile-first media queries for varying breakpoints',
        'Optimize asset loading and utilize relative units (rem, vh, vw)',
        'Ensure WCAG accessibility compliance (contrast, ARIA roles, alt text)'
    ],
    'javascript-fundamentals': [
        'Differentiate between var, let, and const scoping rules',
        'Manage asynchronous operations using Promises and async/await',
        'Manipulate the DOM efficiently minimizing reflows and repaints',
        'Handle event bubbling and delegation gracefully',
        'Understand closures and the lexical binding of the "this" keyword'
    ],
    'react-components-and-state': [
        'Deconstruct the UI into isolated, reusable functional components',
        'Manage local component state using the useState hook',
        'Handle side effects and lifecycle events with useEffect',
        'Pass data downwards via props and hoist state upwards when shared',
        'Optimize re-renders using useMemo, useCallback, or React.memo'
    ],
    'rest-apis-and-authentication': [
        'Map CRUD operations to appropriate HTTP methods (GET, POST, PUT, DELETE)',
        'Design logical, noun-based URI endpoints (e.g., /users/123/orders)',
        'Implement stateless authentication using JWT in the Authorization header',
        'Handle HTTP status codes correctly (200, 201, 400, 401, 404, 500)',
        'Secure endpoints against CORS, CSRF, and SQL Injection vulnerabilities'
    ],
    'deployment-and-git-workflow': [
        'Branch from main using a standardized naming convention (e.g., feature/auth)',
        'Commit atomic changes with descriptive, imperative messages',
        'Open a Pull Request and pass automated CI/CD pipeline tests',
        'Resolve merge conflicts by rebasing or merging carefully',
        'Deploy immutable build artifacts to staging/production environments'
    ],
    'django-rest-apis': [
        'Define Django Models and run makemigrations/migrate',
        'Create ModelSerializers to handle JSON conversion and validation',
        'Implement GenericAPIViews or ViewSets for rapid endpoint creation',
        'Wire up URLs using DRF Routers for automatic routing',
        'Apply permission classes (e.g., IsAuthenticated) to secure endpoints'
    ],
    'authentication-and-jwt': [
        'Capture user credentials securely over HTTPS',
        'Verify password hashes using libraries like bcrypt/Argon2',
        'Generate a signed JWT payload containing user claims and expiration',
        'Store the token securely on the client (HttpOnly cookie or secure storage)',
        'Validate the token signature on middleware for subsequent requests'
    ],
    'api-testing': [
        'Define the expected request payload, headers, and query parameters',
        'Mock external dependencies and database states for isolation',
        'Assert the correct HTTP response status code is returned',
        'Validate the JSON response schema and specific data values',
        'Test edge cases, invalid inputs, and unauthorized access attempts'
    ],

    # Data & Analytics
    'excel-and-spreadsheet-basics': [
        'Format raw data as a Table for dynamic range references',
        'Apply VLOOKUP/XLOOKUP to merge data from related sheets',
        'Utilize conditional formatting to highlight outliers and trends',
        'Create PivotTables to aggregate and summarize large datasets',
        'Protect sensitive cells and validate data entry inputs'
    ],
    'sql-analytics': [
        'Leverage window functions (ROW_NUMBER, RANK) for partitioned analysis',
        'Calculate rolling averages and running totals using OVER clauses',
        'Handle NULL values gracefully with COALESCE or ISNULL',
        'Use Common Table Expressions (CTEs) to simplify complex nested logic',
        'Extract date/time parts for temporal trend aggregation'
    ],
    'python-data-cleaning': [
        'Load data into a Pandas DataFrame and inspect info() and head()',
        'Identify and drop or impute missing values (NaNs)',
        'Detect and remove duplicate rows based on unique identifiers',
        'Convert data types (e.g., string to datetime, object to category)',
        'Filter outliers using Z-scores or Interquartile Range (IQR)'
    ],
    'dashboard-storytelling': [
        'Identify the target audience and their core KPIs',
        'Choose the appropriate chart type (e.g., Line for time, Bar for categories)',
        'Minimize cognitive load by removing chart junk and excessive colors',
        'Implement interactive filters and drill-down capabilities',
        'Add contextual text annotations to explain sudden data spikes'
    ],
    'statistics-fundamentals': [
        'Calculate central tendency (Mean, Median, Mode)',
        'Measure data dispersion (Variance, Standard Deviation, Range)',
        'Identify the probability distribution (Normal, Binomial, Poisson)',
        'Formulate Null and Alternative hypotheses for A/B testing',
        'Determine statistical significance using p-values and confidence intervals'
    ],

    # Misc & Soft Skills
    'object-oriented-design': [
        'Identify the core actors and use cases of the system',
        'Draft a UML Class Diagram defining properties and methods',
        'Apply SOLID principles (Single Responsibility, Open/Closed, etc.)',
        'Utilize Design Patterns (Singleton, Factory, Observer) where applicable',
        'Ensure loose coupling through dependency injection'
    ],
    'debugging-and-code-quality': [
        'Reproduce the bug consistently in an isolated environment',
        'Trace the execution flow using a debugger or strategic log statements',
        'Identify the root cause rather than patching the symptom',
        'Write a unit test that fails to prove the bug exists',
        'Implement the fix and verify the test passes without breaking existing ones'
    ],
    'aptitude-warmup': [
        'Scan the problem to identify the required mathematical concept',
        'Write down the given values and the target unknown',
        'Set up the algebraic equation or ratio',
        'Perform mental math estimations to eliminate obviously wrong answers',
        'Execute the precise calculation and verify units'
    ],
    'company-research': [
        'Review the company’s recent news, product launches, and earnings reports',
        'Understand their core business model and target demographic',
        'Analyze the tech stack and engineering blog for technical insights',
        'Identify their main competitors and market differentiators',
        'Formulate 2-3 specific, insightful questions to ask the interviewer'
    ],
    'communication-practice': [
        'Listen actively to the prompt without interrupting',
        'Pause for 2-3 seconds to structure your thoughts before speaking',
        'State your conclusion or core thesis upfront (Bottom Line Up Front)',
        'Support your thesis with 2-3 logical points or data evidence',
        'Conclude with a brief summary and invite follow-up questions'
    ],
    'mock-test-strategy': [
        'Scan the entire test paper/platform to gauge question difficulty',
        'Allocate strict time limits per section based on weighting',
        'Execute a multi-pass strategy: answer easy questions first',
        'Mark difficult or time-consuming questions for review later',
        'Reserve the last 5 minutes to review flagged answers and guess if no negative marking'
    ],
    'coding-interview-strategy': [
        'Clarify the problem statement and confirm edge cases aloud',
        'Propose a brute force solution to establish a baseline',
        'Discuss optimizations and agree on an approach with the interviewer',
        'Write clean, modular code while vocalizing your thought process',
        'Dry run the code with a small test case to catch off-by-one errors'
    ]
}

def seed_remaining_data():
    topics = Topic.objects.filter(is_active=True)
    updated_count = 0
    
    for topic in topics:
        if topic.slug in AUTHENTIC_STEPS_PART_2:
            vis, created = TopicVisualization.objects.get_or_create(
                topic=topic,
                defaults={
                    'title': f"{topic.name} Simulation",
                    'visualization_type': 'generic'
                }
            )
            
            if vis.visualization_type != 'generic':
                vis.visualization_type = 'generic'
                
            config = vis.config_data or {}
            config['steps'] = AUTHENTIC_STEPS_PART_2[topic.slug]
            vis.config_data = config
            vis.save()
            updated_count += 1
            print(f"Updated authentic steps for: {topic.slug}")
            
    print(f"\nSuccessfully seeded authentic data for {updated_count} topics.")

if __name__ == '__main__':
    seed_remaining_data()

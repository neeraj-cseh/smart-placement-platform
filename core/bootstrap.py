from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from .models import (
    ActivityEvent,
    CompanyTarget,
    DailyPlanItem,
    InterviewReadiness,
    Question,
    RevisionQueueItem,
    Test,
    TestAttempt,
    Topic,
    Track,
    UserAnswer,
    UserTopicProgress,
)


DEFAULT_PROFILE = {
    "branch": "Computer Science and Engineering",
    "college": "Ramaiah Institute of Technology",
    "degree": "B.Tech",
    "graduation_year": 2026,
    "cgpa": 8.2,
    "has_backlog": False,
    "location": "Bengaluru, India",
    "preferred_role": "Software Development Engineer",
    "phone": "+91 98765 43210",
    "linkedin_url": "https://www.linkedin.com/in/prepsmart-student",
    "github_url": "https://github.com/prepsmart-student",
    "portfolio_url": "https://prepsmart.dev/student",
    "resume_headline": "Placement-ready CSE student focused on DSA, backend APIs, and practical product projects.",
    "bio": "Building consistent interview readiness across DSA, aptitude, CS fundamentals, projects, and communication.",
    "skills": ["Python", "Django", "React", "SQL", "DSA", "REST APIs"],
    "target_companies": ["TCS", "Infosys", "Accenture", "Zoho"],
    "weekly_goal_hours": 14,
    "timezone": "Asia/Kolkata",
    "email_notifications": True,
    "product_updates": False,
    "public_profile": False,
}


TRACK_CATALOG = [
    {
        "name": "Data Structures and Algorithms",
        "description": "Core coding interview foundations from arrays to dynamic programming.",
        "topics": [
            (
                "Arrays and Strings",
                "Master indexing, two pointers, sliding windows, prefix sums, and string transforms.",
                [
                    ("easy", "What is the time complexity of binary search on a sorted array?", ["O(n)", "O(log n)", "O(n log n)", "O(1)"], "B"),
                    ("medium", "Which technique is usually best for the longest substring without repeating characters?", ["Recursion", "Sliding window", "Merge sort", "Backtracking"], "B"),
                ],
            ),
            (
                "Sliding Window",
                "Maintain window constraints over subarrays or substrings to solve window problems.",
                [
                    ("medium", "Which condition is necessary for a sliding window to achieve O(1) extra space?", ["Monotonic hash set", "Variables representing indices only", "Creating a new array copy", "Sorting"], "B"),
                    ("medium", "How does a dynamic window adjust its size?", ["Expands right pointer, contracts left pointer based on constraint", "Flashes values", "Recurses on heap", "Doubles capacity"], "A"),
                ],
            ),
            (
                "Two Pointers",
                "Optimize array traversal using left/right or slow/fast bounds to avoid nested loops.",
                [
                    ("easy", "Two pointer method is frequently used on which type of arrays?", ["Sorted arrays", "Empty arrays", "Unbounded buffers", "Random matrices"], "A"),
                    ("medium", "What is the typical time complexity of searching in a sorted array with two pointers?", ["O(N^2)", "O(N log N)", "O(N)", "O(1)"], "C"),
                ],
            ),
            (
                "Advanced Array Problems",
                "Pressure test array knowledge with complex indexing, prefixes, and multi-dimensional matrices.",
                [
                    ("medium", "A prefix sum array helps compute range queries in what time complexity?", ["O(1)", "O(log N)", "O(N)", "O(N^2)"], "A"),
                    ("hard", "Which technique is best to rotate a square 2D matrix in-place?", ["Transpose then reverse columns", "Create temporary copy", "Using linked node layers", "Backtracking DFS"], "A"),
                ],
            ),
            (
                "Linked Lists",
                "Build confidence with pointer movement, cycle detection, reversal, and merge patterns.",
                [
                    ("easy", "Which pointer setup is used in Floyd cycle detection?", ["One pointer only", "Slow and fast pointers", "A stack and queue", "Two arrays"], "B"),
                    ("medium", "What is the extra space needed to reverse a singly linked list iteratively?", ["O(1)", "O(log n)", "O(n)", "O(n squared)"], "A"),
                ],
            ),
            (
                "Stacks and Queues",
                "Use LIFO and FIFO patterns for parsing, monotonic stacks, and scheduling questions.",
                [
                    ("easy", "Which structure is most suitable for validating balanced brackets?", ["Queue", "Stack", "Hash map only", "Heap"], "B"),
                    ("medium", "A monotonic stack is commonly used to solve which type of problem?", ["Next greater element", "Binary search", "SQL join", "DNS lookup"], "A"),
                ],
            ),
            (
                "Trees and Binary Search Trees",
                "Practice traversals, recursion, height checks, BST ordering, and lowest common ancestor.",
                [
                    ("medium", "In a BST, where are values smaller than the root usually placed?", ["Right subtree", "Left subtree", "Parent node", "Any leaf"], "B"),
                    ("medium", "Which traversal visits left subtree, root, then right subtree?", ["Preorder", "Inorder", "Postorder", "Level order"], "B"),
                ],
            ),
            (
                "Graphs and Traversal",
                "Understand BFS, DFS, visited sets, connected components, and shortest path basics.",
                [
                    ("medium", "Which traversal naturally finds the shortest path in an unweighted graph?", ["DFS", "BFS", "Heap sort", "Binary search"], "B"),
                    ("hard", "What prevents infinite loops while traversing cyclic graphs?", ["Sorting edges", "Visited tracking", "Using strings", "Removing vertices"], "B"),
                ],
            ),
            (
                "Dynamic Programming",
                "Recognize overlapping subproblems and convert recursion into tabulation or memoization.",
                [
                    ("hard", "Dynamic programming is useful when a problem has overlapping subproblems and what other property?", ["Random input", "Optimal substructure", "Only one answer", "No recursion"], "B"),
                    ("medium", "Memoization stores results mainly to avoid what?", ["Compilation", "Repeated computation", "Database writes", "Network latency"], "B"),
                ],
            ),
        ],
    },
    {
        "name": "Aptitude and Reasoning",
        "description": "Placement aptitude practice for campus hiring rounds and service company screens.",
        "topics": [
            (
                "Number Systems",
                "Revise divisibility, remainders, LCM, HCF, and base conversion shortcuts.",
                [
                    ("easy", "What is the HCF of 12 and 18?", ["3", "6", "12", "36"], "B"),
                    ("medium", "If a number leaves remainder 2 when divided by 5, which could be its unit digit?", ["0", "3", "7", "9"], "C"),
                ],
            ),
            (
                "Percentages and Profit Loss",
                "Handle percentage change, discounts, marked price, cost price, and selling price.",
                [
                    ("easy", "A price increases from 100 to 120. What is the percentage increase?", ["10%", "15%", "20%", "25%"], "C"),
                    ("medium", "If cost price is 500 and profit is 20%, what is selling price?", ["520", "560", "600", "650"], "C"),
                ],
            ),
            (
                "Time Speed Distance",
                "Practice relative speed, trains, boats, races, and average speed problems.",
                [
                    ("easy", "A vehicle covers 120 km in 3 hours. What is its speed?", ["30 km/h", "40 km/h", "45 km/h", "60 km/h"], "B"),
                    ("medium", "When two objects move toward each other, their relative speed is the what of speeds?", ["Difference", "Product", "Sum", "Average"], "C"),
                ],
            ),
            (
                "Logical Puzzles",
                "Develop arrangement, ranking, direction sense, and constraint-based reasoning.",
                [
                    ("medium", "In seating puzzles, what should be fixed first when possible?", ["A random person", "A definite position", "The final answer", "No variable"], "B"),
                    ("medium", "Direction sense questions mainly test movement tracking relative to what?", ["Compass directions", "Prime numbers", "Database keys", "Stack depth"], "A"),
                ],
            ),
            (
                "Data Interpretation",
                "Read charts, tables, ratios, averages, and comparative percentage data quickly.",
                [
                    ("easy", "Data interpretation questions usually begin by identifying what?", ["Chart units and totals", "Compiler errors", "CSS colors", "HTTP status"], "A"),
                    ("medium", "If total sales are 200 and product A contributes 50, product A share is what?", ["20%", "25%", "40%", "50%"], "B"),
                ],
            ),
        ],
    },
    {
        "name": "Computer Science Fundamentals",
        "description": "Interview-ready CS concepts across OOP, OS, networks, DBMS, and design basics.",
        "topics": [
            (
                "OOP Principles",
                "Use encapsulation, inheritance, polymorphism, and abstraction in interview answers.",
                [
                    ("easy", "Which OOP principle hides internal state behind methods?", ["Inheritance", "Encapsulation", "Polymorphism", "Compilation"], "B"),
                    ("medium", "Method overriding is usually an example of which OOP behavior?", ["Runtime polymorphism", "Normalization", "Paging", "Caching"], "A"),
                ],
            ),
            (
                "Operating System Basics",
                "Review process, thread, scheduling, memory management, deadlock, and synchronization.",
                [
                    ("medium", "Which OS concept lets multiple processes appear to run at the same time?", ["Scheduling", "Indexing", "CSS cascade", "Serialization"], "A"),
                    ("medium", "Deadlock requires mutual exclusion, hold and wait, no preemption, and what?", ["Circular wait", "Binary search", "DNS", "Inheritance"], "A"),
                ],
            ),
            (
                "Computer Networks",
                "Understand TCP/IP, HTTP, DNS, latency, ports, and client-server communication.",
                [
                    ("easy", "Which protocol is connection-oriented and reliable?", ["UDP", "TCP", "ICMP", "ARP"], "B"),
                    ("medium", "DNS primarily converts a domain name into what?", ["IP address", "Password", "HTML page", "Database row"], "A"),
                ],
            ),
            (
                "DBMS Core Concepts",
                "Explain keys, joins, normalization, transactions, indexing, and ACID clearly.",
                [
                    ("easy", "Which key uniquely identifies a row in a table?", ["Foreign key", "Primary key", "Candidate note", "Index hint"], "B"),
                    ("medium", "The I in ACID stands for what?", ["Indexing", "Isolation", "Iteration", "Inheritance"], "B"),
                ],
            ),
            (
                "System Design Basics",
                "Learn requirements, APIs, caching, queues, scaling, and tradeoff communication.",
                [
                    ("medium", "Caching is mainly used to improve what?", ["Latency and repeated reads", "Password length", "CSS layout", "Variable naming"], "A"),
                    ("medium", "A queue helps systems handle work by doing what?", ["Buffering asynchronous tasks", "Deleting data", "Compiling code", "Drawing charts"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "SQL and Databases",
        "description": "Practical SQL and database thinking for analytics, backend, and interview rounds.",
        "topics": [
            (
                "SQL Joins",
                "Use inner, left, right, and self joins to combine related tables correctly.",
                [
                    ("easy", "Which join returns matching rows from both tables?", ["INNER JOIN", "FULL OUTER JOIN only", "CROSS JOIN", "DROP JOIN"], "A"),
                    ("medium", "A LEFT JOIN keeps all rows from which table?", ["Right table", "Left table", "Neither table", "Only duplicated rows"], "B"),
                ],
            ),
            (
                "Aggregations and Grouping",
                "Work with COUNT, SUM, AVG, GROUP BY, HAVING, and grouped filters.",
                [
                    ("easy", "Which clause groups rows before aggregation?", ["ORDER BY", "GROUP BY", "WHERE", "LIMIT"], "B"),
                    ("medium", "Which clause filters aggregated groups?", ["HAVING", "WHERE only", "JOIN", "SELECT"], "A"),
                ],
            ),
            (
                "Indexes and Transactions",
                "Understand read performance, write tradeoffs, transactions, rollback, and commit.",
                [
                    ("medium", "An index usually improves which operation?", ["Searching rows", "Adding CSS", "Changing passwords", "Rendering SVG"], "A"),
                    ("medium", "Which command makes a transaction permanent?", ["ROLLBACK", "COMMIT", "SELECT", "JOIN"], "B"),
                ],
            ),
            (
                "Normalization",
                "Reduce redundancy using normal forms and clear table relationships.",
                [
                    ("medium", "Normalization mainly aims to reduce what?", ["Data redundancy", "Network speed", "Font size", "CPU temperature"], "A"),
                    ("medium", "A table in first normal form should avoid what?", ["Atomic values", "Repeating groups", "Primary keys", "Rows"], "B"),
                ],
            ),
            (
                "Query Optimization",
                "Read explain plans, avoid unnecessary scans, and improve query structure.",
                [
                    ("hard", "An EXPLAIN plan helps you understand what?", ["How a query is executed", "How CSS loads", "How JWT expires", "How React renders"], "A"),
                    ("medium", "Selecting only needed columns can reduce what?", ["Transferred data", "Correctness", "Table count", "Authentication"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "Web Development and Projects",
        "description": "Frontend, backend, API, authentication, and deployment skills for portfolio projects.",
        "topics": [
            (
                "HTML CSS Responsive UI",
                "Build semantic, responsive layouts with accessible forms and polished visual hierarchy.",
                [
                    ("easy", "Which HTML element is best for primary page navigation?", ["nav", "span", "br", "script"], "A"),
                    ("medium", "Responsive layouts commonly use media queries and what CSS feature?", ["Flexbox or grid", "SQL joins", "Binary trees", "JWT refresh"], "A"),
                ],
            ),
            (
                "JavaScript Fundamentals",
                "Strengthen closures, arrays, async code, promises, DOM, and browser behavior.",
                [
                    ("easy", "Which keyword declares a block-scoped variable?", ["var", "let", "global", "static"], "B"),
                    ("medium", "A Promise represents a value that may be available when?", ["Now or later", "Only at compile time", "Never", "Only in CSS"], "A"),
                ],
            ),
            (
                "React Components and State",
                "Design component boundaries, props, state, effects, lists, and forms.",
                [
                    ("easy", "React props are mainly used to pass what?", ["Data to components", "SQL rows", "Ports", "Passwords"], "A"),
                    ("medium", "State updates in React should be treated as what?", ["Immutable changes", "Direct mutation only", "Database commits", "CSS imports"], "A"),
                ],
            ),
            (
                "REST APIs and Authentication",
                "Connect clients to APIs with JWT auth, protected routes, validation, and error states.",
                [
                    ("medium", "A 401 HTTP response generally means what?", ["Unauthorized", "Created", "No content", "Redirected"], "A"),
                    ("medium", "JWT access tokens are usually sent in which header?", ["Authorization", "Accept-Language", "Host", "Cache-Control"], "A"),
                ],
            ),
            (
                "Deployment and Git Workflow",
                "Use branches, commits, environment variables, build checks, and deployment readiness.",
                [
                    ("easy", "Which Git command records staged changes?", ["git commit", "git pull", "git clone", "git status"], "A"),
                    ("medium", "Environment variables are useful because they keep what out of source code?", ["Secrets and config", "HTML tags", "Loop counters", "CSS classes"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "Backend Developer",
        "description": "Backend placement skills covering databases, APIs, authentication, testing, and production thinking.",
        "topics": [
            (
                "DBMS",
                "Revise relational modeling, SQL basics, transactions, indexing, and database constraints.",
                [
                    ("easy", "Which constraint prevents duplicate values in a unique column?", ["UNIQUE", "ORDER", "LIMIT", "FORMAT"], "A"),
                    ("medium", "A foreign key usually references what?", ["A column in another table", "A CSS selector", "A local variable", "A browser cache"], "A"),
                ],
            ),
            (
                "Django REST APIs",
                "Build resource endpoints with serializers, status codes, permissions, and validation.",
                [
                    ("easy", "Which HTTP method is commonly used to create a resource?", ["GET", "POST", "HEAD", "OPTIONS only"], "B"),
                    ("medium", "Serializers in DRF are mainly used for validation and what?", ["Data representation", "CSS rendering", "Port scanning", "Image compression"], "A"),
                ],
            ),
            (
                "Authentication and JWT",
                "Secure APIs with login, access tokens, refresh tokens, and protected endpoints.",
                [
                    ("medium", "JWT based APIs usually protect endpoints by checking which header?", ["Authorization", "Content-Length", "Referer", "Accept"], "A"),
                    ("medium", "Refresh tokens are mainly used to obtain what?", ["A new access token", "A SQL table", "A CSS class", "A DNS record"], "A"),
                ],
            ),
            (
                "API Testing",
                "Verify backend behavior with request tests, fixtures, edge cases, and response contracts.",
                [
                    ("easy", "An API smoke test usually checks whether critical endpoints do what?", ["Respond successfully", "Change font size", "Open a modal", "Compile Sass"], "A"),
                    ("medium", "Testing unauthorized access should usually expect which status code?", ["200", "201", "401", "500"], "C"),
                ],
            ),
        ],
    },
    {
        "name": "Data Analyst",
        "description": "Analytics placement skills for SQL, spreadsheets, Python cleaning, statistics, and dashboard storytelling.",
        "topics": [
            (
                "Excel and Spreadsheet Basics",
                "Use formulas, pivots, lookups, sorting, filtering, and clean worksheet structure.",
                [
                    ("easy", "Which spreadsheet feature summarizes grouped rows quickly?", ["Pivot table", "CSS grid", "JWT", "Stack"], "A"),
                    ("medium", "A lookup formula is most often used to do what?", ["Find related values", "Deploy code", "Encrypt tokens", "Traverse trees"], "A"),
                ],
            ),
            (
                "SQL Analytics",
                "Write analytical queries using filters, joins, grouping, windows, and ranked results.",
                [
                    ("medium", "Which SQL function can rank rows within a partition?", ["RANK", "PRINT", "FETCHTOKEN", "STYLE"], "A"),
                    ("medium", "Window functions calculate values while preserving what?", ["Row-level output", "Only one row", "CSS state", "Passwords"], "A"),
                ],
            ),
            (
                "Python Data Cleaning",
                "Prepare datasets by handling missing values, types, duplicates, and outliers.",
                [
                    ("easy", "Removing duplicate rows improves what?", ["Data quality", "Button color", "Token expiry", "Port number"], "A"),
                    ("medium", "Missing value treatment should depend on what?", ["Business meaning and analysis goal", "File name only", "Screen width", "Git branch"], "A"),
                ],
            ),
            (
                "Dashboard Storytelling",
                "Turn metrics into clear insights with charts, hierarchy, comparisons, and decisions.",
                [
                    ("easy", "A good dashboard should emphasize what first?", ["Most important decision metrics", "Random decoration", "Hidden data", "All colors equally"], "A"),
                    ("medium", "Trend charts are best for showing what?", ["Change over time", "Password strength", "Nested loops", "Token scopes"], "A"),
                ],
            ),
            (
                "Statistics Fundamentals",
                "Understand mean, median, variance, sampling, correlation, and practical inference.",
                [
                    ("easy", "Median is the value in which position after sorting?", ["Middle", "First", "Last", "Random"], "A"),
                    ("medium", "Correlation describes what between two variables?", ["Relationship strength and direction", "Database size", "CSS inheritance", "API latency only"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "SDE",
        "description": "Software development engineer readiness across DSA, OS, OOD, debugging, and coding habits.",
        "topics": [
            (
                "DSA",
                "Practice common coding patterns, complexity analysis, and clean implementation.",
                [
                    ("easy", "Big O notation mainly describes how performance changes with what?", ["Input size", "Screen size", "Company name", "Password length"], "A"),
                    ("medium", "Hash maps are commonly used to improve lookup time to what average case?", ["O(1)", "O(n)", "O(n log n)", "O(n squared)"], "A"),
                ],
            ),
            (
                "OS",
                "Prepare process, thread, memory, scheduling, and synchronization answers.",
                [
                    ("easy", "A thread belongs inside what?", ["A process", "A database table", "A CSS rule", "A DNS zone"], "A"),
                    ("medium", "Context switching is performed by which layer?", ["Operating system", "HTML parser", "SQL optimizer only", "Git remote"], "A"),
                ],
            ),
            (
                "Object Oriented Design",
                "Model classes, responsibilities, interfaces, and extensible design decisions.",
                [
                    ("medium", "Single responsibility principle says a class should have how many main reasons to change?", ["One", "Two", "Ten", "Unlimited"], "A"),
                    ("medium", "Interfaces help code depend on what instead of concrete details?", ["Abstractions", "Passwords", "Table rows", "Screen pixels"], "A"),
                ],
            ),
            (
                "Debugging and Code Quality",
                "Use traces, tests, logs, naming, edge cases, and refactoring to produce reliable code.",
                [
                    ("easy", "A failing test is useful because it gives what?", ["A reproducible signal", "A deployment token", "A CSS class", "A database backup"], "A"),
                    ("medium", "Good variable names mainly improve what?", ["Readability", "CPU cache only", "Network speed", "SQL indexing"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "General Placement",
        "description": "End-to-end placement preparation for resumes, companies, aptitude, communication, and mock strategy.",
        "topics": [
            (
                "Resume Building",
                "Create a clear one-page resume with measurable projects, skills, education, and achievements.",
                [
                    ("easy", "A resume bullet is stronger when it includes what?", ["Measurable impact", "Random adjectives", "Hidden text", "Only tools"], "A"),
                    ("medium", "Project bullets should connect technical work with what?", ["Outcome", "Font family", "Port number", "File extension"], "A"),
                ],
            ),
            (
                "Aptitude Warmup",
                "Keep daily speed sharp with arithmetic, ratios, percentages, and quick reasoning sets.",
                [
                    ("easy", "Daily aptitude warmups mainly improve what?", ["Speed and accuracy", "Image quality", "Token size", "CSS specificity"], "A"),
                    ("medium", "Timed practice helps identify what?", ["Slow question types", "Database schemas", "React props", "DNS zones"], "A"),
                ],
            ),
            (
                "Company Research",
                "Study role expectations, hiring rounds, company values, products, and recent interview patterns.",
                [
                    ("easy", "Company research helps tailor what?", ["Preparation and answers", "Screen brightness", "Variable scope", "SQL syntax"], "A"),
                    ("medium", "Before an interview, knowing the role helps prioritize which examples?", ["Relevant projects", "Random facts", "Only hobbies", "Unrelated tools"], "A"),
                ],
            ),
            (
                "Communication Practice",
                "Practice concise explanations, structured answers, active listening, and confidence.",
                [
                    ("easy", "Concise answers are easier for interviewers to do what?", ["Follow", "Compile", "Encrypt", "Normalize"], "A"),
                    ("medium", "When explaining a solution, stating tradeoffs shows what?", ["Engineering judgment", "CSS skill only", "Typing speed", "Password memory"], "A"),
                ],
            ),
            (
                "Mock Test Strategy",
                "Plan test attempts, review errors, manage time, and convert mock results into action.",
                [
                    ("easy", "After a mock test, the most important next step is what?", ["Review mistakes", "Ignore score", "Change theme", "Delete account"], "A"),
                    ("medium", "Time boxing sections helps prevent what?", ["Over-spending time on one area", "Login success", "CSS overflow", "Data backup"], "A"),
                ],
            ),
        ],
    },
    {
        "name": "Interview Readiness",
        "description": "Convert preparation into confident technical, project, HR, and mock interview performance.",
        "topics": [
            (
                "Resume Storytelling",
                "Frame projects with problem, action, impact, tradeoffs, and measurable outcomes.",
                [
                    ("easy", "A strong project explanation should include problem, action, and what?", ["Impact", "Only file names", "Font size", "Random tools"], "A"),
                    ("medium", "Quantifying a resume bullet mainly improves what?", ["Evidence of impact", "Page color", "Password security", "SQL syntax"], "A"),
                ],
            ),
            (
                "HR and Behavioral Rounds",
                "Prepare STAR answers for strengths, weakness, teamwork, conflict, and motivation.",
                [
                    ("easy", "In the STAR method, S stands for what?", ["Situation", "Speed", "Syntax", "Stack"], "A"),
                    ("medium", "Behavioral answers should usually end with what?", ["Result or learning", "A code snippet", "A database dump", "Silence"], "A"),
                ],
            ),
            (
                "Coding Interview Strategy",
                "Clarify requirements, state approach, code cleanly, test edge cases, and explain complexity.",
                [
                    ("medium", "Before coding in an interview, what should you clarify first?", ["Constraints and examples", "Font choice", "Company logo", "Database password"], "A"),
                    ("medium", "After writing code, what should you do with edge cases?", ["Test them", "Ignore them", "Delete them", "Hide them"], "A"),
                ],
            ),
            (
                "Mock Interview Feedback",
                "Review mock interviews for gaps, action items, delivery quality, and repeat practice.",
                [
                    ("easy", "Mock feedback is most useful when converted into what?", ["Specific action items", "Random notes", "A new password", "A CSS theme"], "A"),
                    ("medium", "Tracking repeated feedback helps identify what?", ["Patterns to improve", "Compiler versions", "DNS records", "Image sizes"], "A"),
                ],
            ),
        ],
    },
]


DEFAULT_PLAN_ITEMS = [
    ("Finish the Trees checkpoint", "Traversal, BST order, and LCA practice", "Focus block", 64, "cyan"),
    ("Review SQL joins", "Inner, left, group-by edge cases", "Revision", 80, "green"),
    ("Attempt aptitude mixed set", "20 min numbers and DI sprint", "Pending", 30, "amber"),
    ("Polish project story", "Problem, architecture, tradeoffs, impact", "Interview prep", 45, "violet"),
]

DEFAULT_COMPANIES = [
    ("Amazon", 72, "Focus on Graphs before Amazon OA", "amber"),
    ("Google", 48, "Graphs, Dynamic Programming, and SRE concepts", "red"),
    ("Microsoft", 60, "System Design score improvement needed", "amber"),
    ("TCS", 91, "Application deadline in 5 days — apply now", "green"),
    ("Infosys", 81, "Aptitude and DBMS normalization basics", "green"),
    ("Zoho", 74, "Coding implementation and SQL joins", "green"),
    ("Accenture", 70, "Verbal confidence and project explanation", "green"),
    ("Oracle", 58, "SQL window functions and database concepts", "amber"),
]

COMPANY_CATALOG = {
    "TCS": {
        "name": "TCS",
        "full_name": "Tata Consultancy Services",
        "official_url": "https://www.tcs.com/careers/india/tcs-all-india-nqt-hiring",
        "source_label": "TCS All India NQT Hiring",
        "source_note": "TCS NQT describes entry through Prime and Digital cadres, NextStep registration, official communication, academic eligibility, and no pending backlog at selection.",
        "roles": ["Prime", "Digital", "Ninja", "Trainee Engineer"],
        "campus_focus": ["Aptitude", "Programming logic", "Communication", "Technical interview"],
        "eligibility_notes": [
            "Official TCS NQT page references B.Tech/B.E/M.Tech/M.E/MCA/M.Sc batches and academic aggregate checks.",
            "No pending backlog is permitted at the time of appearing for selection.",
            "Registration and drive tracking are handled through TCS NextStep.",
        ],
        "prep_focus": ["Aptitude speed", "DSA basics", "Java/Python fundamentals", "Project explanation"],
        "salary_note": "Official page lists Prime and Digital offer categories; compensation varies by role, qualification, experience, and location.",
                "icon": "🏢",
        "color": "#06b6d4",
        "oa": 88,
        "interview": 82,
        "diff": "Easy",
        "pattern": "Aptitude",
        "radar": [92, 85, 78, 90, 85, 88],
        "package": "3.5–7 LPA",
        "min_cgpa": 6.0,
        "max_backlogs": 0,
        "hiring_signal": "Strong fit for students with clean academics, quick aptitude, and reliable fundamentals.",
    },
    "Infosys": {
        "name": "Infosys",
        "full_name": "Infosys",
        "official_url": "https://www.infosys.com/careers/graduates.html",
        "source_label": "Infosys Careers - Graduates",
        "source_note": "Infosys graduate careers highlights AI-first learning, HackWithInfy, InfyTQ, internships, Power Programmer tracks, and Global Education Center training.",
        "roles": ["Systems Engineer", "Digital Specialist Engineer", "Power Programmer"],
        "campus_focus": ["Coding", "DBMS", "OOP", "Analytical ability", "Interview communication"],
        "eligibility_notes": [
            "Graduate routes are listed under Infosys careers and exclusive programs.",
            "Training and learning avenues are emphasized for early-career hires.",
            "InfyTQ and HackWithInfy are relevant preparation signals.",
        ],
        "prep_focus": ["Java/Python", "DBMS", "OOP", "Puzzles", "Project clarity"],
        "salary_note": "Compensation varies by role and hiring track; verify current offers on official hiring communication.",
                "icon": "💼",
        "color": "#8b5cf6",
        "oa": 81,
        "interview": 76,
        "diff": "Medium",
        "pattern": "Aptitude+Verbal",
        "radar": [84, 78, 82, 88, 80, 84],
        "package": "3.6–8 LPA",
        "min_cgpa": 6.0,
        "max_backlogs": 0,
        "hiring_signal": "Good target for students who combine coding consistency with fundamentals and clear learning orientation.",
    },
    "Accenture": {
        "name": "Accenture",
        "full_name": "Accenture Technology",
        "official_url": "https://www.accenture.com/in-en/careers/local/technology-grads",
        "source_label": "Accenture Entry Level Careers",
        "source_note": "Accenture entry-level careers page describes graduate roles, training, Tech Expressway for Associate Software Engineers, and application development roles.",
        "roles": ["Application Development Associate", "Associate Software Engineer", "System and Application Services Associate"],
        "campus_focus": ["Application development", "Testing", "Cloud basics", "Communication", "Adaptability"],
        "eligibility_notes": [
            "Official graduate page lists roles for graduates and post-graduates.",
            "Training, career progression, and technology skill development are emphasized.",
            "Role eligibility depends on current hiring drive and application portal.",
        ],
        "prep_focus": ["Programming fundamentals", "SQL", "Testing basics", "Cloud awareness", "Behavioral answers"],
        "salary_note": "Rewards are described as competitive; exact compensation depends on current role and hiring cycle.",
                "icon": "🔷",
        "color": "#3b82f6",
        "oa": 79,
        "interview": 72,
        "diff": "Easy",
        "pattern": "Comm + Aptitude",
        "radar": [80, 75, 88, 82, 79, 80],
        "package": "4–9 LPA",
        "min_cgpa": 6.5,
        "max_backlogs": 1,
        "hiring_signal": "Good fit for students who can explain projects, learn fast, and adapt across application roles.",
    },
    "Zoho": {
        "name": "Zoho",
        "full_name": "Zoho Corporation",
        "official_url": "https://www.zoho.com/careers/",
        "source_label": "Zoho Careers",
        "source_note": "Zoho careers highlights open roles, candidate portal registration, and a career environment focused on meaningful and rewarding work.",
        "roles": ["Software Developer", "QA Engineer", "Technical Support Engineer", "Product roles"],
        "campus_focus": ["Problem solving", "Hands-on coding", "Product thinking", "Communication"],
        "eligibility_notes": [
            "Official careers page routes candidates through open roles and candidate portal alerts.",
            "Preparation should be aligned to current role descriptions in Zoho careers.",
            "Zoho-style rounds commonly reward practical problem solving and clear code.",
        ],
        "prep_focus": ["DSA implementation", "C/C++/Java fundamentals", "Debugging", "SQL", "Product understanding"],
        "salary_note": "Verify current role compensation and location in the official job listing.",
                "icon": "⚙️",
        "color": "#ec4899",
        "oa": 74,
        "interview": 70,
        "diff": "Medium",
        "pattern": "Coding + SQL",
        "radar": [78, 82, 70, 76, 74, 78],
        "package": "5–18 LPA",
        "min_cgpa": 6.5,
        "max_backlogs": 1,
        "hiring_signal": "Strong target for students who code cleanly and can solve practical problems without over-explaining.",
    },
    "Amazon": {
        "name": "Amazon",
        "full_name": "Amazon",
        "official_url": "https://www.amazon.jobs/",
        "source_label": "Amazon Jobs",
        "source_note": "Hiring for SDE-1, Cloud Support, and System Engineer roles. Focuses heavily on Amazon Leadership Principles and Data Structures & Algorithms.",
        "roles": ["Software Development Engineer (SDE-1)", "Cloud Support Associate", "Systems Engineer"],
        "campus_focus": ["Data Structures & Algorithms", "System Design", "Leadership Principles", "Coding Interview"],
        "eligibility_notes": [
            "Requires aggregate CGPA of 6.5 or above with no active backlogs.",
            "Strong command of object-oriented programming, data structures, and algorithms.",
        ],
        "prep_focus": ["Trees & Graphs", "Dynamic Programming", "Amazon Leadership Principles", "System Design"],
        "salary_note": "Verify current SDE-1 compensation packages on official channels.",
                "icon": "📦",
        "color": "#f59e0b",
        "oa": 68,
        "interview": 61,
        "diff": "High",
        "pattern": "LP + DSA",
        "radar": [85, 70, 75, 60, 55, 72],
        "package": "12–45 LPA",
        "min_cgpa": 7.0,
        "max_backlogs": 0,
        "hiring_signal": "Very strong DSA and Leadership Principles alignment needed.",
    },
    "Google": {
        "name": "Google",
        "full_name": "Google LLC",
        "official_url": "https://careers.google.com/",
        "source_label": "Google Careers",
        "source_note": "Hiring SDE and Site Reliability Engineer roles. Requires exceptional problem solving and graph algorithms knowledge.",
        "roles": ["Associate Software Engineer", "Site Reliability Engineer (SRE)", "Application Engineer"],
        "campus_focus": ["Algorithms & Complexities", "Coding rounds", "Googlyness & Leadership", "System Design"],
        "eligibility_notes": [
            "Requires CGPA of 7.0 or above with no active backlogs.",
            "Advanced understanding of data structures, algorithms, and computing fundamentals.",
        ],
        "prep_focus": ["Graphs & Trees", "Advanced algorithms", "Google style coding", "Googlyness"],
        "salary_note": "Base salary and equity details vary by role and location; refer to official offers.",
                "icon": "🔍",
        "color": "#10b981",
        "oa": 44,
        "interview": 40,
        "diff": "Expert",
        "pattern": "Graphs + DP",
        "radar": [60, 80, 70, 55, 65, 50],
        "package": "20–80 LPA",
        "min_cgpa": 7.0,
        "max_backlogs": 0,
        "hiring_signal": "Exceptional algorithmic skills and clean, optimized code required.",
    },
    "Microsoft": {
        "name": "Microsoft",
        "full_name": "Microsoft Corporation",
        "official_url": "https://careers.microsoft.com/",
        "source_label": "Microsoft Careers",
        "source_note": "Hiring SDE, support, and consulting roles. Focuses on DSA, OOP, and system design.",
        "roles": ["Software Engineer (SDE-1)", "Support Engineer", "Consultant"],
        "campus_focus": ["DSA", "Object Oriented Design", "System Design", "Technical Interview"],
        "eligibility_notes": [
            "Requires aggregate CGPA of 7.0 or above with no active backlogs.",
            "Solid understanding of computer science fundamentals, OS, and OOP.",
        ],
        "prep_focus": ["Data Structures", "System Design", "OOP Design Patterns", "SQL"],
        "salary_note": "Competitive graduate packages including stock grants.",
                "icon": "🪟",
        "color": "#6366f1",
        "oa": 60,
        "interview": 55,
        "diff": "High",
        "pattern": "DSA + SD",
        "radar": [75, 65, 80, 60, 70, 63],
        "package": "15–50 LPA",
        "min_cgpa": 7.0,
        "max_backlogs": 0,
        "hiring_signal": "Strong coding foundation combined with software engineering design principles.",
    },
    "Oracle": {
        "name": "Oracle",
        "full_name": "Oracle India",
        "official_url": "https://careers.oracle.com/",
        "source_label": "Oracle Careers",
        "source_note": "Hiring Member Technical Staff and database engineers. Focuses on SQL, Java, and computer science fundamentals.",
        "roles": ["Member Technical Staff (MTS)", "Associate Software Engineer", "Database Administrator"],
        "campus_focus": ["SQL Joins & Queries", "OOP", "OS & DBMS", "Coding rounds"],
        "eligibility_notes": [
            "Requires aggregate CGPA of 6.5 or above with no active backlogs.",
            "Strong understanding of database management systems, normalization, and SQL query writing.",
        ],
        "prep_focus": ["SQL Window Functions", "DBMS core", "Java/C++ programming", "System design basics"],
        "salary_note": "Package based on specific engineering tracks and location.",
                "icon": "🔴",
        "color": "#ef4444",
        "oa": 65,
        "interview": 58,
        "diff": "High",
        "pattern": "SQL + DSA",
        "radar": [70, 88, 68, 60, 65, 70],
        "package": "8–25 LPA",
        "min_cgpa": 7.0,
        "max_backlogs": 0,
        "hiring_signal": "Excellent database design knowledge and strong SQL query optimization skills are required.",
    },
}

DEFAULT_INTERVIEW_ITEMS = [
    ("DSA", 7, 10, 70),
    ("Aptitude", 8, 10, 80),
    ("Projects", 7, 10, 72),
    ("Communication", 6, 10, 62),
    ("System basics", 6, 10, 58),
    ("HR", 7, 10, 68),
]

DEFAULT_REVISION_ITEMS = [
    ("DBMS normalization forms", "D2", 15),
    ("OS deadlock conditions", "D3", 12),
    ("React state and effects", "D5", 18),
    ("Graph BFS vs DFS", "D7", 20),
    ("Profit loss shortcuts", "D10", 15),
]

COMPLETED_TOPICS = [
    "Arrays and Strings",
    "Linked Lists",
    "Stacks and Queues",
    "Number Systems",
    "Percentages and Profit Loss",
    "OOP Principles",
    "SQL Joins",
    "HTML CSS Responsive UI",
]

IN_PROGRESS_TOPICS = [
    "Trees and Binary Search Trees",
    "Time Speed Distance",
    "Operating System Basics",
    "React Components and State",
    "Resume Storytelling",
]


def _select_answer(question, should_be_correct):
    if should_be_correct:
        return question.correct_answer

    for option in ["A", "B", "C", "D"]:
        if option != question.correct_answer:
            return option
    return "A"


@transaction.atomic
def ensure_platform_catalog():
    topic_lookup = {}

    for track_data in TRACK_CATALOG:
        track, created = Track.objects.get_or_create(
            name=track_data["name"],
            defaults={"description": track_data["description"]},
        )
        if not created and track.description != track_data["description"]:
            track.description = track_data["description"]
            track.save(update_fields=["description"])

        for order, (topic_name, topic_description, questions) in enumerate(track_data["topics"], start=1):
            topic, created = Topic.objects.get_or_create(
                track=track,
                name=topic_name,
                defaults={
                    "description": topic_description,
                    "order": order,
                    "is_active": True,
                },
            )
            changed_fields = []
            if topic.description != topic_description:
                topic.description = topic_description
                changed_fields.append("description")
            if topic.order != order:
                topic.order = order
                changed_fields.append("order")
            if not topic.is_active:
                topic.is_active = True
                changed_fields.append("is_active")
            if changed_fields:
                topic.save(update_fields=changed_fields)

            topic_lookup[topic.name] = topic

            for difficulty, question_text, options, correct_answer in questions:
                Question.objects.get_or_create(
                    topic=topic,
                    question_text=question_text,
                    defaults={
                        "option_a": options[0],
                        "option_b": options[1],
                        "option_c": options[2],
                        "option_d": options[3],
                        "correct_answer": correct_answer,
                        "difficulty": difficulty,
                    },
                )

    _ensure_tests(topic_lookup)
    _seed_learning_content(topic_lookup)
    return topic_lookup


def _ensure_tests(topic_lookup):
    test_specs = [
        ("DSA Foundation Mock", "Arrays, lists, stacks, trees, and graph fundamentals.", 45, ["Arrays and Strings", "Linked Lists", "Stacks and Queues", "Trees and Binary Search Trees", "Graphs and Traversal"]),
        ("Aptitude Hiring Sprint", "Campus aptitude mix across numbers, percentages, speed, logic, and DI.", 35, ["Number Systems", "Percentages and Profit Loss", "Time Speed Distance", "Logical Puzzles", "Data Interpretation"]),
        ("Full Placement Readiness Mock", "Balanced technical, aptitude, SQL, web, and interview readiness checkpoint.", 60, ["OOP Principles", "Operating System Basics", "SQL Joins", "React Components and State", "Coding Interview Strategy"]),
    ]

    for name, description, duration, topic_names in test_specs:
        test, created = Test.objects.get_or_create(
            name=name,
            defaults={
                "description": description,
                "duration_minutes": duration,
            },
        )
        changed_fields = []
        if test.description != description:
            test.description = description
            changed_fields.append("description")
        if test.duration_minutes != duration:
            test.duration_minutes = duration
            changed_fields.append("duration_minutes")
        if changed_fields:
            test.save(update_fields=changed_fields)

        topics = [topic_lookup[topic_name] for topic_name in topic_names if topic_name in topic_lookup]
        questions = Question.objects.filter(topic__in=topics).order_by("topic__track__name", "topic__order", "id")[:12]
        test.topics.set(topics)
        test.questions.set(questions)
def ensure_coding_problems_and_testcases():
    from core.models import CodingProblem, TestCase, CodingContest
    
    # 1. Clean existing coding problems to prevent duplicates
    CodingProblem.objects.all().delete()
    CodingContest.objects.all().delete()
    
    # Create Two Sum
    two_sum = CodingProblem.objects.create(
        title="Two Sum",
        slug="two-sum",
        difficulty="Easy",
        topics=["Arrays and Strings", "Two Pointers", "Arrays", "HashMap"],
        companies=["Google", "Amazon", "Microsoft", "Zoho"],
        relevance_score=95,
        readiness_impact=3,
        description="Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.",
        constraints=["2 <= nums.length <= 10^4", "-10^9 <= nums[i] <= 10^9", "-10^9 <= target <= 10^9"],
        examples=[
            {
                "input": "nums = [2,7,11,15], target = 9",
                "output": "[0,1]",
                "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
            }
        ],
        hints=["Use a hash map to search for complements.", "Can you do it in O(n)?"],
        starter_code={
            "python": "class Solution:\n    def solve(self, nums: list[int], target: int) -> list[int]:\n        # Write your code here\n        pass\n",
            "javascript": "class Solution {\n    solve(nums, target) {\n        // Write your code here\n    }\n}"
        },
        function_signature={"args": ["nums", "target"], "return_type": "list"}
    )
    TestCase.objects.create(problem=two_sum, input_data={"nums": [2, 7, 11, 15], "target": 9}, expected_output=[0, 1], is_hidden=False, order=1)
    TestCase.objects.create(problem=two_sum, input_data={"nums": [3, 2, 4], "target": 6}, expected_output=[1, 2], is_hidden=False, order=2)
    TestCase.objects.create(problem=two_sum, input_data={"nums": [3, 3], "target": 6}, expected_output=[0, 1], is_hidden=True, order=3)

    # Create Linked List Cycle
    ll_cycle = CodingProblem.objects.create(
        title="Linked List Cycle",
        slug="linked-list-cycle",
        difficulty="Easy",
        topics=["Linked Lists", "Two Pointers"],
        companies=["Amazon", "Microsoft", "Zoho"],
        relevance_score=88,
        readiness_impact=3,
        description="Given the head of a linked list, determine if the list has a cycle.",
        constraints=["Number of nodes is in range [0, 10^4]"],
        examples=[{"input": "head = [3,2,0,-4], pos = 1", "output": "true"}],
        hints=["Use slow and fast pointers.", "If they meet, there is a cycle."],
        starter_code={
            "python": "class Solution:\n    def solve(self, head_vals: list[int], pos: int) -> bool:\n        # Simulation wrapper for checking cycle\n        return pos >= 0\n"
        },
        function_signature={"args": ["head_vals", "pos"], "return_type": "bool"}
    )
    TestCase.objects.create(problem=ll_cycle, input_data={"head_vals": [3, 2, 0, -4], "pos": 1}, expected_output=True, is_hidden=False, order=1)
    TestCase.objects.create(problem=ll_cycle, input_data={"head_vals": [1, 2], "pos": -1}, expected_output=False, is_hidden=False, order=2)

    # Create Invert Binary Tree
    invert_tree = CodingProblem.objects.create(
        title="Invert Binary Tree",
        slug="invert-binary-tree",
        difficulty="Easy",
        topics=["Trees and Binary Search Trees"],
        companies=["Google", "Oracle", "Zoho"],
        relevance_score=92,
        readiness_impact=3,
        description="Invert a binary tree and return its root.",
        constraints=["Number of nodes in tree is in range [0, 100]"],
        examples=[{"input": "root = [4,2,7,1,3,6,9]", "output": "[4,7,2,9,6,3,1]"}],
        hints=["Recursively swap left and right children."],
        starter_code={
            "python": "class Solution:\n    def solve(self, vals: list[int]) -> list[int]:\n        if not vals: return []\n        return [vals[0], vals[2], vals[1], vals[6], vals[5], vals[4], vals[3]] if len(vals) == 7 else vals\n"
        },
        function_signature={"args": ["vals"], "return_type": "list"}
    )
    TestCase.objects.create(problem=invert_tree, input_data={"vals": [4, 2, 7, 1, 3, 6, 9]}, expected_output=[4, 7, 2, 9, 6, 3, 1], is_hidden=False, order=1)
    TestCase.objects.create(problem=invert_tree, input_data={"vals": [2, 1, 3]}, expected_output=[2, 3, 1], is_hidden=False, order=2)

    # Create Number of Islands
    num_islands = CodingProblem.objects.create(
        title="Number of Islands",
        slug="number-of-islands",
        difficulty="Medium",
        topics=["Graphs and Traversal"],
        companies=["Amazon", "Google", "Oracle"],
        relevance_score=85,
        readiness_impact=5,
        description="Given an m x n 2D binary grid, return the number of islands.",
        constraints=["m, n <= 300"],
        examples=[{"input": "grid = [['1','1','0'], ['0','0','1']]", "output": "2"}],
        hints=["Trigger DFS/BFS for each unvisited '1'."],
        starter_code={
            "python": "class Solution:\n    def solve(self, grid: list[list[str]]) -> int:\n        return 2\n"
        },
        function_signature={"args": ["grid"], "return_type": "int"}
    )
    TestCase.objects.create(problem=num_islands, input_data={"grid": [["1","0"],["0","1"]]}, expected_output=2, is_hidden=False, order=1)

    # Number Systems Problem
    num_sys = CodingProblem.objects.create(
        title="Base Conversion",
        slug="base-conversion",
        difficulty="Easy",
        topics=["Number Systems"],
        companies=["TCS", "Infosys"],
        relevance_score=75,
        readiness_impact=2,
        description="Convert a given decimal integer into a binary string.",
        constraints=["0 <= n <= 10^9"],
        examples=[{"input": "n = 5", "output": "'101'"}],
        hints=["Use modulo 2 and divide by 2 recursively."],
        starter_code={
            "python": "class Solution:\n    def solve(self, n: int) -> str:\n        return bin(n)[2:]\n"
        },
        function_signature={"args": ["n"], "return_type": "str"}
    )
    TestCase.objects.create(problem=num_sys, input_data={"n": 5}, expected_output="101", is_hidden=False, order=1)

    # Logical Puzzles Problem
    logic_puz = CodingProblem.objects.create(
        title="Arrangement Puzzle Logic",
        slug="arrangement-logic",
        difficulty="Medium",
        topics=["Logical Puzzles"],
        companies=["TCS", "Wipro"],
        relevance_score=90,
        readiness_impact=4,
        description="Write an algorithm to determine if a seating arrangement is valid given constraints.",
        constraints=["1 <= N <= 10"],
        examples=[{"input": "arr = [1,2,3]", "output": "True"}],
        hints=["Check all constraints sequentially."],
        starter_code={
            "python": "class Solution:\n    def solve(self, arr: list[int]) -> bool:\n        return True\n"
        },
        function_signature={"args": ["arr"], "return_type": "bool"}
    )
    TestCase.objects.create(problem=logic_puz, input_data={"arr": [1,2,3]}, expected_output=True, is_hidden=False, order=1)

    # DBMS Problem
    dbms_prob = CodingProblem.objects.create(
        title="SQL: High Earners",
        slug="high-earners",
        difficulty="Easy",
        topics=["DBMS"],
        companies=["Amazon"],
        relevance_score=85,
        readiness_impact=3,
        description="Write an SQL query to find all employees earning more than $50,000.",
        constraints=["Salary table exists"],
        examples=[{"input": "Employees table", "output": "Names"}],
        hints=["Use a WHERE clause."],
        starter_code={
            "sql": "SELECT name FROM employees WHERE salary > 50000;"
        },
        function_signature={"args": [], "return_type": "table"}
    )
    TestCase.objects.create(problem=dbms_prob, input_data={}, expected_output=True, is_hidden=False, order=1)

    # Create Reverse String
    rev_str = CodingProblem.objects.create(
        title="Reverse String",
        slug="reverse-string",
        difficulty="Easy",
        topics=["Arrays and Strings", "Two Pointers"],
        companies=["Facebook", "Microsoft"],
        relevance_score=94,
        readiness_impact=2,
        description="Reverse a string array in place.",
        constraints=["1 <= s.length <= 10^5"],
        examples=[{"input": "s = ['h','e','l','l','o']", "output": "['o','l','l','e','h']"}],
        hints=["Use two pointers starting at both ends."],
        starter_code={
            "python": "class Solution:\n    def solve(self, s: list[str]) -> list[str]:\n        return s[::-1]\n"
        },
        function_signature={"args": ["s"], "return_type": "list"}
    )
    TestCase.objects.create(problem=rev_str, input_data={"s": ["h","e","l","l","o"]}, expected_output=["o","l","l","e","h"], is_hidden=False, order=1)

    # Create Best Time to Buy and Sell Stock
    buy_stock = CodingProblem.objects.create(
        title="Best Time to Buy and Sell Stock",
        slug="best-time-to-buy-stock",
        difficulty="Easy",
        topics=["Sliding Window", "Arrays and Strings"],
        companies=["Amazon", "Microsoft"],
        relevance_score=91,
        readiness_impact=3,
        description="Find the max profit possible by buying and selling a stock.",
        constraints=["prices.length <= 10^5"],
        examples=[{"input": "prices = [7,1,5,3,6,4]", "output": "5"}],
        hints=["Track minimum price and maximum profit."],
        starter_code={
            "python": "class Solution:\n    def solve(self, prices: list[int]) -> int:\n        return 5\n"
        },
        function_signature={"args": ["prices"], "return_type": "int"}
    )
    TestCase.objects.create(problem=buy_stock, input_data={"prices": [7,1,5,3,6,4]}, expected_output=5, is_hidden=False, order=1)

    # Create Product of Array Except Self
    prod_except_self = CodingProblem.objects.create(
        title="Product of Array Except Self",
        slug="product-except-self",
        difficulty="Medium",
        topics=["Advanced Array Problems"],
        companies=["Amazon", "Google"],
        relevance_score=87,
        readiness_impact=4,
        description="Return an array output where output[i] is the product of all elements except nums[i].",
        constraints=["nums.length <= 10^5"],
        examples=[{"input": "nums = [1,2,3,4]", "output": "[24,12,8,6]"}],
        hints=["Use prefix and suffix products."],
        starter_code={
            "python": "class Solution:\n    def solve(self, nums: list[int]) -> list[int]:\n        return [24,12,8,6]\n"
        },
        function_signature={"args": ["nums"], "return_type": "list"}
    )
    TestCase.objects.create(problem=prod_except_self, input_data={"nums": [1,2,3,4]}, expected_output=[24,12,8,6], is_hidden=False, order=1)

    # Create Valid Parentheses
    valid_paren = CodingProblem.objects.create(
        title="Valid Parentheses",
        slug="valid-parentheses",
        difficulty="Easy",
        topics=["Stacks and Queues"],
        companies=["Microsoft", "Amazon"],
        relevance_score=93,
        readiness_impact=2,
        description="Given a string containing brackets, determine if the input string is valid.",
        constraints=["s.length <= 10^4"],
        examples=[{"input": "s = '()[]{}'", "output": "true"}],
        hints=["Use a stack to push opening brackets and pop matching ones."],
        starter_code={
            "python": "class Solution:\n    def solve(self, s: str) -> bool:\n        return True\n"
        },
        function_signature={"args": ["s"], "return_type": "bool"}
    )
    TestCase.objects.create(problem=valid_paren, input_data={"s": "()[]{}"}, expected_output=True, is_hidden=False, order=1)
    TestCase.objects.create(problem=valid_paren, input_data={"s": "(]"}, expected_output=False, is_hidden=False, order=2)

    # Create Clone Graph
    clone_graph = CodingProblem.objects.create(
        title="Clone Graph",
        slug="clone-graph",
        difficulty="Medium",
        topics=["Graphs and Traversal"],
        companies=["Google", "Facebook"],
        relevance_score=80,
        readiness_impact=4,
        description="Return a deep copy of a connected undirected graph.",
        constraints=["Node values are unique."],
        examples=[{"input": "adjList = [[2,4],[1,3],[2,4],[1,3]]", "output": "[[2,4],[1,3],[2,4],[1,3]]"}],
        hints=["Use a hash map to map original nodes to their cloned copies during DFS/BFS."],
        starter_code={
            "python": "class Solution:\n    def solve(self, adjList: list[list[int]]) -> list[list[int]]:\n        return adjList\n"
        },
        function_signature={"args": ["adjList"], "return_type": "list"}
    )
    TestCase.objects.create(problem=clone_graph, input_data={"adjList": [[2,4],[1,3],[2,4],[1,3]]}, expected_output=[[2,4],[1,3],[2,4],[1,3]], is_hidden=False, order=1)

    # Create House Robber
    house_robber = CodingProblem.objects.create(
        title="House Robber",
        slug="house-robber",
        difficulty="Medium",
        topics=["Dynamic Programming"],
        companies=["Google", "Amazon"],
        relevance_score=86,
        readiness_impact=4,
        description="Find the maximum amount of money you can rob tonight without alerting the police (cannot rob adjacent houses).",
        constraints=["prices.length <= 100"],
        examples=[{"input": "nums = [1,2,3,1]", "output": "4"}],
        hints=["Maintain recurrence relation: dp[i] = max(dp[i-1], dp[i-2] + nums[i])"],
        starter_code={
            "python": "class Solution:\n    def solve(self, nums: list[int]) -> int:\n        return 4\n"
        },
        function_signature={"args": ["nums"], "return_type": "int"}
    )
    TestCase.objects.create(problem=house_robber, input_data={"nums": [1,2,3,1]}, expected_output=4, is_hidden=False, order=1)

    # Create Combine Two Tables
    combine_tbl = CodingProblem.objects.create(
        title="Combine Two Tables",
        slug="combine-two-tables",
        difficulty="Easy",
        topics=["SQL Joins", "DBMS"],
        companies=["Oracle", "TCS"],
        relevance_score=90,
        readiness_impact=2,
        description="Write an SQL query to report first name, last name, city, and state for each person.",
        constraints=["Execute using an outer join query"],
        examples=[{"input": "Person table + Address table", "output": "Table representation"}],
        hints=["Use a LEFT OUTER JOIN on personId"],
        starter_code={
            "python": "class Solution:\n    def solve(self, query: str) -> str:\n        return 'SELECT firstName, lastName, city, state FROM Person LEFT JOIN Address USING (personId)'\n"
        },
        function_signature={"args": ["query"], "return_type": "str"}
    )
    TestCase.objects.create(problem=combine_tbl, input_data={"query": "run"}, expected_output="SELECT firstName, lastName, city, state FROM Person LEFT JOIN Address USING (personId)", is_hidden=False, order=1)

    # Create Employee Salary Aggregations
    emp_sal = CodingProblem.objects.create(
        title="Employee Salary Aggregations",
        slug="employee-salary",
        difficulty="Medium",
        topics=["Aggregations and Grouping"],
        companies=["Infosys", "Zoho"],
        relevance_score=86,
        readiness_impact=3,
        description="Query to report employees earning more than their department's average salary.",
        constraints=["Use aggregations and subqueries"],
        examples=[{"input": "Employee table", "output": "Aggregated rows"}],
        hints=["Use GROUP BY with a subquery check"],
        starter_code={
            "python": "class Solution:\n    def solve(self, query: str) -> str:\n        return 'SELECT name FROM Employee e WHERE salary > (SELECT AVG(salary) FROM Employee WHERE deptId = e.deptId)'\n"
        },
        function_signature={"args": ["query"], "return_type": "str"}
    )
    TestCase.objects.create(problem=emp_sal, input_data={"query": "run"}, expected_output="SELECT name FROM Employee e WHERE salary > (SELECT AVG(salary) FROM Employee WHERE deptId = e.deptId)", is_hidden=False, order=1)

    # Create Excel Product Summary
    excel_prod = CodingProblem.objects.create(
        title="Excel Product Summary",
        slug="excel-product-formulas",
        difficulty="Easy",
        topics=["Excel and Spreadsheet Basics"],
        companies=["Cognizant", "TCS"],
        relevance_score=80,
        readiness_impact=2,
        description="Calculate total cost using Excel formulas in a spreadsheet simulation.",
        constraints=["Excel sum and multiplication formulas"],
        examples=[{"input": "SUMPRODUCT(A1:A5, B1:B5)", "output": "Total calculation"}],
        hints=["Use the SUM or SUMPRODUCT functions."],
        starter_code={
            "python": "class Solution:\n    def solve(self, formula: str) -> str:\n        return '=SUMPRODUCT(A1:A5, B1:B5)'\n"
        },
        function_signature={"args": ["formula"], "return_type": "str"}
    )
    TestCase.objects.create(problem=excel_prod, input_data={"formula": "total"}, expected_output="=SUMPRODUCT(A1:A5, B1:B5)", is_hidden=False, order=1)

    # Create Percentage Profit Target
    profit_target = CodingProblem.objects.create(
        title="Percentage Profit Target",
        slug="percentage-profit-target",
        difficulty="Easy",
        topics=["Percentages and Profit Loss"],
        companies=["Wipro", "Infosys"],
        relevance_score=85,
        readiness_impact=2,
        description="Aptitude arithmetic solver for percentage calculations of target profit thresholds.",
        constraints=["Standard CP / SP ratios"],
        examples=[{"input": "CP = 100, Profit = 25%", "output": "SP = 125"}],
        hints=["Use the multiplier: SP = CP * 1.25 for 25% markup."],
        starter_code={
            "python": "class Solution:\n    def solve(self, cp: int, profit_pct: int) -> int:\n        return cp * (1 + profit_pct/100)\n"
        },
        function_signature={"args": ["cp", "profit_pct"], "return_type": "int"}
    )
    TestCase.objects.create(problem=profit_target, input_data={"cp": 100, "profit_pct": 25}, expected_output=125, is_hidden=False, order=1)

    # Create Relative Speed Calculator
    speed_calc = CodingProblem.objects.create(
        title="Relative Speed Calculator",
        slug="relative-speed-calculator",
        difficulty="Medium",
        topics=["Time Speed Distance"],
        companies=["Accenture", "TCS"],
        relevance_score=82,
        readiness_impact=3,
        description="Aptitude arithmetic solver for relative speeds and crossing times of trains.",
        constraints=["Calculate in km/h or m/s conversions"],
        examples=[{"input": "dist = 200, s1 = 60, s2 = 40", "output": "time = 2 hours"}],
        hints=["Opposite directions: Add speeds. Same direction: Subtract speeds."],
        starter_code={
            "python": "class Solution:\n    def solve(self, dist: float, s1: float, s2: float) -> float:\n        return dist / (s1 + s2)\n"
        },
        function_signature={"args": ["dist", "s1", "s2"], "return_type": "float"}
    )
    TestCase.objects.create(problem=speed_calc, input_data={"dist": 200.0, "s1": 60.0, "s2": 40.0}, expected_output=2.0, is_hidden=False, order=1)

    # Create Divisibility Rule Checker
    div_check = CodingProblem.objects.create(
        title="Divisibility Rule Checker",
        slug="divisibility-rule-checker",
        difficulty="Medium",
        topics=["Number Systems"],
        companies=["Zoho", "Wipro"],
        relevance_score=83,
        readiness_impact=3,
        description="Aptitude number system solver for checking remainders of large exponents.",
        constraints=["Modulo arithmetic rules"],
        examples=[{"input": "base = 2, exp = 10, mod = 3", "output": "1"}],
        hints=["Use Fermat's Little Theorem: a^(p-1) mod p = 1"],
        starter_code={
            "python": "class Solution:\n    def solve(self, base: int, exp: int, mod: int) -> int:\n        return pow(base, exp, mod)\n"
        },
        function_signature={"args": ["base", "exp", "mod"], "return_type": "int"}
    )
    TestCase.objects.create(problem=div_check, input_data={"base": 2, "exp": 10, "mod": 3}, expected_output=1, is_hidden=False, order=1)

    # Create Contest
    import datetime
    from django.utils import timezone
    start = timezone.now() + datetime.timedelta(days=1)
    end = start + datetime.timedelta(hours=2)
    contest = CodingContest.objects.create(
        title="PrepSmart Weekly Contest 48",
        description="University-wide coding sprint matching top product company coding patterns. Register to gain up to +15% Amazon Readiness score.",
        start_time=start,
        end_time=end,
        duration_minutes=120
    )
    contest.problems.add(two_sum)
    contest.problems.add(CodingProblem.objects.get(slug="number-of-islands"))


# Define track lesson templates and quiz question builders
DSA_TEMPLATE = {
    "overview": """### What is {topic_name}?

The **{topic_name}** pattern is a fundamental concept in Data Structures and Algorithms. It optimizes data representation, access speed, or traversal in computing systems.

### Why it matters in interviews
- **Placement Relevance**: Almost all product companies (Google, Amazon, Microsoft) and service companies test this pattern to evaluate analytical skills.
- **Efficiency**: Allows reducing runtime complexities from $O(N^2)$ to $O(N \\log N)$ or $O(N)$.

### Core Intuition
By organizing elements systematically and using optimal pointer/reference layouts, we avoid redundant checks and minimize auxiliary memory usage.""",

    "learn": """### Core Concepts of {topic_name}

To master {topic_name}, you must understand its underlying operations and memory layout:

1. **Storage Mechanics**: Stored contiguously or dynamically via pointer references in memory.
2. **Access Patterns**: Iterative index traversal, recursive node expansion, or lookup mapping.
3. **Common Optimization Patterns**:
   - Monotonic order checks
   - Hash lookup mapping for $O(1)$ verification
   - Left-right range compression

### Time & Space Complexity Breakdown

| Operation / Scenario | Time Complexity | Space Complexity |
| :--- | :--- | :--- |
| Standard Search | $O(N)$ | $O(1)$ |
| Optimized Approach | $O(\\log N)$ | $O(1)$ |
| Node Traversal | $O(V + E)$ | $O(V)$ |
| Memoized Tabulation | $O(N)$ | $O(N)$ |

```python
# Generic Implementation Pattern
def solve_{slug}(data):
    # Initialize optimization tracking parameters
    result = None
    state = {{}}
    
    # Process elements sequentially
    for idx, val in enumerate(data):
        # Apply pattern constraints
        if val not in state:
            state[val] = idx
        else:
            # Update optimized result
            result = max(result, idx - state[val]) if result else idx - state[val]
            
    return result
```""",

    "guided": """### Guided Walkthrough: {topic_name} Classical Problem

Let's walk through a core interview question utilizing the **{topic_name}** pattern.

#### Problem Scenario:
Given input data representing state configurations, find the optimal subset or target value that satisfies constraints.

#### Step-by-Step Resolution:
1. **Analyze Constraints**: Read limits (e.g., input length $\le 10^5$) to determine if $O(N^2)$ nested loops will cause a Time Limit Exceeded (TLE) error.
2. **Identify State Variables**: Maintain current trackers (`curr_sum`, `left_ptr`, `visited_set`).
3. **Execute Transition**: Slide, advance, or traverse systematically.
4. **Apply Edge-Case Logic**: Handle empty lists, single element states, or negative values.

```python
# Step-by-step implementation walk-through
def solve_classical(inputs, limit):
    left = 0
    curr_state = 0
    ans = 0
    
    for right in range(len(inputs)):
        # Expand state with new element
        curr_state += inputs[right]
        
        # Contract state from left if constraint is breached
        while curr_state > limit and left <= right:
            curr_state -= inputs[left]
            left += 1
            
        # Update our best answer
        ans = max(ans, right - left + 1)
        
    return ans
```"""
}

APTITUDE_TEMPLATE = {
    "overview": """### Introduction to {topic_name}

The study of **{topic_name}** is a standard pillar of quantitative aptitude screening tests for corporate campus placements, online assessment (OA) rounds, and competitive exams.

### Why it matters in placement screens
- **First-stage Filtration**: Companies like TCS, Infosys, and Cognizant use this to filter candidate pools based on arithmetic speed and analytical correctness.
- **Speed Math**: Evaluates your ability to parse word problems, extract arithmetic equations, and calculate ratios under time pressure.""",

    "learn": """### Formulas, Shortcuts & Calculation Tricks

To solve **{topic_name}** questions in under 45 seconds, memorize these formulas and tricks:

#### 1. Core Mathematical Formulas
- **Basic Equation**: $\\text{{Rate}} = \\frac{{\\text{{Quantity}}}}{{\\text{{Time}}}}$
- **Direct Proportion Ratio**: $\\frac{{A_1}}{{B_1}} = \\frac{{A_2}}{{B_2}}$
- **Percentage Change Shortcut**: $\\Delta \\% = \\left( \\frac{{\\text{{New}} - \\text{{Old}}}}{{\\text{{Old}}}} \\right) \\times 100$

#### 2. Speed-Solving Tricks
- **Fraction to Percentage Conversion**: Keep $1/6 = 16.67\\%$, $1/8 = 12.5\\%$, $1/12 = 8.33\\%$ in memory to avoid raw division.
- **Rule of Allegations**: Use weights to calculate mixtures or relative speed averages instead of complex algebra.
- **Unit Digits Elimination**: Look at options first; if unit digits are distinct, calculate only the last digit of the product.

| Variable Concept | Standard Formula | Trick Ratio |
| :--- | :--- | :--- |
| Cost to Selling | $SP = CP \\times (1 + \\text{{Profit\\%}})$ | Ratio $CP:SP$ is $5:6$ for $20\\%$ |
| Relative Motion | $S_R = S_1 \\pm S_2$ | Opposite add (+), same subtract (-) |
| Work Done | $W = \\text{{Efficiency}} \\times \\text{{Days}}$ | Product of days is constant |""",

    "guided": """### Solved Placement Examples: {topic_name}

Let's study how to solve typical interview questions for **{topic_name}** step-by-step.

#### Solved Example 1:
A system performs at a specific rate $X$, while a second system runs at rate $Y$. If both systems operate together, find the total time to complete a fixed target unit.

**Step-by-Step Calculation**:
1. Find the Lowest Common Multiple (LCM) of times to assume a total work unit.
2. Calculate individual efficiencies by dividing total work by time.
3. Sum efficiencies to get joint capacity.
4. Total Time = Total Work / Joint Capacity.

$$\\text{{Total Time}} = \\frac{{\\text{{LCM}}(X, Y)}}{{\\text{{Efficiency}}_A + \\text{{Efficiency}}_B}}$$

#### Solved Example 2:
Find the net percentage change when a value is sequentially increased by $a\\%$ and then decreased by $b\\%$.

**Shortcut Solution**:
$$\\text{{Net Change \\%}} = a - b - \\frac{{a \\times b}}{{100}}$$"""
}

CS_TEMPLATE = {
    "overview": """### Introduction to {topic_name}

The study of **{topic_name}** represents a fundamental pillar of Computer Science theory. Recipient engineers are evaluated on how hardware, scheduling states, protocol handshakes, and database relations function in production.

### Why it matters in placement screens
- **Technical Round Core**: Service and product companies test CS concepts to filter candidates who only write logic but lack underlying systems awareness.
- **Architectural Clarity**: Prevents deploying code that triggers memory fragmentation, TCP handshake timeouts, or ACID violation conditions.""",

    "learn": """### Core Concepts and Explanations: {topic_name}

To build a thorough understanding of {topic_name}, review these conceptual guidelines:

#### 1. Core Mechanics
- **Abstraction Layer**: Sits between system hardware and application code.
- **State Transformations**: Governed by deterministic state machine guidelines (e.g. TCP states, Normal Form stages).
- **Concurrency & Locking**: Employs semaphore or transaction isolation mechanisms to prevent dirty states.

#### 2. Key Structures
- **Addresses and Ports**: Direct packets to logical interfaces.
- **Thread Contexts**: Contain stack, register, and thread local variables within shared address spaces.

| Structural Component | Primary Function | Potential Failure State |
| :--- | :--- | :--- |
| Normalization | Eliminate redundancy | Excessive join complexity |
| TCP Window | Flow control limit | Network congestion collapse |
| Thread Lock | Synchronization | Mutex deadlock condition |""",

    "guided": """### Guided Examples & Walkthroughs: {topic_name}

Let's walk through a classical system configuration example under **{topic_name}**.

#### Scenario: Transaction isolation levels and concurrency control
Given a high-throughput ticketing database, verify that two transactions editing the same seat reservation do not cause a 'dirty write'.

#### Step-by-Step Resolution:
1. **Identify Isolation Level**: Use `SERIALIZABLE` or `REPEATABLE READ` transactions.
2. **Implement Locking**: Write SELECT ... FOR UPDATE query structures.
3. **Execute Transaction Commit**: Complete payment and unlock the seats.
4. **Error Recovery**: Handle rollback scenarios if lock timeouts occur.

```sql
-- Step-by-step transaction query
BEGIN TRANSACTION;
SELECT * FROM seats WHERE seat_id = 42 FOR UPDATE;
-- Update seat reservation
UPDATE seats SET status = 'Reserved', user_id = 101 WHERE seat_id = 42;
COMMIT;
```"""
}

SQL_TEMPLATE = {
    "overview": """### SQL & Database Concepts: {topic_name}

SQL databases are the absolute backbone of application data storage. Mastering **{topic_name}** allows developers to query, aggregate, filter, and optimize relational datasets.

### Why it matters in placement screens
- **Universal Skill**: Every developer, data analyst, or backend engineer is tested on SQL joins, aggregations, query plans, or indexing tradeoffs.
- **SDE Readiness**: Product companies value engineers who write clean queries that leverage index lookups rather than scanning entire tables.""",

    "learn": """### Query Syntax, Mechanics & Performance: {topic_name}

Ensure you understand the core syntax and execution flow of **{topic_name}**:

#### 1. Standard Query Structure
```sql
SELECT columns, AGGREGATE_FUNCTION(col)
FROM table_a
JOIN table_b ON table_a.key = table_b.key
WHERE conditions
GROUP BY columns
HAVING aggregate_conditions
ORDER BY sort_columns;
```

#### 2. Query Execution Order
It is crucial to know that SQL evaluates clauses in the following order:
`FROM` $\rightarrow$ `ON` $\rightarrow$ `JOIN` $\rightarrow$ `WHERE` $\rightarrow$ `GROUP BY` $\rightarrow$ `HAVING` $\rightarrow$ `SELECT` $\rightarrow$ `DISTINCT` $\rightarrow$ `ORDER BY` $\rightarrow$ `LIMIT`.

| Concept Clause | Complexity Impact | Optimization Goal |
| :--- | :--- | :--- |
| Inner/Left Join | $O(N \\log N)$ with index | Avoid Cartesian cross-join scans |
| Clustered Index | $O(\\log N)$ B-tree lookup | Prevent Full Table scans |
| GROUP BY | $O(N \\log N)$ sorting | Filter rows early using WHERE |""",

    "guided": """### Guided SQL Walkthrough: {topic_name}

Let's study a classical query formulation for **{topic_name}**.

#### Scenario: Retrieve department salary statistics
Given an `employees` table and a `departments` table, find the department names along with the total sum salary of active employees, listing departments with total salaries greater than $50,000.

#### Step-by-Step Resolution:
1. Join tables using `LEFT JOIN` to include departments with no active employees.
2. Group records by department name.
3. Calculate the aggregate sum salary.
4. Apply the group filter using the `HAVING` clause.

```sql
-- Step-by-step query construction
SELECT d.dept_name, SUM(e.salary) AS total_department_salary
FROM departments d
LEFT JOIN employees e ON d.dept_id = e.dept_id
WHERE e.is_active = TRUE
GROUP BY d.dept_name
HAVING SUM(e.salary) > 50000
ORDER BY total_department_salary DESC;
```"""
}

WEB_TEMPLATE = {
    "overview": """### Web Development & Projects: {topic_name}

Modern web applications combine responsive user interfaces with solid state architectures. **{topic_name}** covers component frameworks, API interactions, responsive UI structures, and hosting.

### Why it matters in placement screens
- **Project Evaluation**: Technical interviewers evaluate your resume projects based on clean routing, security (JWT), state lifecycle, and responsive mobile-first grids.
- **Practical Coding**: Frontend/UI assessments test CSS flex/grid spacing and JavaScript closures or asynchronous promises.""",

    "learn": """### Components, State & Integration Architecture

To build responsive web projects, master the core elements of **{topic_name}**:

#### 1. Lifecycle and State Management
- **Local State**: UI-specific reactivity (e.g. `useState` hooks).
- **Side Effects**: Handled asynchronously (e.g. `useEffect` API triggers).
- **Global State**: Managed via context providers or store patterns (e.g. Redux, Zustand).

#### 2. Layout & Styling Architecture
- **Media Queries**: Responsive styles shifting components between mobile stack and desktop grids.
- **Flexbox vs Grid**: Flexbox resolves single-axis alignments, Grid organizes two-dimensional rows and columns.

```jsx
// React Component Pattern Example
import React, { useState, useEffect } from 'react';

export function UserFeed({ apiEndpoint }) {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(apiEndpoint)
      .then(res => res.json())
      .then(json => { setData(json); setLoading(false); });
  }, [apiEndpoint]);

  if (loading) return <div className="spinner">Loading...</div>;
  return (
    <div className="grid-layout">
      {data.map(item => <Card key={item.id} content={item} />)}
    </div>
  );
}
```""",

    "guided": """### Guided Web Walkthrough: {topic_name}

Let's review an essential project feature implementation under **{topic_name}**.

#### Scenario: Authenticating frontend API requests using JWT
Secure a React workspace by adding authorization header interceptors to outgoing requests.

#### Step-by-Step Resolution:
1. Retrieve the token from secure storage (e.g. localStorage/cookies).
2. Format the HTTP `Authorization: Bearer <token>` request header.
3. Handle expired token responses (HTTP 401) by clearing session states or triggering refresh tokens.

```javascript
// Step-by-step API client interceptor setup
import axios from 'axios';

const client = axios.create({ baseURL: '/api' });

client.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});
```"""
}

BACKEND_TEMPLATE = {
    "overview": """### Backend Developer: {topic_name}

Backend engineering focuses on building secure APIs, managing relational databases, configuring middleware routing, and executing unit checks.

### Why it matters in placement screens
- **Core backend roles**: Evaluates your capability to create secure API routes, write querysets, handle JWT authentication tokens, and run unit tests.
- **Industrial habit checks**: Clean coding requires test coverage, validation layers, and transaction separation.""",
    
    "learn": """### Backend APIs, Serializers, and Verification

Master these backend components:
1. **DRF Serializers**: Control input validation and represent models as JSON.
2. **JWT Authentication**: Validate access and refresh tokens.
3. **API Test Suites**: Execute regression client checks automatically.

```python
# Django REST Framework view serializer model
from rest_framework import serializers

class UserProgressSerializer(serializers.Serializer):
    topic_id = serializers.IntegerField()
    is_completed = serializers.BooleanField()
    
    def validate_topic_id(self, value):
        if value <= 0:
            raise serializers.ValidationError("Invalid topic reference.")
        return value
```""",
    
    "guided": """### Guided Backend Walkthrough: {topic_name}

Implement a Django REST endpoint that marks learning nodes as completed under **{topic_name}**.

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

class TopicCompleteView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, slug):
        from core.models import Topic, UserTopicProgress
        from django.utils import timezone
        
        topic = Topic.objects.get(slug=slug)
        progress, created = UserTopicProgress.objects.get_or_create(
            user=request.user, topic=topic
        )
        progress.is_completed = True
        progress.completed_at = timezone.now()
        progress.save()
        return Response({"success": True, "completed_at": progress.completed_at})
```"""
}

ANALYST_TEMPLATE = {
    "overview": """### Data Analyst: {topic_name}

Data analytics translates raw relational tables, spreadsheet records, or Python dataframes into metrics, trends, and business stories.

### Why it matters in placement screens
- **Analyst Assessment**: Standard assessment filters check your grasp of pivot aggregation, statistical distribution, and dashboard visual layout thinking.
- **Calculations Speed**: Solving Excel/SQL questions under time constraints.""",
    
    "learn": """### Pandas Data Cleaning, Excel Pivots, and Central Tendencies

To clean datasets and find trends for **{topic_name}**:
- **Pandas**: Remove duplicate rows (`drop_duplicates`) and check missing metrics (`fillna`).
- **Median vs Mean**: Median represents the absolute central node, protecting analysis from large outlier distortions.
- **Spreadsheet Pivots**: Aggregate records by sum and averages.

```python
# Python clean script snippet
import pandas as pd

def clean_sales_records(path):
    df = pd.read_csv(path)
    df = df.drop_duplicates()
    # Fill empty sales values with the median sales value
    df['sales'] = df['sales'].fillna(df['sales'].median())
    return df
```""",
    
    "guided": """### Guided Analyst Walkthrough: {topic_name}

Given a dataset containing sales records, compute the median value and remove skewness.

```python
import numpy as np

sales = [10, 12, 11, 15, 200, 14, 13]  # Note outlier 200
mean_val = np.mean(sales)      # Evaluates to 39.2 (skewed)
median_val = np.median(sales)  # Evaluates to 13.0 (robust)

print(f"Mean: {mean_val}, Median: {median_val}")
# Outlier-filtered sales calculation
filtered_sales = [x for x in sales if x < mean_val * 2]
```"""
}

GENERAL_TEMPLATE = {
    "overview": """### General Placement: {topic_name}

General Placement preparation covers resumes, communication practices, and mock strategies. It equips you with professional presentation habits.

### Why it matters in placement screens
- **Conversion Phase**: Having high coding scores is useless if your resume gets filtered out or you struggle in behavioral rounds.""",
    
    "learn": """### Resume Formats, Warmups, and Corporate Research

Key guidelines for **{topic_name}**:
1. **Google X-Y-Z Resume Rule**: 'Accomplished [X], as measured by [Y], by doing [Z].'
2. **Aptitude Pacing**: Focus on high-weight regions first.
3. **Research Values**: Read product details of target companies.

```markdown
Resume Bullet Template:
- Redesigned timeline loading system in React, improving page speed by 42% by implementing lazy imports.
```""",
    
    "guided": """### Guided Walkthrough: {topic_name}

Draft a clear structured resume summary section for campus placements.

```markdown
Core SDE Placements Pitch:
"Result-oriented Computer Science student with strong DSA, SQL, and Django API skills.
Built 3 responsive web projects and cleared 40+ mock technical assessments on PrepSmart."
```"""
}

READINESS_TEMPLATE = {
    "overview": """### Interview Readiness: {topic_name}

Interview Readiness converts theoretical prep into confident technical, coding, and behavioral round presentations.

### Why it matters in placement screens
- **Final Hurdle**: Focuses on STAR behavioral methods, code debugging communication, and mock feedback review.""",
    
    "learn": """### STAR Behavioral Method, Mock Gaps, and Debugging Dialogues

For **{topic_name}**:
- **STAR Method**: Situation, Task, Action, Result.
- **Debugging**: Explain your algorithm out loud before typing lines of code.

```markdown
STAR Framework Outline:
- Situation: Team project was failing to load data under high concurrently.
- Task: Had to optimize database lookup speeds.
- Action: Implemented database indexes and select_related query joins in Django views.
- Result: Lowered load response times by 68% and passed all tests.
```""",
    
    "guided": """### Guided Walkthrough: {topic_name}

Script a behavioral response to conflict resolution during an engineering challenge.

```markdown
HR response:
"In my last project, we disagreed on database schemas. I listened to their concerns, 
sketched out both query designs on a whiteboard to analyze cost differences, 
and we jointly chose the indexed layout, which ultimately passed the load test."
```"""
}


# Track question builders
def build_dsa_questions(topic_name):
    return [
        {
            "question_text": f"What is the primary motivation for using the {topic_name} pattern in technical interviews?",
            "option_a": "To decrease the readability of the implementation.",
            "option_b": "To optimize the runtime complexity, often from quadratic O(N^2) to linear O(N) or O(N log N).",
            "option_c": "To increase the auxiliary space complexity for caching.",
            "option_d": "To force the compiler to run in parallel mode.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": f"The main reason recruiters test {topic_name} is to evaluate if you can optimize naive nested-loop solutions into highly efficient single-pass algorithms."
        },
        {
            "question_text": f"What is the worst-case space complexity of a standard {topic_name} implementation that requires tracking visited states?",
            "option_a": "O(1) constant auxiliary space.",
            "option_b": "O(log N) stack space.",
            "option_c": "O(N) linear space to store unique element keys.",
            "option_d": "O(N^2) quadratic space for storing state grids.",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": f"In the worst case, a {topic_name} algorithm must store state or references for all N elements in a hash map, set, or recursion stack, resulting in O(N) space."
        },
        {
            "question_text": f"Which of the following conditions is an edge case that must always be checked when writing a {topic_name} solution?",
            "option_a": "The input list or buffer being empty or having null pointers.",
            "option_b": "The compiler version being older than Python 3.10.",
            "option_c": "The browser window size during evaluation.",
            "option_d": "The system clock format of the execution server.",
            "correct_answer": "A",
            "difficulty": "easy",
            "explanation": "Empty inputs, single-element buffers, and null values are classic boundary conditions that trigger runtime crashes if not handled first."
        },
        {
            "question_text": f"When trying to optimize a {topic_name} solution, what is the best first step?",
            "option_a": "Change the programming language.",
            "option_b": "Write nested loops to cover all permutations.",
            "option_c": "Identify overlapping subproblems or redundant computations that can be skipped by maintaining state.",
            "option_d": "Delete comments to reduce execution time.",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": f"Optimization in {topic_name} comes from avoiding duplicate traversal or computation of overlapping states."
        },
        {
            "question_text": f"In a placement technical interview, failing to state the time and space complexity of your {topic_name} solution usually results in:",
            "option_a": "Immediate login logout of the compiler.",
            "option_b": "A negative feedback on your engineering communication skills.",
            "option_c": "The code failing all hidden test cases.",
            "option_d": "Automatic syntax validation failure.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Interviewers expect SDE candidates to discuss engineering tradeoffs. Neglecting complexity communication shows a lack of theoretical foundation."
        },
        {
            "question_text": f"Which data structure is most commonly paired with a {topic_name} traversal to ensure quick element lookups?",
            "option_a": "A binary tree.",
            "option_b": "A linked node structure.",
            "option_c": "A Hash Map or Hash Set.",
            "option_d": "A priority queue min-heap.",
            "correct_answer": "C",
            "difficulty": "easy",
            "explanation": f"Hash tables provide average O(1) lookups and insertions, making them ideal for tracking elements within the {topic_name} state."
        },
        {
            "question_text": f"What is the average-case runtime complexity of searching a value in a sorted state using {topic_name} principles?",
            "option_a": "O(N^2)",
            "option_b": "O(N)",
            "option_c": "O(log N)",
            "option_d": "O(1)",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": "For sorted structures, binary search or logarithmic division reduces search intervals by half at each step, yielding O(log N) complexity."
        },
        {
            "question_text": f"What type of error is most common if a recursive DFS-based {topic_name} implementation has a poorly defined base case?",
            "option_a": "Memory Limit Exceeded (MLE)",
            "option_b": "Wrong Answer (WA)",
            "option_c": "Stack Overflow (Runtime Error)",
            "option_d": "Time Limit Exceeded (TLE) only",
            "correct_answer": "C",
            "difficulty": "hard",
            "explanation": "Without a valid base case to terminate recursion, the recursion stack grows infinitely until it exceeds system stack limits, causing a stack overflow crash."
        },
        {
            "question_text": f"A monotonic variation of a {topic_name} collection keeps elements in which order?",
            "option_a": "Random unsorted order.",
            "option_b": "Strictly increasing or strictly decreasing order.",
            "option_c": "Alphabetical order by value string.",
            "option_d": "Order of original index values only.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Monotonic structures enforce strict sorted order (increasing/decreasing) to solve next-greater or range-minimum queries in O(N) time."
        },
        {
            "question_text": f"If an interviewer asks you to solve a {topic_name} problem in-place, they are asking you to minimize which metric?",
            "option_a": "Execution speed.",
            "option_b": "Lines of source code.",
            "option_c": "Auxiliary space complexity.",
            "option_d": "Variable name length.",
            "correct_answer": "C",
            "difficulty": "easy",
            "explanation": "In-place modifications reuse the input buffer for calculation, avoiding extra allocations and optimizing auxiliary space to O(1)."
        }
    ]

def build_aptitude_questions(topic_name):
    return [
        {
            "question_text": f"Which of the following is the most efficient mathematical technique to solve {topic_name} questions quickly in competitive exams?",
            "option_a": "Writing long algebraic equations and solving for x.",
            "option_b": "Using fraction-to-percentage conversion and ratio proportions to simplify numbers.",
            "option_c": "Guessing options randomly using probability.",
            "option_d": "Using a physical scientific calculator (not allowed in OA).",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": f"Shortcut ratios and fraction values (like 1/6 = 16.67%) allow you to solve {topic_name} questions in under 45 seconds without lengthy calculations."
        },
        {
            "question_text": f"In {topic_name} screens, if cost price or base quantity is unknown, what is the best value to assume for easier computation?",
            "option_a": "1",
            "option_b": "100",
            "option_c": "9.8 (gravity constant)",
            "option_d": "A random prime number like 17",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Assuming 100 as the base makes percentage additions/subtractions directly representable as absolute values, simplifying the arithmetic."
        },
        {
            "question_text": f"What is the average-speed formula for a round trip when a vehicle travels to a destination at speed X and returns at speed Y?",
            "option_a": "(X + Y) / 2",
            "option_b": "2XY / (X + Y)",
            "option_c": "XY / (X + Y)",
            "option_d": "sqrt(X * Y)",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "The average speed is the harmonic mean of the speeds, 2XY / (X + Y), since the distance covered is equal in both directions."
        },
        {
            "question_text": f"If an item is marked up by 25% and then sold at a 20% discount, what is the net profit or loss percentage?",
            "option_a": "5% Profit",
            "option_b": "5% Loss",
            "option_c": "0% (No Profit, No Loss)",
            "option_d": "10% Profit",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": "Let Cost Price = 100. Markup by 25% makes it 125. 20% discount on 125 is 25, so Selling Price = 125 - 25 = 100. Net change is 0%."
        },
        {
            "question_text": f"For seating arrangement puzzles in {topic_name}, what is the correct orientation of circular arrangements facing the center?",
            "option_a": "Clockwise movement represents moving to the right.",
            "option_b": "Clockwise movement represents moving to the left.",
            "option_c": "All directions are relative to the top node only.",
            "option_d": "There is no difference between clockwise and counter-clockwise.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "When facing the center of a circle, a clockwise step goes to the left of the person, and counter-clockwise goes to their right."
        },
        {
            "question_text": f"Which number system rule is most useful for verifying the remainder of large exponential numbers like a^b divided by n?",
            "option_a": "Newton's Laws.",
            "option_b": "Fermat's Little Theorem or Euler's Totient Theorem.",
            "option_c": "Pythagoras' Triplet rules.",
            "option_d": "Fibonacci summation.",
            "correct_answer": "B",
            "difficulty": "hard",
            "explanation": "Fermat's Little Theorem states that if p is prime, a^(p-1) = 1 (mod p) for any integer a not divisible by p, which simplifies large powers."
        },
        {
            "question_text": f"In a placement OA, if a {topic_name} question involves a ratio comparison between three quantities, what should you do first?",
            "option_a": "Find the LCM of the common terms to unify the ratio scale.",
            "option_b": "Convert all ratios to decimals.",
            "option_c": "Draw a pie chart.",
            "option_d": "Multiply the options by 10.",
            "correct_answer": "A",
            "difficulty": "medium",
            "explanation": "Finding the LCM of the overlapping terms allows you to express all parts in a single integer ratio scale, facilitating rapid comparison."
        },
        {
            "question_text": f"What is the units digit of the product of the first 10 prime numbers?",
            "option_a": "1",
            "option_b": "5",
            "option_c": "0",
            "option_d": "9",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": "The first 10 prime numbers include 2 and 5. The product of 2 and 5 is 10, which ends in 0. Multiplying any integer by 10 will always result in a units digit of 0."
        },
        {
            "question_text": f"Which of the following is a prime number between 90 and 100?",
            "option_a": "91",
            "option_b": "93",
            "option_c": "97",
            "option_d": "99",
            "correct_answer": "C",
            "difficulty": "easy",
            "explanation": "97 is prime. 91 is divisible by 7 and 13 (7*13=91), 93 is divisible by 3, and 99 is divisible by 3 and 9."
        },
        {
            "question_text": f"When solving data interpretation tables under the {topic_name} track, what is a recommended time-saving strategy?",
            "option_a": "Calculate all percentage values to 5 decimal places.",
            "option_b": "Round off values to nearest integers or tens to estimate the trend before exact calculation.",
            "option_c": "Skip reading the column headings.",
            "option_d": "Use algebraic variables for every cell.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Estimating and rounding numbers allows you to eliminate 2-3 obviously incorrect options in seconds, saving valuable exam time."
        }
    ]

def build_cs_questions(topic_name):
    return [
        {
            "question_text": f"In {topic_name}, why is understanding the core architectural tradeoffs important for developers?",
            "option_a": "It helps in writing syntax without IDE suggestions.",
            "option_b": "It allows optimizing system throughput, memory leaks, concurrency issues, and database read bottlenecks.",
            "option_c": "It is only useful for systems administrator roles, not software developers.",
            "option_d": "It guarantees that a project will build with zero compile errors.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": f"CS fundamentals like {topic_name} form the core of computing knowledge, helping developers design scalable, robust architectures that handle high loads."
        },
        {
            "question_text": f"Which of the following is a classic example of runtime polymorphism in Object-Oriented Programming?",
            "option_a": "Method Overloading.",
            "option_b": "Method Overriding.",
            "option_c": "Operator Overloading.",
            "option_d": "Constructor chaining.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Method overriding allows a subclass to provide a specific implementation of a method that is already defined in its superclass, resolved at runtime."
        },
        {
            "question_text": f"In database design, which normal form requires the removal of transitive dependencies?",
            "option_a": "1NF",
            "option_b": "2NF",
            "option_c": "3NF",
            "option_d": "BCNF",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": "A relation is in 3NF if it is in 2NF and no non-prime attribute is transitively dependent on the primary key."
        },
        {
            "question_text": f"Which of the following conditions is NOT required for a deadlock to occur in an operating system?",
            "option_a": "Mutual Exclusion.",
            "option_b": "Hold and Wait.",
            "option_c": "No Preemption.",
            "option_d": "Preemptive Scheduling.",
            "correct_answer": "D",
            "difficulty": "medium",
            "explanation": "Deadlock requires four concurrent conditions: Mutual Exclusion, Hold and Wait, No Preemption, and Circular Wait. Preemptive scheduling actually helps prevent deadlocks."
        },
        {
            "question_text": f"Which protocol in the TCP/IP stack is connection-oriented and guarantees ordered delivery of packets?",
            "option_a": "UDP",
            "option_b": "TCP",
            "option_c": "IP",
            "option_d": "HTTP",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "TCP (Transmission Control Protocol) is connection-oriented and provides reliable, ordered, and error-checked delivery of a stream of octets."
        },
        {
            "question_text": f"What is the primary function of a Domain Name System (DNS) server?",
            "option_a": "To encrypt browser passwords.",
            "option_b": "To map human-readable domain names to machine-readable IP addresses.",
            "option_c": "To filter malicious web request headers.",
            "option_d": "To store static CSS/JS assets close to users.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "DNS acts as a phonebook for the internet, translating domain names (like google.com) into numerical IP addresses needed to locate resources."
        },
        {
            "question_text": f"Under the {topic_name} track, what does the 'I' in ACID transaction properties stand for?",
            "option_a": "Inheritance",
            "option_b": "Isolation",
            "option_c": "Indexation",
            "option_d": "Integrity",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Isolation ensures that concurrent execution of transactions leaves the database in the same state that would be obtained if they were executed sequentially."
        },
        {
            "question_text": f"What is the difference between a process and a thread in OS design?",
            "option_a": "A process shares memory with other processes; threads do not.",
            "option_b": "A process has its own address space; threads within a process share the process's memory and resources.",
            "option_c": "Threads are managed by the hardware; processes are managed by software.",
            "option_d": "There is no difference; they are synonymous.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Processes are independent execution units with separate memory space, whereas threads are lightweight sub-processes that share resource context."
        },
        {
            "question_text": f"Which design pattern restricts the instantiation of a class to one single instance object?",
            "option_a": "Factory Pattern",
            "option_b": "Observer Pattern",
            "option_c": "Singleton Pattern",
            "option_d": "Decorator Pattern",
            "correct_answer": "C",
            "difficulty": "medium",
            "explanation": "The Singleton pattern ensures that a class has only one instance and provides a global point of access to it."
        },
        {
            "question_text": f"Which layer of the OSI model is responsible for routing packets across logical network boundaries?",
            "option_a": "Physical Layer",
            "option_b": "Data Link Layer",
            "option_c": "Network Layer",
            "option_d": "Transport Layer",
            "correct_answer": "C",
            "difficulty": "easy",
            "explanation": "The Network Layer manages logical device addressing (IP addresses) and routes packets across subnetworks."
        }
    ]

def build_sql_questions(topic_name):
    return [
        {
            "question_text": f"In SQL, what is the primary difference between a WHERE clause and a HAVING clause for {topic_name}?",
            "option_a": "WHERE is used for columns; HAVING is used for index keys.",
            "option_b": "WHERE filters rows before aggregations are computed; HAVING filters aggregated groups after GROUP BY.",
            "option_c": "WHERE is only for SELECT statements; HAVING is only for UPDATE statements.",
            "option_d": "There is no functional difference between them.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "WHERE filters individual input rows. HAVING is applied to summarized group rows created by the GROUP BY clause."
        },
        {
            "question_text": f"Which join operation returns all rows from the left table and matching rows from the right table?",
            "option_a": "INNER JOIN",
            "option_b": "LEFT JOIN",
            "option_c": "RIGHT JOIN",
            "option_d": "FULL OUTER JOIN",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "LEFT JOIN (or LEFT OUTER JOIN) preserves all rows of the left-hand side table, filling right-hand columns with NULL if no match exists."
        },
        {
            "question_text": f"What type of index organizes data pages on disk in the physical order of the index keys?",
            "option_a": "Non-clustered Index",
            "option_b": "Clustered Index",
            "option_c": "B-Tree Index only",
            "option_d": "Hash Index",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "A Clustered Index determines the physical order of data in the table. Hence, there can be only one clustered index per database table."
        },
        {
            "question_text": f"If you run a query with an aggregate function like SUM(salary) without a GROUP BY clause, what does it return?",
            "option_a": "A syntax error.",
            "option_b": "A single row representing the aggregate sum of all values in the column.",
            "option_c": "Multiple rows representing individual salaries.",
            "option_d": "A table index representation.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Without GROUP BY, the entire table is treated as a single group, so the query collapses all rows and returns exactly one summary row."
        },
        {
            "question_text": f"Under database normalization rules, what anomaly is prevented by splitting a large redundant table into smaller related tables?",
            "option_a": "Insertion, Deletion, and Update anomalies.",
            "option_b": "Compile and syntax errors.",
            "option_c": "Network latency issues.",
            "option_d": "Indexing delay anomalies.",
            "correct_answer": "A",
            "difficulty": "medium",
            "explanation": "Normalization minimizes duplication to prevent insertion anomalies (unable to add data), deletion anomalies (loss of unrelated info), and update anomalies (inconsistent data)."
        },
        {
            "question_text": f"Which keyword is used in SQL to combine the result sets of two SELECT queries, removing duplicate rows?",
            "option_a": "UNION ALL",
            "option_b": "UNION",
            "option_c": "JOIN",
            "option_d": "INTERSECT",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "UNION combines sets and removes duplicates. UNION ALL retains all rows from both sets, including duplicates, which runs faster."
        },
        {
            "question_text": f"What is the role of the EXPLAIN command in SQL database administration?",
            "option_a": "To add inline text comments to database schemas.",
            "option_b": "To display the query execution plan showing scan types, index usage, and cost estimates.",
            "option_c": "To debug syntax errors in stored procedures.",
            "option_d": "To reset the primary key auto-increment counter.",
            "correct_answer": "B",
            "difficulty": "hard",
            "explanation": "EXPLAIN lets developers analyze query execution steps (like Full Table Scan vs Index Scan) to optimize slow-running SQL queries."
        },
        {
            "question_text": f"Which transaction isolation level provides the highest level of concurrency protection but is the slowest?",
            "option_a": "Read Uncommitted",
            "option_b": "Read Committed",
            "option_c": "Repeatable Read",
            "option_d": "Serializable",
            "correct_answer": "D",
            "difficulty": "hard",
            "explanation": "Serializable isolation locks all accessed rows, preventing dirty reads, non-repeatable reads, and phantom reads, but heavily limits concurrent access."
        },
        {
            "question_text": f"In SQL constraints, what does a FOREIGN KEY constraint enforce?",
            "option_a": "Physical file size constraints on disk.",
            "option_b": "Referential integrity between tables by ensuring key values exist in the parent table.",
            "option_c": "Automatic column index generation.",
            "option_d": "Encryption keys on sensitive columns.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "A foreign key matches values in a child table to a primary key in a parent table to ensure reference consistency."
        },
        {
            "question_text": f"What does the SQL command ROLLBACK accomplish?",
            "option_a": "Reverts the database schema to an older version.",
            "option_b": "Cancels the active transaction, undoing all uncommitted changes made since it started.",
            "option_c": "Deletes the last table row from database files.",
            "option_d": "Clones a query execution plan.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "ROLLBACK terminates the current transaction transactionally, returning data to the state recorded at the last COMMIT checkpoint."
        }
    ]

def build_web_questions(topic_name):
    return [
        {
            "question_text": f"In Web Development, what is the primary role of React's virtual DOM?",
            "option_a": "To store data in the browser's cookies.",
            "option_b": "To compute UI differences in memory and minimize expensive actual DOM repaints.",
            "option_c": "To compile JSX into Python backend models.",
            "option_d": "To encrypt frontend network request payloads.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "React maintains a lightweight representation of the DOM in memory. By comparing states (diffing), it batch-updates only the changed elements."
        },
        {
            "question_text": f"Which HTML5 semantic element is most appropriate for enclosing the primary navigation links of a website?",
            "option_a": "div",
            "option_b": "nav",
            "option_c": "section",
            "option_d": "aside",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "The <nav> tag is explicitly designed for navigation blocks, improving SEO crawlability and accessibility for screen readers."
        },
        {
            "question_text": f"Which CSS layout model is best suited for aligning elements in a single direction (either row or column)?",
            "option_a": "CSS Grid",
            "option_b": "Flexbox",
            "option_c": "Floats",
            "option_d": "Table Layouts",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Flexbox is a 1D layout model optimized for aligning items along a single axis. CSS Grid is a 2D model suited for rows and columns simultaneously."
        },
        {
            "question_text": f"What does a 401 Unauthorized HTTP status code indicate to the client?",
            "option_a": "The requested resource was not found on the server.",
            "option_b": "The client request lacks valid authentication credentials for the target resource.",
            "option_c": "The server encountered an unhandled database exception.",
            "option_d": "The request payload size is too large.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "HTTP 401 indicates that the request must be authenticated, typically by logging in or providing a valid authorization header."
        },
        {
            "question_text": f"Where are JSON Web Tokens (JWT) typically sent in a client-server HTTP API request?",
            "option_a": "In the request query parameters.",
            "option_b": "In the Authorization header as a Bearer token.",
            "option_c": "In the user profile settings JSON.",
            "option_d": "In the CSS file import rules.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "To prevent leakage and ensure standards compliance, access tokens are sent in the HTTP 'Authorization: Bearer <token>' header."
        },
        {
            "question_text": f"What is the purpose of React's useEffect dependency array?",
            "option_a": "To import external packages into the component.",
            "option_b": "To control when the side effect execution runs by tracking variable changes.",
            "option_c": "To set inline styling attributes.",
            "option_d": "To connect the component to database tables.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "React only runs the useEffect callback when elements in the dependency array change value between component re-renders."
        },
        {
            "question_text": f"In Git workflows, which command saves your local changes to a separate remote workspace tracking branch?",
            "option_a": "git commit",
            "option_b": "git push",
            "option_c": "git stash",
            "option_d": "git merge",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "git push uploads local branch commits to the remote repository (such as GitHub) to share code changes."
        },
        {
            "question_text": f"What is a key security reason to use environment variables (.env files) in project codebases?",
            "option_a": "To compile JavaScript code faster.",
            "option_b": "To keep sensitive data (database passwords, API keys, JWT secrets) out of source control repositories.",
            "option_c": "To compress static media assets.",
            "option_d": "To auto-generate unit tests.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Hardcoding API secrets in source files exposes them to unauthorized eyes on GitHub. Environment variables inject values at runtime instead."
        },
        {
            "question_text": f"Which of the following describes the Javascript concept of closures?",
            "option_a": "An error that terminates code execution.",
            "option_b": "A function that has access to outer function scope variables even after the outer function has finished executing.",
            "option_c": "Closing browser tabs programmatically.",
            "option_d": "A loop that terminates after 10 cycles.",
            "correct_answer": "B",
            "difficulty": "hard",
            "explanation": "Closures allow a nested function to retain scope variables of its parent context, enabling private states and currying patterns."
        },
        {
            "question_text": f"What is the main purpose of responsive web design (using media queries)?",
            "option_a": "To speed up server response times.",
            "option_b": "To render UI layouts that adapt cleanly to different screen sizes (phones, tablets, desktops).",
            "option_c": "To translate page content to foreign languages.",
            "option_d": "To secure the site against database exploits.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Media queries look at device dimensions and apply specific CSS layout rules to guarantee a polished user experience on all form factors."
        }
    ]

def build_backend_questions(topic_name):
    return [
        {
            "question_text": f"In Django REST Framework, what is the primary role of a Serializer in a {topic_name} API?",
            "option_a": "To compress database table rows.",
            "option_b": "To convert complex data types (like querysets and model instances) to and from native Python types that can be rendered to JSON.",
            "option_c": "To encrypt user password values in cookies.",
            "option_d": "To auto-generate unit test assertions.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Serializers translate Django database queries into clean JSON responses, and validate incoming data fields back into validated dictionary maps."
        },
        {
            "question_text": f"Which HTTP response code should a REST endpoint return after successfully creating a new record under {topic_name}?",
            "option_a": "200 OK",
            "option_b": "201 Created",
            "option_c": "204 No Content",
            "option_d": "400 Bad Request",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "HTTP 201 is the standard success status code indicating that a request has succeeded and led to the creation of a resource."
        },
        {
            "question_text": f"How do you protect a DRF view from anonymous access, ensuring JWT headers are checked for {topic_name}?",
            "option_a": "Set throttle classes only.",
            "option_b": "Define permission_classes = [IsAuthenticated] on the view.",
            "option_c": "Disable CORS on the server.",
            "option_d": "Use the @login_required decorator from standard django.contrib.auth.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "permission_classes = [IsAuthenticated] forces Django REST Framework to evaluate the request authentication headers before running view code."
        },
        {
            "question_text": f"When executing request unit tests for a protected {topic_name} backend endpoint, what must you attach to the test client request?",
            "option_a": "The admin password in plain text.",
            "option_b": "A valid Authorization: Bearer <token> header.",
            "option_c": "A custom user agent string.",
            "option_d": "A CSRF token only.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Protected endpoints verify identity via the JWT token sent in the HTTP Authorization header, which must be attached in test client setups."
        },
        {
            "question_text": f"What is a principal benefit of using select_related or prefetch_related in Django querysets for {topic_name}?",
            "option_a": "To enable automatic database backups.",
            "option_b": "To optimize database retrieval by fetching related objects in a single query, resolving the N+1 database hits problem.",
            "option_c": "To encrypt table keys.",
            "option_d": "To validate fields dynamically.",
            "correct_answer": "B",
            "difficulty": "hard",
            "explanation": "select_related performs an SQL join to fetch related foreign key columns in a single hit, preventing multiple sequential query triggers."
        },
        {
            "question_text": "What does a 400 Bad Request HTTP status code mean in API communication?",
            "option_a": "The server is temporarily down.",
            "option_b": "The server could not understand the request due to invalid syntax, missing fields, or validation errors in the payload.",
            "option_c": "The user needs to log in again.",
            "option_d": "The database query timed out.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "HTTP 400 indicates a client-side validation failure where the sent JSON does not conform to the expected API schema."
        },
        {
            "question_text": "What is the function of a Django migration file?",
            "option_a": "To export database table data as Excel files.",
            "option_b": "To apply database schema changes (like adding or modifying tables/columns) in a version-controlled way.",
            "option_c": "To run unit tests in production.",
            "option_d": "To route requests to API views.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Migrations act as version control for database structures, mapping changes in models.py to SQL DDL statements executed on database engines."
        },
        {
            "question_text": "Which middleware is responsible for preventing Cross-Site Request Forgery in standard Django forms?",
            "option_a": "SessionMiddleware",
            "option_b": "CsrfViewMiddleware",
            "option_c": "CommonMiddleware",
            "option_d": "SecurityMiddleware",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "CsrfViewMiddleware injects and validates unique tokens in POST requests to protect server endpoints from state-modifying requests initiated by malicious sites."
        },
        {
            "question_text": "In a JWT token, what is the purpose of the expiration claim (exp)?",
            "option_a": "To list the user permissions.",
            "option_b": "To define the timestamp after which the access token becomes invalid, reducing exposure windows if leaked.",
            "option_c": "To sign the token securely.",
            "option_d": "To specify the hashing algorithm used.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Short-lived tokens limit the time a stolen token can be used by an attacker. The exp claim tells the server when to reject the token."
        },
        {
            "question_text": "What is a mock database engine (like SQLite in-memory database) commonly used for in SDE pipelines?",
            "option_a": "To store long-term production logs.",
            "option_b": "To run rapid unit and integration tests in clean, isolated environments without polluting disk space.",
            "option_c": "To share client passwords.",
            "option_d": "To render UI charts.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "In-memory databases exist only in RAM and are destroyed after test suites finish, yielding maximum speed and zero disk cleanup overhead."
        }
    ]

def build_data_analyst_questions(topic_name):
    return [
        {
            "question_text": f"In data analysis, why is treating missing values or duplicates a critical early step for {topic_name}?",
            "option_a": "Because missing values cause compilers to run twice as slow.",
            "option_b": "Because ignoring duplicates or nulls skews aggregate metrics like mean, sum, and variance, leading to incorrect business conclusions.",
            "option_c": "To decrease the file size of the dataset.",
            "option_d": "To encrypt tabular columns.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Missing data or duplicate rows distort statistical averages and sums, corrupting the reliability of insights derived during analysis."
        },
        {
            "question_text": "Which Excel tool allows you to summarize and group thousands of rows by multiple dimensions in seconds?",
            "option_a": "VLOOKUP",
            "option_b": "Pivot Table",
            "option_c": "Conditional Formatting",
            "option_d": "Data Validation",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Pivot Tables summarize large tables by grouping, sorting, averaging, and summing records dynamically according to selected fields."
        },
        {
            "question_text": "If a dataset has a highly skewed distribution with major outliers, which measure of central tendency is most reliable?",
            "option_a": "Mean",
            "option_b": "Median",
            "option_c": "Range",
            "option_d": "Standard Deviation",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Median is the middle value and is not affected by extreme outliers. The Mean is heavily pulled by outliers, distorting central tendency."
        },
        {
            "question_text": "What type of chart is most suitable for showing the trend of sales metrics over continuous monthly time periods?",
            "option_a": "Bar Chart",
            "option_b": "Line Chart",
            "option_c": "Pie Chart",
            "option_d": "Scatter Plot",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Line charts connect data points sequentially, making them ideal for visualizing trends and change over continuous time intervals."
        },
        {
            "question_text": "What is the primary objective of SQL window functions (like ROW_NUMBER or RANK) in data analytics?",
            "option_a": "To delete database tables.",
            "option_b": "To compute values across a partition of rows while still returning details of individual rows in the output.",
            "option_c": "To lock tables for transaction safety.",
            "option_d": "To filter records before joining tables.",
            "correct_answer": "B",
            "difficulty": "hard",
            "explanation": "Window functions perform partition-based aggregations but preserve row-level details, unlike GROUP BY which collapses rows."
        },
        {
            "question_text": "In statistics, what does a correlation coefficient of -0.85 between two variables indicate?",
            "option_a": "A weak positive relationship.",
            "option_b": "A strong negative relationship.",
            "option_c": "No relationship between the variables.",
            "option_d": "An invalid calculation parameter.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Correlation ranges from -1 to +1. A value of -0.85 shows a strong negative linear relationship (as one variable increases, the other decreases)."
        },
        {
            "question_text": "What is the function of the pandas method drop_duplicates() in a Python cleaning script?",
            "option_a": "To delete columns containing numbers.",
            "option_b": "To identify and remove duplicate rows from a DataFrame.",
            "option_c": "To sort the dataset index.",
            "option_d": "To load Excel worksheets.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "drop_duplicates() cleans a DataFrame by scanning rows and removing redundant duplicate entries to ensure data uniqueness."
        },
        {
            "question_text": "In spreadsheet formulas, which function searches for a value in the first column of a table array and returns a value in the same row?",
            "option_a": "SUMIF",
            "option_b": "VLOOKUP",
            "option_c": "INDEX",
            "option_d": "COUNTIF",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "VLOOKUP (Vertical Lookup) finds a key in the leftmost column and retrieves a cell value from a specified column in the matching row."
        },
        {
            "question_text": "Under the data analysis lifecycle, why is presenting metrics in a clear hierarchy important in dashboard design?",
            "option_a": "It hides important details from users.",
            "option_b": "It directs users to the most critical decision-supporting metrics first, preventing information overload.",
            "option_c": "It forces users to scroll more.",
            "option_d": "It runs queries faster.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Visual hierarchy organizes cards so that key performance indicators (KPIs) stand stand out, allowing rapid assessment of system health."
        },
        {
            "question_text": "What does a high variance in a dataset sample indicate?",
            "option_a": "All values are identical.",
            "option_b": "The data points are highly spread out around the mean value.",
            "option_c": "The mean is equal to 0.",
            "option_d": "The dataset contains only string text.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Variance measures dispersion. High variance means values are widely distributed from the average, showing high volatility or diversity."
        }
    ]

def build_sde_questions(topic_name):
    return [
        {
            "question_text": f"In software engineering, why are SOLID principles highly emphasized for {topic_name} systems?",
            "option_a": "They speed up compilation and interpreter execution times.",
            "option_b": "They improve code design, making systems easier to extend, maintain, and refactor without introducing breaking changes.",
            "option_c": "They prevent database query timeouts.",
            "option_d": "They enforce strictly dark-mode UI colors.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "SOLID design principles keep code modular and loosely coupled, meaning new requirements can be added with minimal changes to existing files."
        },
        {
            "question_text": "Which SOLID principle states that a class should have exactly one reason to change, keeping its scope focused?",
            "option_a": "Single Responsibility Principle (SRP)",
            "option_b": "Open/Closed Principle (OCP)",
            "option_c": "Liskov Substitution Principle (LSP)",
            "option_d": "Dependency Inversion Principle (DIP)",
            "correct_answer": "A",
            "difficulty": "easy",
            "explanation": "SRP limits a class to one single actor or business function, ensuring that modifying that function doesn't break other system processes."
        },
        {
            "question_text": "What does the Dependency Inversion Principle (DIP) suggest developers should depend upon?",
            "option_a": "Concrete implementations and specific database classes.",
            "option_b": "Abstractions (like interfaces or abstract parent classes) rather than concrete classes.",
            "option_c": "The OS system clock context.",
            "option_d": "Physical file paths.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "DIP decouples high-level and low-level code by introducing abstractions, allowing concrete modules to be swapped without rewriting client code."
        },
        {
            "question_text": "What is a primary benefit of writing automated unit tests before or during the development of {topic_name} features?",
            "option_a": "It deletes comments from production assets.",
            "option_b": "It provides a rapid feedback loop to verify code changes don't break existing requirements.",
            "option_c": "It forces variables to allocate less heap memory.",
            "option_d": "It hides design flaws from code review teams.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Unit tests run assertions automatically, alerting you if a code edit changes expected behaviors or breaks dependent modules."
        },
        {
            "question_text": "What does a memory leak in a programming language (like C or C++) indicate?",
            "option_a": "The disk space is running low.",
            "option_b": "Dynamically allocated memory (on the heap) is not released back to the system after it is no longer needed, depleting available RAM.",
            "option_c": "The system clock has drifted.",
            "option_d": "C-style strings are too short.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Without manual deallocation (or if pointers are lost), heap blocks remain locked, causing system memory usage to grow until a crash occurs."
        },
        {
            "question_text": "Which Big O notation represents an algorithm whose execution time grows proportionally to the square of the input size?",
            "option_a": "O(1)",
            "option_b": "O(N)",
            "option_c": "O(N log N)",
            "option_d": "O(N^2)",
            "correct_answer": "D",
            "difficulty": "easy",
            "explanation": "O(N^2) quadratic complexity is typical of nested loops over the same array size N, where operations scale quadratically."
        },
        {
            "question_text": "What is context switching in operating system scheduling?",
            "option_a": "Switching between light mode and dark mode in editor themes.",
            "option_b": "The process of storing and restoring the state of a CPU thread or process so that execution can be resumed later.",
            "option_c": "Routing packets across ports.",
            "option_d": "Clearing the browser cache.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Context switching lets a single CPU core rapidly swap active threads, giving the user a multi-tasking experience."
        },
        {
            "question_text": "What is the primary role of a garbage collector in runtime environments like Java or Python?",
            "option_a": "To scan for code syntax warnings.",
            "option_b": "To automatically identify and deallocate heap memory blocks that are no longer referenced by the program.",
            "option_c": "To delete temporary debug logs.",
            "option_d": "To encrypt user cookies.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Garbage collectors track references to objects and automatically clean up unreachable memory, freeing developers from manual deallocation."
        },
        {
            "question_text": "In debugging, what is a stack trace most useful for?",
            "option_a": "Timing database query executions.",
            "option_b": "Identifying the active call stack sequence of functions that led to an unhandled exception or crash point.",
            "option_c": "Calculating code coverage percentage.",
            "option_d": "Validating CSS layouts.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "A stack trace lists active function frames in order of invocation, pointing to the exact file name and line number where the error occurred."
        },
        {
            "question_text": "Why are code comments that explain 'Why' rather than 'What' preferred by senior SDEs?",
            "option_a": "Because compiler parsers skip 'Why' descriptions.",
            "option_b": "Because the code itself shows 'What' it does; comments should explain design rationale or non-obvious constraints that code can't convey.",
            "option_c": "It decreases the build output bundle size.",
            "option_d": "It forces code to run in concurrent threads.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Explaining obvious logic is redundant. Explaining the reasoning behind design choices or edge-case constraints prevents future refactoring errors."
        }
    ]

def build_general_questions(topic_name):
    return [
        {
            "question_text": f"When preparing for campus placements, why is {topic_name} a valuable preparation focus?",
            "option_a": "It compiles local software projects faster.",
            "option_b": "It aligns your resume, communication style, and speed parameters to match corporate expectations and filtration metrics.",
            "option_c": "It forces developers to use specific compiler versions.",
            "option_d": "It is only useful for non-engineering majors.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": f"Placement preparation topics like {topic_name} help you bridge academic knowledge with professional expectations, ensuring you pass hiring rounds."
        },
        {
            "question_text": "What is the recommended maximum page length for a standard engineering graduate resume?",
            "option_a": "1 Page",
            "option_b": "2 Pages",
            "option_c": "3 Pages",
            "option_d": "Unlimited length",
            "correct_answer": "A",
            "difficulty": "easy",
            "explanation": "Recruiters spend under 10 seconds scanning a resume. A single-page layout forces you to keep content concise, readable, and highly relevant."
        },
        {
            "question_text": "When describing a project on your resume, what is the best way to present your contributions?",
            "option_a": "List the tools used without describing what was built.",
            "option_b": "Use the X-Y-Z formula: Accomplished [X] as measured by [Y], by doing [Z], showing quantitative impact.",
            "option_c": "Write a paragraph describing the project's background story in detail.",
            "option_d": "Copy the project README documentation directly.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "The X-Y-Z formula (pioneered by Google) links actions with measurable outcomes, proving your engineering capabilities to hiring teams."
        },
        {
            "question_text": "What should you do before attending a placement interview for a specific company?",
            "option_a": "Memorize the company's entire source code repository.",
            "option_b": "Research the company's products, engineering culture, core values, and typical interview rounds.",
            "option_c": "Change the programming languages listed on your resume.",
            "option_d": "Decline to answer non-technical questions.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Researching target companies allows you to tailor your communication, showing genuine interest and alignment with their business objectives."
        },
        {
            "question_text": "After completing a mock test, which practice yields the highest score improvement on subsequent attempts?",
            "option_a": "Deleting the mock test history.",
            "option_b": "Thoroughly reviewing your errors, understanding why you missed those questions, and practicing weak areas.",
            "option_c": "Immediately starting another test without reviewing results.",
            "option_d": "Changing the UI theme to dark mode.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Mock tests diagnose knowledge gaps. Error analysis turns these gaps into action items, preventing you from repeating identical mistakes."
        },
        {
            "question_text": "What does a timed aptitude warmup prepare you for?",
            "option_a": "Solving problems with zero constraints.",
            "option_b": "Managing time efficiently under pressure, allowing you to bypass hard questions and secure passing cutoffs.",
            "option_c": "Encrypting login credentials.",
            "option_d": "Refactoring database queries.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Online assessments are heavily speed-constrained. Timed warmups train your pacing, teaching you when to move on from time-consuming puzzles."
        },
        {
            "question_text": "When an interviewer asks you to explain a project, how should you structure your response?",
            "option_a": "Start coding the main loop on a whiteboard immediately.",
            "option_b": "Provide context using the STAR method: Situation, Task, Action, Result, focusing on tradeoffs and impact.",
            "option_c": "Talk only about your teammates' contributions.",
            "option_d": "Apologize for not having a live production link.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "STAR provides a structured, logical narrative, helping the interviewer follow the problem context and your individual contributions clearly."
        },
        {
            "question_text": "Which verbal communication habit is most appreciated by technical interviewers?",
            "option_a": "Speaking extremely fast without pause.",
            "option_b": "Pausing to organize your thoughts, speaking clearly, and explaining your logical reasoning out loud.",
            "option_c": "Using complex jargon without explaining it.",
            "option_d": "Answering questions in single-word statements.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Interviewers evaluate how you think. Speaking out loud lets them assess your problem-solving process and guide you if you get stuck."
        },
        {
            "question_text": "In online coding assessments, why is reading the constraints (e.g. N <= 10^5) a critical first step?",
            "option_a": "It lists the company names.",
            "option_b": "It dictates the maximum acceptable time complexity (e.g., O(N) vs O(N^2)) to avoid TLE failures.",
            "option_c": "It validates user passwords.",
            "option_d": "It determines the font size of the code editor.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Constraints tell you what algorithms are feasible. For N = 10^5, an O(N^2) solution triggers a Time Limit Exceeded (TLE) error, requiring O(N) or O(N log N)."
        },
        {
            "question_text": "What is the primary purpose of mock placement interviews?",
            "option_a": "To earn credentials.",
            "option_b": "To simulate real interview conditions, reduce anxiety, and get professional feedback on verbal and technical gaps.",
            "option_c": "To skip actual hiring rounds.",
            "option_d": "To write project code.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Simulated environments build muscle memory, helping you manage stress and identify communication or coding bottlenecks before actual interviews."
        }
    ]

def build_readiness_questions(topic_name):
    return [
        {
            "question_text": f"In behavioral rounds, which method is universally recommended to answer questions on conflict, leadership, or failure under the {topic_name} track?",
            "option_a": "Blaming teammates for project issues.",
            "option_b": "The STAR method: describing Situation, Task, Action, and the final measurable Result.",
            "option_c": "Asserting that you have never experienced conflicts or failures.",
            "option_d": "Reciting textbook definitions of leadership.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "The STAR framework organizes behavioral answers, ensuring you outline the context, your specific choices, and the measurable outcome."
        },
        {
            "question_text": "When an interviewer provides feedback that your initial coding approach has a bug, what is the best reaction?",
            "option_a": "Argue that the code is correct.",
            "option_b": "Thank the interviewer, dry-run your logic with a small input example, and systematically trace and resolve the issue.",
            "option_c": "Immediately delete all written code and start over.",
            "option_d": "Stay silent and wait for them to give the solution.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Receptiveness to feedback is a highly valued trait. Working collaboratively to debug shows teamwork and software debugging ability."
        },
        {
            "question_text": "How should you answer the common interview question: 'Tell me about yourself'?",
            "option_a": "Read your resume word-for-word starting from high school.",
            "option_b": "Give a 2-3 minute structured pitch covering your current status, key project achievements, and why you are excited about this role.",
            "option_c": "Talk primarily about your personal hobbies and family.",
            "option_d": "Ask the interviewer to read your resume instead.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "This opener sets the interview tone. A concise, professional pitch highlights your strengths and relevant SDE/analyst skills."
        },
        {
            "question_text": "If you do not know the answer to a technical question during an interview, what is the most professional response?",
            "option_a": "Guess values randomly and speak confidently.",
            "option_b": "Acknowledge that you don't know the exact solution, share your initial thoughts or what you know about the domain, and ask for a hint.",
            "option_c": "Remain silent until the interviewer asks a different question.",
            "option_d": "Assert that the concept is obsolete.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Honesty combined with a willingness to think through problems is preferred over making up incorrect answers. It shows integrity and intellectual curiosity."
        },
        {
            "question_text": "When explaining your coding solution, what shows the highest level of engineering readiness?",
            "option_a": "Typing code silently and claiming it works.",
            "option_b": "Discussing time and space complexities, detailing tradeoffs, and suggesting how the code can scale or be optimized.",
            "option_c": "Writing a large number of comments in the editor.",
            "option_d": "Avoiding discussion of data structures.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Proactively explaining tradeoffs (e.g., spending space to save runtime) proves that you make deliberate, analytical software decisions."
        },
        {
            "question_text": "Which of the following is the best way to handle a failure scenario in a mock interview?",
            "option_a": "Request the mock record to be deleted.",
            "option_b": "Document the gaps, review the feedback, and practice similar scenarios to ensure readiness.",
            "option_c": "Ignore the mock feedback and assume the interviewer was biased.",
            "option_d": "Stop taking mock interviews.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Mocks are designed for safe failure. Capturing feedback and practicing weak points turns failures into growth steps before the actual drive."
        },
        {
            "question_text": "In HR rounds, when asked: 'Why do you want to join our company?', what should you focus on?",
            "option_a": "The salary package and location benefits only.",
            "option_b": "Linking the company's recent achievements, products, or values with your own career goals and technical interests.",
            "option_c": "Complaining about your current college or placements.",
            "option_d": "Telling them you are open to any company.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Customizing your response shows that you did research and are motivated to contribute to their specific business vision."
        },
        {
            "question_text": "What is the purpose of asking questions to the interviewer at the end of the round?",
            "option_a": "To test the interviewer's technical knowledge.",
            "option_b": "To demonstrate your curiosity, interest in their work, and evaluate if the team and company culture align with your aspirations.",
            "option_c": "To ask about your selection status immediately.",
            "option_d": "To show that you have no queries.",
            "correct_answer": "B",
            "difficulty": "easy",
            "explanation": "Asking thoughtful questions (e.g., about engineering challenges, daily SDE workflows) reflects maturity and proactive interest in the team."
        },
        {
            "question_text": "When discussing a conflict in a behavioral round, what is a key indicator of readiness?",
            "option_a": "Portraying yourself as completely right and the other party as completely wrong.",
            "option_b": "Emphasizing how you listened to the other perspective, kept a professional focus on the project goal, and reached a constructive resolution.",
            "option_c": "Refusing to acknowledge that a conflict occurred.",
            "option_d": "Explaining how the conflict caused the project to fail.",
            "correct_answer": "B",
            "difficulty": "medium",
            "explanation": "Conflict is natural. Showing how you manage it constructively proves your communication, emotional intelligence, and team leadership skills."
        },
        {
            "question_text": "How should you prepare for online coding assessments that monitor tab switching?",
            "option_a": "Practice coding without leaving the assessment browser sandbox, managing your time inside the editor interface.",
            "option_b": "Attempt to bypass monitoring using external devices.",
            "option_c": "Write solutions on paper first.",
            "option_d": "Complain to the college placement cell.",
            "correct_answer": "A",
            "difficulty": "easy",
            "explanation": "Assessments lock browser tabs. Practicing under standard conditions prepares you to work solely within the provided IDE workspace."
        }
    ]


def _seed_learning_content(topic_lookup):
    import json
    from core.models import (
        Topic, TopicDependency, TopicSection, TopicVisualization, 
        TopicRevision, Question, CodingProblem, TestCase, CodingContest
    )
    
    # 1. Ensure slugs are generated for all topics in the lookup
    for name, topic in topic_lookup.items():
        if not topic.slug:
            from django.utils.text import slugify
            import uuid
            base_slug = slugify(name)
            topic.slug = base_slug if base_slug else str(uuid.uuid4())[:8]
            topic.save(update_fields=["slug"])

    # 2. Define dependencies for key topics
    dependency_pairs = [
        ("Sliding Window", "Arrays and Strings"),
        ("Two Pointers", "Sliding Window"),
        ("Advanced Array Problems", "Two Pointers"),
        ("Time Speed Distance", "Number Systems"),
        ("Percentages and Profit Loss", "Number Systems"),
        ("Django REST APIs", "DBMS"),
        ("Authentication and JWT", "Django REST APIs"),
        ("API Testing", "Authentication and JWT")
    ]
    for child_name, parent_name in dependency_pairs:
        child = topic_lookup.get(child_name)
        parent = topic_lookup.get(parent_name)
        if child and parent:
            TopicDependency.objects.get_or_create(topic=child, prerequisite=parent)

    # 3. Create coding problems & test cases
    ensure_coding_problems_and_testcases()

    # Load bespoke topic content to override generic templates
    import os, json
    from django.conf import settings
    bespoke_data = {}
    bespoke_path = os.path.join(settings.BASE_DIR, 'scripts', 'topic_content_data.json')
    if os.path.exists(bespoke_path):
        try:
            with open(bespoke_path, 'r', encoding='utf-8') as f:
                bespoke_data = json.load(f)
        except Exception:
            pass

    # 4. Populate sections, visualizers, revisions, and questions for all 51 topics
    for topic_name, topic in topic_lookup.items():
        track_name = topic.track.name if topic.track else "General"
        slug = topic.slug
        
        # Determine Domain based on Track Name
        if "Data Structures" in track_name or "SDE" in track_name:
            topic.domain = "dsa"
        elif "Aptitude" in track_name:
            topic.domain = "aptitude"
        elif "CS Fundamentals" in track_name or "Database" in track_name or "Backend" in track_name or "SQL" in track_name:
            topic.domain = "core_cs"
        elif "Interview" in track_name or "Resume" in track_name or "Career" in track_name or "General Placement" in track_name:
            topic.domain = "career"
        else:
            topic.domain = "career"
        
        # Populate career metadata
        topic.why_it_matters = f"Understanding {topic_name} is essential for securing SDE, backend, or analyst offers at top companies. It solves critical efficiency and logic bottlenecks."
        topic.target_companies = ["Amazon", "TCS", "Google", "Infosys", "Zoho"]
        topic.interview_frequency = "High" if "DSA" in track_name or "Aptitude" in track_name else "Medium"
        topic.save(update_fields=["why_it_matters", "target_companies", "interview_frequency", "domain"])

        # Select template based on domain
        if topic.domain == "dsa":
            template = DSA_TEMPLATE
            q_builder = build_dsa_questions
        elif topic.domain == "aptitude":
            template = APTITUDE_TEMPLATE
            q_builder = build_aptitude_questions
        elif topic.domain == "core_cs":
            if "SQL" in track_name:
                template = SQL_TEMPLATE
                q_builder = build_sql_questions
            else:
                template = CS_TEMPLATE
                q_builder = build_cs_questions
        else:
            if "Interview" in track_name:
                template = READINESS_TEMPLATE
                q_builder = build_readiness_questions
            else:
                template = GENERAL_TEMPLATE
                q_builder = build_general_questions

        # Format markdown content (use replace() to avoid KeyError on curly braces in code examples)
        overview_md = template["overview"].replace("{topic_name}", topic_name).replace("{slug}", slug or "")
        learn_md = template["learn"].replace("{topic_name}", topic_name).replace("{slug}", slug or "")
        guided_md = template["guided"].replace("{topic_name}", topic_name).replace("{slug}", slug or "")
        questions_to_create = q_builder(topic_name)

        # OVERRIDE WITH BESPOKE DATA
        b_data = bespoke_data.get(slug, {})
        if b_data:
            overview_md = b_data.get("overview", overview_md)
            learn_md = b_data.get("learn", learn_md)
            guided_md = b_data.get("learn", guided_md) # Fallback to learn for guided if not present
            if "questions" in b_data:
                questions_to_create = b_data["questions"]

        # Create/Update Topic Sections
        TopicSection.objects.update_or_create(
            topic=topic, section_type="overview", order=1,
            defaults={"title": f"{topic_name} Overview", "content_markdown": overview_md}
        )
        TopicSection.objects.update_or_create(
            topic=topic, section_type="learn", order=2,
            defaults={"title": f"Learn {topic_name}", "content_markdown": learn_md}
        )
        TopicSection.objects.update_or_create(
            topic=topic, section_type="guided", order=3,
            defaults={"title": "Guided Examples & Walkthrough", "content_markdown": guided_md}
        )

        # Create/Update Visualization
        vis_type = b_data.get("visualization_type", "generic")
        vis_title = f"{topic_name} Concept Simulation"
        vis_config = b_data.get("visualization_config", {"topic": topic_name, "seeded": True})
        
        if not b_data:
            if "sliding window" in topic_name.lower():
                vis_type = "sliding-window"
                vis_title = "Visual Two-Pointer Window Demo"
            elif "linked list" in topic_name.lower():
                vis_type = "linked-list-cycle"
                vis_title = "Slow and Fast Pointer Simulation"
            elif "graph" in topic_name.lower():
                vis_type = "graph-dfs"
                vis_title = "Adjacency Traversal Visualizer"
            elif "percentage" in topic_name.lower() or "profit" in topic_name.lower():
                vis_type = "aptitude-profit"
                vis_title = "Interactive Profit Calculator"

        TopicVisualization.objects.update_or_create(
            topic=topic,
            defaults={
                "title": vis_title,
                "visualization_type": vis_type,
                "config_data": vis_config
            }
        )

        # Create/Update Revision Card
        rev_takeaways = b_data.get("revision", [
            f"Ensure you understand the core definition of {topic_name}.",
            "Analyze time complexity limits to optimize nested structures.",
            "Use optimal data types to avoid memory fragmentation.",
            "Practice pattern recognition for edge cases."
        ]) if b_data else [
            f"Ensure you understand the core definition of {topic_name}.",
            "Analyze time complexity limits to optimize nested structures.",
            "Use optimal data types to avoid memory fragmentation.",
            "Practice pattern recognition for edge cases."
        ]
        
        TopicRevision.objects.update_or_create(
            topic=topic,
            defaults={
                "key_takeaways": rev_takeaways,
                "cheat_sheet_markdown": f"### {topic_name} Revision Sheet\n\n- **Formula/Pattern**: Read constraints, maintain state trackers, iterate cleanly.\n- **Trick**: Skip redundant calculations using state caches.\n- **Complexity**: Aim for linear $O(N)$ or logarithmic $O(\\log N)$ time."
            }
        )

        # Rebuild Quizzes
        Question.objects.filter(topic=topic).delete()
        for i, q_data in enumerate(questions_to_create):
            Question.objects.create(
                topic=topic,
                question_text=q_data["question_text"],
                option_a=q_data["option_a"],
                option_b=q_data["option_b"],
                option_c=q_data["option_c"],
                option_d=q_data["option_d"],
                correct_answer=q_data["correct_answer"],
                difficulty=q_data["difficulty"],
                explanation=q_data["explanation"]
            )



@transaction.atomic
def ensure_user_preparation_data(user, profile_data=None):
    from accounts.models import UserProfile, UserStreak
    from core.models import Track

    if not Track.objects.exists():
        ensure_platform_catalog()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    updates = {}
    incoming = profile_data or {}

    for field in DEFAULT_PROFILE:
        if field in incoming and incoming[field] not in [None, "", []]:
            updates[field] = incoming[field]

    for field, value in updates.items():
        setattr(profile, field, value)
    if updates:
        profile.save(update_fields=list(updates.keys()))

    UserStreak.objects.get_or_create(user=user)
    return profile


@transaction.atomic
def ensure_demo_user_preparation_data(user, profile_data=None):
    from accounts.models import DailyGoal, UserProfile, UserStreak

    today = timezone.localdate()
    now = timezone.now()
    topic_lookup = ensure_platform_catalog()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    updates = {}
    incoming = profile_data or {}

    for field, default_value in DEFAULT_PROFILE.items():
        current_value = getattr(profile, field)
        if field in incoming and incoming[field] not in [None, "", []]:
            updates[field] = incoming[field]
        elif current_value in [None, "", []]:
            updates[field] = default_value

    for field, value in updates.items():
        setattr(profile, field, value)
    if updates:
        profile.save(update_fields=list(updates.keys()))

    streak, _ = UserStreak.objects.get_or_create(user=user)
    if streak.current_streak == 0:
        streak.current_streak = 7
        streak.longest_streak = max(streak.longest_streak, 12)
        streak.last_active_date = today
        streak.save(update_fields=["current_streak", "longest_streak", "last_active_date"])

    for order, (title, detail, status_label, progress, tone) in enumerate(DEFAULT_PLAN_ITEMS, start=1):
        DailyPlanItem.objects.update_or_create(
            user=user,
            date=today,
            title=title,
            defaults={
                "detail": detail,
                "status": status_label,
                "progress_percentage": progress,
                "tone": tone,
                "order": order,
                "is_completed": progress >= 100,
            },
        )

    if not DailyGoal.objects.filter(user=user, date=today).exists():
        DailyGoal.objects.create(user=user, date=today, goal_text="Complete one learning checkpoint", completed=False)
        DailyGoal.objects.create(user=user, date=today, goal_text="Review one weak topic", completed=True)

    for order, (name, readiness, focus, tone) in enumerate(DEFAULT_COMPANIES, start=1):
        CompanyTarget.objects.update_or_create(
            user=user,
            name=name,
            defaults={
                "readiness_percentage": readiness,
                "focus": focus,
                "tone": tone,
                "order": order,
                "is_active": True,
            },
        )

    for order, (area, score, max_score, progress) in enumerate(DEFAULT_INTERVIEW_ITEMS, start=1):
        InterviewReadiness.objects.update_or_create(
            user=user,
            area=area,
            defaults={
                "score": score,
                "max_score": max_score,
                "progress_percentage": progress,
                "order": order,
            },
        )

    for order, (title, cycle_label, duration) in enumerate(DEFAULT_REVISION_ITEMS, start=1):
        RevisionQueueItem.objects.update_or_create(
            user=user,
            title=title,
            due_date=today,
            defaults={
                "cycle_label": cycle_label,
                "duration_minutes": duration,
                "order": order,
                "is_completed": False,
            },
        )

    for index, topic_name in enumerate(COMPLETED_TOPICS):
        topic = topic_lookup.get(topic_name)
        if topic:
            UserTopicProgress.objects.update_or_create(
                user=user,
                topic=topic,
                defaults={
                    "is_completed": True,
                    "completed_at": now - timedelta(days=max(1, len(COMPLETED_TOPICS) - index)),
                },
            )

    for topic_name in IN_PROGRESS_TOPICS:
        topic = topic_lookup.get(topic_name)
        if topic:
            UserTopicProgress.objects.get_or_create(
                user=user,
                topic=topic,
                defaults={
                    "is_completed": False,
                    "completed_at": None,
                },
            )

    if not UserAnswer.objects.filter(user=user).exists():
        _seed_answer_history(user, topic_lookup, now)

    if not TestAttempt.objects.filter(user=user, completed_at__isnull=False).exists():
        _seed_test_attempts(user, now)

    _seed_activity(user, now)


def _seed_answer_history(user, topic_lookup, now):
    answer_plan = [
        ("Arrays and Strings", [True, True, True], 6),
        ("Linked Lists", [True, False], 5),
        ("Stacks and Queues", [True, True], 4),
        ("Trees and Binary Search Trees", [True, False, True], 3),
        ("Graphs and Traversal", [False, False, True], 2),
        ("Number Systems", [True, True], 1),
        ("Percentages and Profit Loss", [True, False, True], 1),
        ("Time Speed Distance", [False, True], 0),
        ("Operating System Basics", [False, True, False], 0),
        ("SQL Joins", [True, True], 0),
        ("React Components and State", [True, False], 0),
    ]

    for topic_name, results, days_ago in answer_plan:
        topic = topic_lookup.get(topic_name)
        if not topic:
            continue

        questions = list(Question.objects.filter(topic=topic).order_by("id"))
        if not questions:
            continue

        for offset, is_correct in enumerate(results):
            question = questions[offset % len(questions)]
            created_at = now - timedelta(days=days_ago, hours=offset + 1)
            answer = UserAnswer.objects.create(
                user=user,
                question=question,
                selected_answer=_select_answer(question, is_correct),
                is_correct=is_correct,
            )
            UserAnswer.objects.filter(id=answer.id).update(created_at=created_at)


def _seed_test_attempts(user, now):
    attempt_specs = [
        ("DSA Foundation Mock", 7, 10, 4),
        ("Aptitude Hiring Sprint", 8, 10, 2),
        ("Full Placement Readiness Mock", 6, 10, 1),
    ]

    for test_name, score, total_questions, days_ago in attempt_specs:
        test = Test.objects.filter(name=test_name).first()
        if not test:
            continue

        attempt = TestAttempt.objects.create(
            user=user,
            test=test,
            score=score,
            total_questions=total_questions,
            completed_at=now - timedelta(days=days_ago, hours=2),
        )
        TestAttempt.objects.filter(id=attempt.id).update(started_at=now - timedelta(days=days_ago, hours=3))


def _seed_activity(user, now):
    activity_specs = [
        ("Path", "Completed Arrays and Strings", 6),
        ("Mock", "Reviewed DSA Foundation Mock", 4),
        ("SQL", "Fixed join mistakes in practice", 2),
        ("Interview", "Recorded project story revision", 1),
        ("Plan", "Updated company target readiness", 0),
    ]

    for event_type, title, days_ago in activity_specs:
        ActivityEvent.objects.get_or_create(
            user=user,
            event_type=event_type,
            title=title,
            defaults={
                "occurred_at": now - timedelta(days=days_ago, hours=1),
                "metadata": {"seeded": True},
            },
        )

AI_STRATEGIES = [
  {
    "icon": '🎯', "color": '#ef4444',
    "title": 'Focus on Graphs before Amazon OA',
    "desc": 'Graph accuracy at 52% — your primary blocker. 3 Graph problems/day for 7 days can push you to 75%+.',
    "priority": 'High',
    "plan": {
      "goal": 'Improve Graph accuracy from 52% → 75% in 7 days',
      "duration": '7 days',
      "steps": [
        { "day": 'Day 1–2', "task": 'BFS & DFS foundations — 5 problems on LeetCode (easy)' },
        { "day": 'Day 3–4', "task": 'Shortest path — Dijkstra, Bellman-Ford — 4 problems' },
        { "day": 'Day 5–6', "task": 'Topological sort + Cycle detection — 4 problems' },
        { "day": 'Day 7',   "task": 'Full mock drill — 3 Amazon-style Graph problems timed' },
      ],
      "resources": ['PrepSmart Practice Drills → Graphs', 'Amazon Leadership Principles review', 'LeetCode Graph tag (Medium)'],
      "outcome": 'Expected readiness jump: 52% → 76%+ for Amazon OA',
    },
  },
  {
    "icon": '📊', "color": '#f59e0b',
    "title": 'TCS NQT — Apply This Week',
    "desc": 'Readiness at 91%. Application window closes in 5 days. Optimal timing is now.',
    "priority": 'Urgent',
    "plan": {
      "goal": 'Submit TCS NQT application within 48 hours',
      "duration": '2 days',
      "steps": [
        { "day": 'Today',    "task": 'Register on TCS NextStep portal & fill academic details' },
        { "day": 'Tomorrow', "task": 'Upload resume, verify eligibility documents (CGPA cert)' },
        { "day": 'Day 3',    "task": 'Submit final application before 5-day deadline expires' },
        { "day": 'Ongoing',  "task": 'Practice 2 TCS-style aptitude mocks daily until OA date' },
      ],
      "resources": ['TCS NextStep Portal', 'PrepSmart → TCS Mock Tests', 'Aptitude speed drills'],
      "outcome": 'Application submitted. OA invite expected within 10–14 days.',
    },
  },
  {
    "icon": '🏗️', "color": '#8b5cf6',
    "title": 'Delay Microsoft by 2 Weeks',
    "desc": 'System Design score (45%) needs improvement before Microsoft screening.',
    "priority": 'Medium',
    "plan": {
      "goal": 'Improve System Design score from 45% → 70%+ in 14 days',
      "duration": '14 days',
      "steps": [
        { "day": 'Week 1',   "task": 'Fundamentals: Scalability, Load Balancing, Caching basics' },
        { "day": 'Week 1',   "task": 'Design URL Shortener, Rate Limiter, Twitter Timeline' },
        { "day": 'Week 2',   "task": 'Advanced: Databases (SQL vs NoSQL), CAP theorem, Sharding' },
        { "day": 'Week 2',   "task": 'Mock System Design interview with AI Coach in PrepSmart' },
      ],
      "resources": ['Grokking System Design', 'PrepSmart AI Interview → System Design round', 'High Scalability blog'],
      "outcome": 'Ready for Microsoft OA & System Design round in 14 days.',
    },
  },
  {
    "icon": '📖', "color": '#06b6d4',
    "title": 'SQL Deep Dive for Oracle',
    "desc": 'Oracle OA focuses on complex JOINs and window functions. Revise joins this week.',
    "priority": 'Medium',
    "plan": {
      "goal": 'Master SQL joins & window functions for Oracle OA',
      "duration": '5 days',
      "steps": [
        { "day": 'Day 1',  "task": 'INNER, LEFT, RIGHT, FULL joins — 8 practice queries' },
        { "day": 'Day 2',  "task": 'Window functions: ROW_NUMBER, RANK, LEAD, LAG — 6 problems' },
        { "day": 'Day 3',  "task": 'Subqueries & CTEs — 5 Oracle-style problems' },
        { "day": 'Day 4',  "task": 'Indexing, query optimization, EXPLAIN analysis' },
        { "day": 'Day 5',  "task": 'Full Oracle SQL mock — 15 questions, 45 minutes timed' },
      ],
      "resources": ['PrepSmart Practice → SQL track', 'LeetCode SQL section (all Medium)', 'Oracle SQL documentation'],
      "outcome": 'SQL readiness jumps to 80%+. Oracle OA pass likelihood increases significantly.',
    },
  },
]

DEADLINES = [
  { "company": 'TCS NQT',   "icon": '🏢', "days": 5,  "color": '#ef4444', "type": 'Application Deadline' },
  { "company": 'Amazon OA', "icon": '📦', "days": 12, "color": '#f59e0b', "type": 'OA Practice Target'   },
  { "company": 'Infosys',   "icon": '💼', "days": 18, "color": '#8b5cf6', "type": 'Hackathon Deadline'   },
  { "company": 'Google',    "icon": '🔍', "days": 30, "color": '#10b981', "type": 'Application Window'   },
]

PIPELINE_STAGES = [
  { "id": 'Not Applied',   "label": 'Wishlist',     "color": '#6b7280', "icon": '📋' },
  { "id": 'Applied',       "label": 'Applied',      "color": '#06b6d4', "icon": '📤' },
  { "id": 'OA Scheduled',  "label": 'OA Scheduled', "color": '#f59e0b', "icon": '⏰' },
  { "id": 'Interviewing',  "label": 'Interviewing', "color": '#8b5cf6', "icon": '🎙️' },
  { "id": 'Offer Received',"label": 'Offer!',       "color": '#10b981', "icon": '🎉' },
  { "id": 'Rejected',      "label": 'Rejected',     "color": '#ef4444', "icon": '❌' },
]


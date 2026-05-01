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
    ("TCS", 76, "Aptitude speed and communication polish", "green"),
    ("Infosys", 69, "DBMS, OOP, and coding consistency", "amber"),
    ("Accenture", 63, "Verbal confidence and project explanation", "amber"),
    ("Zoho", 54, "DSA depth and hands-on coding rounds", "red"),
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
        "hiring_signal": "Strong target for students who code cleanly and can solve practical problems without over-explaining.",
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


@transaction.atomic
def ensure_user_preparation_data(user, profile_data=None):
    from accounts.models import DailyGoal, UserProfile, UserStreak

    today = timezone.localdate()
    now = timezone.now()
    topic_lookup = ensure_platform_catalog()

    profile, _ = UserProfile.objects.get_or_create(user=user, defaults=DEFAULT_PROFILE)
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

"""
Static data for AI Study Guide Modules.
Refactored from views.py for maintainability.
"""

INTERVIEW_TYPES = [
    {
        "id": 'hr', "icon": '🤝', "label": 'HR & Culture Fit', "color": '#6366f1',
        "difficulty": 'Easy', "duration": 20, "focus": ['Communication', 'Culture', 'Goals'],
        "description": 'Master the classic HR questions to prove your motivation and company fit.',
    },
    {
        "id": 'dsa', "icon": '💻', "label": 'Data Structures', "color": '#10b981',
        "difficulty": 'Hard', "duration": 45, "focus": ['Algorithms', 'Complexity', 'Logic'],
        "badge": '🔥 High Demand',
        "description": 'Detailed walkthroughs on optimizing arrays, strings, trees, and graphs.',
    },
    {
        "id": 'behavioral', "icon": '🌟', "label": 'Behavioral & STAR', "color": '#f59e0b',
        "difficulty": 'Medium', "duration": 30, "focus": ['Conflict', 'Leadership', 'Failures'],
        "description": 'Structure your experiences perfectly using the STAR method to win over interviewers.',
    },
    {
        "id": 'system_design', "icon": '🏗️', "label": 'System Design', "color": '#8b5cf6',
        "difficulty": 'Expert', "duration": 60, "focus": ['Architecture', 'Scaling', 'Databases'],
        "badge": '⭐ Senior Role',
        "description": 'Learn how to architect scalable systems like Netflix, Twitter, and URL shorteners.',
    },
    {
        "id": 'react', "icon": '⚛️', "label": 'Frontend & React', "color": '#0ea5e9',
        "difficulty": 'Medium', "duration": 35, "focus": ['Hooks', 'State', 'Performance'],
        "description": 'Deep dive into React internals, Virtual DOM, Custom Hooks, and Web Vitals.',
    },
    {
        "id": 'sql', "icon": '🗄️', "label": 'SQL & Databases', "color": '#eab308',
        "difficulty": 'Medium', "duration": 30, "focus": ['Queries', 'Indexing', 'Normalization'],
        "description": 'Understand complex JOINs, indexing strategies, and database normalization forms.',
    },
    {
        "id": 'ml', "icon": '🤖', "label": 'Machine Learning', "color": '#ec4899',
        "difficulty": 'Hard', "duration": 45, "focus": ['Models', 'Evaluation', 'Math'],
        "description": 'Core ML concepts, bias-variance tradeoff, and evaluation metrics explained.',
    },
    {
        "id": 'pm', "icon": '📊', "label": 'Product Management', "color": '#14b8a6',
        "difficulty": 'Medium', "duration": 40, "focus": ['Strategy', 'Metrics', 'Execution'],
        "description": 'Nail product sense, execution cases, and product metric deep-dives.',
    },
    {
        "id": 'core_cs', "icon": '🖥️', "label": 'Core CS (OS/Net)', "color": '#64748b',
        "difficulty": 'Hard', "duration": 40, "focus": ['OS', 'Networks', 'DBMS'],
        "description": 'Fundamental concepts of operating systems, networking layers, and concurrency.',
    },
    {
        "id": 'leadership', "icon": '👑', "label": 'Leadership', "color": '#f43f5e',
        "difficulty": 'Medium', "duration": 30, "focus": ['Mentorship', 'Vision', 'Delegation'],
        "description": 'For leads and managers. Cover delegation, resolving team conflicts, and driving vision.',
    }
]

INTERVIEW_QUESTIONS = {
    "hr": [
        {
            "question": "Tell me about yourself.",
            "area": "Introduction",
            "blueprint": {
                "context": "Interviewers use this to break the ice and gauge your communication skills. They want a concise professional summary, not your life story.",
                "what_to_say": "- Your current role/status.\n- 2-3 key professional achievements.\n- Why you are interested in this specific role.",
                "what_not_to_say": "- Personal details (hobbies, family) unless directly relevant.\n- A chronological recounting of your entire resume.",
                "example_answer": "I'm currently a software engineer at X, where I focus on backend systems. Recently, I led a project that improved API latency by 30%. I'm looking to bring my expertise in scalable architectures to your team.",
                "behavioral": "Maintain eye contact, smile naturally, and keep it under 2 minutes."
            }
        },
        {
            "question": "What is your biggest weakness?",
            "area": "Self-Awareness",
            "blueprint": {
                "context": "They are testing your self-awareness and willingness to improve. They want to see that you can identify a real flaw and take steps to mitigate it.",
                "what_to_say": "- A genuine, but not deal-breaking, weakness.\n- The specific, actionable steps you are taking to overcome it.",
                "what_not_to_say": "- Fake weaknesses ('I work too hard', 'I care too much').\n- Core competencies required for the job (e.g., 'I am bad at coding' for a dev role).",
                "example_answer": "I sometimes struggle with delegating tasks, preferring to do things myself to ensure quality. However, I've started using project management tools to clearly assign tasks and trust my team, which has improved our overall velocity.",
                "behavioral": "Speak thoughtfully and show genuine reflection."
            }
        },
        {
            "question": "Why do you want to work here?",
            "area": "Motivation",
            "blueprint": {
                "context": "To ensure you're genuinely interested in the company and haven't just mass-applied. They want to see if your values align with theirs.",
                "what_to_say": "- Specific details about the company's product, mission, or culture.\n- How your skills and career goals align with their trajectory.",
                "what_not_to_say": "- Generic statements ('It is a great company').\n- Focusing solely on perks, salary, or location.",
                "example_answer": "I've been following your recent shift towards AI-driven products. My background is in machine learning, and I'm deeply passionate about building intelligent tools that scale. Your engineering culture of continuous learning aligns perfectly with how I work.",
                "behavioral": "Show enthusiasm and passion for the company's domain."
            }
        }
    ],
    "dsa": [
        {
            "question": "How would you find a cycle in a Linked List?",
            "area": "Data Structures",
            "blueprint": {
                "context": "A classic algorithm question testing your knowledge of pointers and space complexity optimization (Floyd's Cycle-Finding Algorithm).",
                "what_to_say": "- Mention the 'Fast and Slow pointer' (Tortoise and Hare) approach.\n- Explain that if there is a cycle, the fast pointer will eventually meet the slow pointer.\n- State Time Complexity: O(N) and Space Complexity: O(1).",
                "what_not_to_say": "- Jumping straight into a Hash Set solution without mentioning the O(1) space alternative.\n- Struggling with edge cases like empty lists.",
                "example_answer": "I would use Floyd's Tortoise and Hare algorithm. I'd initialize two pointers, slow and fast. Slow moves one step, fast moves two. If they ever meet, a cycle exists. If fast reaches null, there's no cycle. This is O(N) time and O(1) space.",
                "behavioral": "Use a whiteboard or hand gestures to visually explain the pointers moving."
            }
        },
        {
            "question": "Explain the time complexity of Binary Search.",
            "area": "Algorithms",
            "blueprint": {
                "context": "Tests fundamental understanding of logarithmic time complexity and how search space reduction works.",
                "what_to_say": "- The time complexity is O(log N).\n- Explain WHY: At each step, the search space is divided in half (N, N/2, N/4... 1).\n- Note that the array must be sorted first.",
                "what_not_to_say": "- Just saying 'O(log N)' without explaining the math behind the halving process.\n- Confusing it with O(N) linear search.",
                "example_answer": "Binary search has a time complexity of O(log N) because in each iteration, we compare the target to the middle element and discard half of the remaining search space. This halving continues until the space is reduced to 1.",
                "behavioral": "Speak confidently; this is a fundamental concept you should know cold."
            }
        },
        {
            "question": "What is Dynamic Programming?",
            "area": "Optimization",
            "blueprint": {
                "context": "Evaluates your ability to optimize recursive algorithms by avoiding redundant calculations.",
                "what_to_say": "- It's a method for solving complex problems by breaking them down into simpler subproblems.\n- Mention the two key properties: Overlapping Subproblems and Optimal Substructure.\n- Mention Memoization (Top-Down) and Tabulation (Bottom-Up).",
                "what_not_to_say": "- Defining it as just 'recursion'.\n- Failing to mention caching/storing results.",
                "example_answer": "Dynamic programming is an optimization technique where we solve a complex problem by breaking it into smaller overlapping subproblems. By storing the results of these subproblems—either via memoization or tabulation—we avoid redundant work, reducing time complexity from exponential to polynomial.",
                "behavioral": "Relate it to a real-world problem like Fibonacci to make the explanation concrete."
            }
        }
    ],
    "behavioral": [
        {
            "question": "Describe a time you had a conflict with a coworker.",
            "area": "Conflict Resolution",
            "blueprint": {
                "context": "Assesses your maturity, empathy, and ability to collaborate even when disagreements arise.",
                "what_to_say": "- Use the STAR method (Situation, Task, Action, Result).\n- Focus on the *Action*: How you communicated calmly, sought to understand their perspective, and found a compromise.\n- Highlight a positive *Result*.",
                "what_not_to_say": "- Blaming the coworker entirely.\n- Claiming you never have conflicts (unrealistic).",
                "example_answer": "We disagreed on the architecture for a new feature. Instead of arguing, I scheduled a 1-on-1. I listened to their concerns about scalability, and we realized our goals were aligned. We drafted a hybrid approach that satisfied both needs. The feature launched smoothly and our working relationship strengthened.",
                "behavioral": "Maintain a calm, positive tone. Never speak poorly of former colleagues."
            }
        },
        {
            "question": "Tell me about a time you failed.",
            "area": "Resilience",
            "blueprint": {
                "context": "Evaluates accountability and growth mindset. They want to see that you take responsibility and learn from mistakes.",
                "what_to_say": "- Pick a real, specific failure where you were at fault (but not one that caused catastrophic damage).\n- Take absolute ownership.\n- Emphasize what you learned and how you changed your processes.",
                "what_not_to_say": "- Blaming external factors or team members.\n- Framing a success as a failure ('I worked too hard on it').",
                "example_answer": "Early in my career, I deployed a change without full test coverage, causing a minor production bug. I immediately rolled it back and took responsibility. To ensure it didn't happen again, I championed a mandatory peer-review and CI/CD testing policy for our team. It taught me the critical value of robust safety nets.",
                "behavioral": "Show humility and focus heavily on the learning outcome."
            }
        },
        {
            "question": "Describe a time you showed leadership without a formal title.",
            "area": "Leadership",
            "blueprint": {
                "context": "Companies want proactive employees who take initiative and guide others, regardless of their official rank.",
                "what_to_say": "- A situation where a project lacked direction or a team member needed help.\n- How you stepped up, organized the effort, and drove the outcome.\n- Emphasize collaboration, not bossiness.",
                "what_not_to_say": "- A story where you just did your assigned job.\n- Sounding arrogant or dismissive of actual managers.",
                "example_answer": "Our team was struggling with a massive backlog of technical debt. No one was formally assigned to it. I took the initiative to categorize the issues, proposed a 'Tech Debt Friday' to management, and guided junior devs through the fixes. Over a quarter, we reduced bugs by 40%.",
                "behavioral": "Use 'I' for your initiative, but 'We' for the team's success."
            }
        }
    ],
    "system_design": [
        {
            "question": "How would you design a URL Shortener like Bitly?",
            "area": "Architecture",
            "blueprint": {
                "context": "A foundational system design question testing capacity estimation, API design, database choice, and hash generation.",
                "what_to_say": "- Discuss Requirements (Read heavy? High availability?).\n- Mention Capacity Estimation (traffic, storage).\n- Propose an API (create_url, get_url).\n- Discuss the shortening logic (Base62 encoding of a unique ID/DB auto-increment).\n- Mention caching (Redis) for fast redirects.",
                "what_not_to_say": "- Diving into code immediately.\n- Ignoring the difference between read and write ratios.",
                "example_answer": "I'd start by defining it as a read-heavy system (100:1 read/write ratio). We need a highly available database, likely NoSQL like Cassandra for scalability. For the shortening, I'd use an offline Key Generation Service (KGS) that pre-generates unique Base62 strings. When a user requests a short link, we pop one from KGS. We'd heavily cache redirects in Redis to ensure low latency.",
                "behavioral": "Drive the conversation. Treat the interviewer as a collaborator. Draw boxes if possible."
            }
        },
        {
            "question": "SQL vs NoSQL: When to choose which?",
            "area": "Data Storage",
            "blueprint": {
                "context": "Evaluates your understanding of database paradigms, ACID properties, and horizontal vs vertical scaling.",
                "what_to_say": "- Choose SQL for complex relationships, ACID compliance, and structured schemas (e.g., financial systems).\n- Choose NoSQL for flexible schemas, massive horizontal scaling, and unstructured/semi-structured data (e.g., social media feeds, logs).",
                "what_not_to_say": "- Saying one is strictly 'better' or 'faster' than the other without context.",
                "example_answer": "I choose SQL when data integrity and ACID compliance are paramount, like in banking or inventory management. I opt for NoSQL, like MongoDB or Cassandra, when I need highly flexible schemas, rapid development, or massive horizontal scalability for read/write heavy workloads like IoT telemetry or user activity logs.",
                "behavioral": "Use specific examples of technologies (PostgreSQL, Cassandra) to show practical experience."
            }
        },
        {
            "question": "Explain the concept of a Load Balancer.",
            "area": "Scalability",
            "blueprint": {
                "context": "Tests knowledge of how to distribute traffic to prevent single points of failure and ensure high availability.",
                "what_to_say": "- It distributes incoming network traffic across multiple servers.\n- Mention routing algorithms (Round Robin, Least Connections).\n- Briefly mention L4 (Transport) vs L7 (Application) load balancing.",
                "what_not_to_say": "- Confusing a load balancer with a reverse proxy (though they often overlap, distinctions matter).",
                "example_answer": "A load balancer acts as a traffic cop, distributing incoming requests across a cluster of servers to ensure no single server is overwhelmed. It improves responsiveness and availability. Algorithms like Least Connections are common. They can operate at Layer 4, routing based on IP/Port, or Layer 7, routing based on HTTP headers.",
                "behavioral": "Use analogies (like a traffic cop or a bank teller line) if explaining to a non-technical stakeholder."
            }
        }
    ],
    "react": [
        {
            "question": "Explain the Virtual DOM and how React renders it.",
            "area": "React Internals",
            "blueprint": {
                "context": "Fundamental understanding of why React is fast and how its core rendering engine operates.",
                "what_to_say": "- The Virtual DOM is a lightweight JavaScript representation of the actual DOM.\n- React creates a new Virtual DOM tree on state change, compares it with the previous one (Diffing/Reconciliation).\n- It then batches the minimum necessary updates to the real DOM.",
                "what_not_to_say": "- Saying 'Virtual DOM is faster than the real DOM' (it's the *batching of updates* that makes it efficient, touching the real DOM is still slow).",
                "example_answer": "The Virtual DOM is an in-memory representation of the real DOM. When state changes, React creates a new Virtual DOM tree. It uses a diffing algorithm (Reconciliation) to compare the new tree with the old one, calculates the exact differences, and then applies only those specific changes to the real DOM in a single batch update.",
                "behavioral": "Use clear, precise vocabulary like 'Reconciliation' and 'Diffing Algorithm'."
            }
        },
        {
            "question": "What is the useEffect hook and how do you prevent infinite loops?",
            "area": "React Hooks",
            "blueprint": {
                "context": "useEffect is the most complex standard hook. They want to know you understand the dependency array and side effects.",
                "what_to_say": "- Used for side effects (fetching data, subscriptions, DOM manipulation).\n- The dependency array controls when it fires.\n- Infinite loops happen when state is updated inside the effect without proper dependencies, causing continuous re-renders.",
                "what_not_to_say": "- Confusing it with lifecycle methods exactly (it's about synchronization, not just mount/unmount).",
                "example_answer": "useEffect lets you synchronize a component with an external system. To prevent infinite loops, you must accurately declare dependencies in the second argument array. If you update state inside the effect, and that state is in the dependency array (or causes a re-render that triggers the effect again), it loops. I use the ESLint exhaustive-deps rule to catch this.",
                "behavioral": "Mentioning ESLint rules shows practical, production-level experience."
            }
        },
        {
            "question": "How do you manage global state in a React application?",
            "area": "State Management",
            "blueprint": {
                "context": "Tests architectural decision making. When do you use Context API vs Redux vs Zustand?",
                "what_to_say": "- Mention Context API for simple, low-frequency updates (theme, auth).\n- Mention Redux, Zustand, or Recoil for complex, high-frequency state.\n- Mention Server State tools like React Query or RTK Query for API data.",
                "what_not_to_say": "- 'I always use Redux for everything' (shows lack of nuance).",
                "example_answer": "It depends on the scope. For UI theme or user auth, React's built-in Context API is sufficient. For complex client-side state, I prefer Zustand because it's lightweight and avoids boilerplate. However, for server state—like caching API responses—I use React Query, as it handles loading, error states, and caching automatically.",
                "behavioral": "Showcase pragmatism. 'It depends' is a great way to start architecture answers."
            }
        }
    ],
    "sql": [
        {
            "question": "Explain the difference between INNER JOIN and LEFT JOIN.",
            "area": "Queries",
            "blueprint": {
                "context": "The most fundamental SQL question. Tests your ability to combine relational data accurately.",
                "what_to_say": "- INNER JOIN returns only the rows where there is a match in BOTH tables.\n- LEFT JOIN returns ALL rows from the left table, and the matched rows from the right table (with NULLs if no match).",
                "what_not_to_say": "- Rambling or confusing the left and right tables.",
                "example_answer": "An INNER JOIN returns records that have matching values in both tables. A LEFT JOIN returns all records from the left table, regardless of whether there's a match. If there is no match in the right table, the result will contain NULL for those columns.",
                "behavioral": "Visualize Venn diagrams if it helps you explain clearly."
            }
        },
        {
            "question": "What is Database Indexing and how does it work?",
            "area": "Performance",
            "blueprint": {
                "context": "Crucial for backend performance. Tests understanding of B-Trees and read/write tradeoffs.",
                "what_to_say": "- An index is a data structure (often a B-Tree) that improves data retrieval speed.\n- It works like an index in a book.\n- Tradeoff: Indexes speed up SELECTs but slow down INSERTs/UPDATEs because the index must be updated.",
                "what_not_to_say": "- 'Just index every column' (ignores the write penalty).",
                "example_answer": "Indexing creates a separate data structure, typically a B-Tree, that allows the database to find rows quickly without scanning the entire table. It drastically speeds up read operations. However, the tradeoff is that write operations (inserts, updates) become slower because the index must be maintained, and it consumes extra disk space.",
                "behavioral": "Always mention the tradeoffs. Senior engineers understand there is no free lunch."
            }
        },
        {
            "question": "What are ACID properties in a database?",
            "area": "Transactions",
            "blueprint": {
                "context": "Tests foundational knowledge of database reliability and transaction integrity.",
                "what_to_say": "- Atomicity (all or nothing).\n- Consistency (valid state to valid state).\n- Isolation (concurrent transactions don't interfere).\n- Durability (committed data is permanent).",
                "what_not_to_say": "- Forgetting one of the letters or mixing up Isolation and Consistency.",
                "example_answer": "ACID stands for Atomicity, meaning a transaction is all-or-nothing. Consistency ensures the database moves from one valid state to another. Isolation guarantees that concurrent transactions execute as if they were sequential, preventing dirty reads. Durability ensures that once committed, data survives even system crashes.",
                "behavioral": "Provide a quick real-world example like a bank transfer to illustrate Atomicity."
            }
        }
    ],
    "ml": [
        {
            "question": "Explain the Bias-Variance Tradeoff.",
            "area": "Model Fundamentals",
            "blueprint": {
                "context": "The most fundamental concept in supervised learning. Evaluates understanding of underfitting and overfitting.",
                "what_to_say": "- Bias is error from erroneous assumptions (Underfitting).\n- Variance is error from sensitivity to small fluctuations in training data (Overfitting).\n- The tradeoff is finding the sweet spot that minimizes total error.",
                "what_not_to_say": "- Confusing Bias (statistical) with human bias in datasets.",
                "example_answer": "High bias means the model is too simple and underfits the data, missing underlying patterns. High variance means the model is too complex and overfits, memorizing noise in the training data rather than generalizing. The tradeoff is tuning the model complexity to find the sweet spot where total error on unseen data is minimized.",
                "behavioral": "Use the dartboard analogy (clustered off-center vs spread out) for clarity."
            }
        },
        {
            "question": "What is the difference between Supervised and Unsupervised Learning?",
            "area": "Machine Learning Types",
            "blueprint": {
                "context": "Tests basic categorization of ML algorithms and data requirements.",
                "what_to_say": "- Supervised learning uses labeled data (input-output pairs) to predict outcomes (Regression/Classification).\n- Unsupervised learning uses unlabeled data to find hidden structures (Clustering/Association).",
                "what_not_to_say": "- Failing to mention 'labeled vs unlabeled' data.",
                "example_answer": "Supervised learning requires labeled training data to learn a mapping from inputs to outputs, commonly used for classification or regression. Unsupervised learning deals with unlabeled data, where the algorithm tries to find inherent structure, like clustering customers by purchasing behavior.",
                "behavioral": "Provide one concrete algorithm for each (e.g., Random Forest for supervised, K-Means for unsupervised)."
            }
        },
        {
            "question": "How do you evaluate a classification model dealing with an imbalanced dataset?",
            "area": "Evaluation Metrics",
            "blueprint": {
                "context": "A classic trap. Accuracy is useless on imbalanced data. Evaluates practical ML experience.",
                "what_to_say": "- Do NOT use Accuracy.\n- Use Precision, Recall, and the F1-Score.\n- Mention the AUC-ROC curve.\n- Briefly mention techniques like SMOTE or class weighting.",
                "what_not_to_say": "- Suggesting Accuracy as the primary metric (a red flag).",
                "example_answer": "Accuracy is misleading for imbalanced data. If 99% of transactions are legitimate, a model predicting 'legitimate' always gets 99% accuracy but fails to catch fraud. Instead, I use Precision (how many predicted frauds were actual frauds) and Recall (how many actual frauds were caught). The F1-score provides a harmonic mean of the two. I'd also look at the PR-AUC curve.",
                "behavioral": "Speak confidently about why accuracy fails. It shows real-world scars."
            }
        }
    ],
    "pm": [
        {
            "question": "How would you prioritize features for a new product?",
            "area": "Strategy",
            "blueprint": {
                "context": "Evaluates strategic thinking, user empathy, and frameworks for decision making.",
                "what_to_say": "- Mention a framework (RICE, Kano, or Value vs Effort).\n- Emphasize aligning with company goals and user needs.\n- Discuss using data and user feedback to drive decisions.",
                "what_not_to_say": "- 'I just build what the CEO wants' or 'Whatever I think is coolest'.",
                "example_answer": "I align prioritization with the core business goals and user pain points. I typically use the RICE framework—Reach, Impact, Confidence, and Effort. I'd gather quantitative data from product analytics and qualitative data from user interviews to estimate Impact and Confidence, then work with engineering to size the Effort. This ensures we deliver maximum value quickly.",
                "behavioral": "Show structure. PMs need to bring order to chaos."
            }
        },
        {
            "question": "Design an elevator for a 100-story building.",
            "area": "Product Sense",
            "blueprint": {
                "context": "A classic product design question to test how you identify users, pain points, and creative solutions.",
                "what_to_say": "- Clarify the goal and users (Residents? Office workers? Freight?).\n- Identify pain points (Wait times, crowding during rush hour).\n- Propose solutions (Express elevators, smart dispatch systems where users select floors before entering).",
                "what_not_to_say": "- Jumping straight into the physical dimensions of the elevator car.",
                "example_answer": "First, let's define the users—is this commercial or residential? Assuming commercial, the main pain point is rush hour wait times. Instead of a standard button interface, I'd design a destination dispatch system. Users swipe their badge at the lobby, and the screen directs them to a specific elevator grouped with others going to nearby floors, optimizing the routing algorithm and minimizing stops.",
                "behavioral": "Think out loud and explicitly walk through: Users -> Pain Points -> Solutions."
            }
        },
        {
            "question": "What metrics would you track to measure the success of a new messaging feature?",
            "area": "Execution / Metrics",
            "blueprint": {
                "context": "Tests your analytical skills and understanding of Acquisition, Activation, Retention, Referral, and Revenue (AARRR).",
                "what_to_say": "- Define the North Star metric (e.g., Messages sent per active user).\n- Mention secondary/guardrail metrics (e.g., App load time, spam reports).\n- Differentiate between engagement and retention.",
                "what_not_to_say": "- Just listing random metrics without tying them back to the feature's goal.",
                "example_answer": "The goal of a messaging feature is usually engagement. My North Star metric would be 'Average messages sent per active user per day'. For adoption, I'd track the percentage of DAUs who initiate a chat. I'd also set up guardrail metrics, such as monitoring for increases in blocked users or spam reports, to ensure quality doesn't degrade.",
                "behavioral": "Always include 'Guardrail Metrics' to show you think about potential negative impacts."
            }
        }
    ],
    "core_cs": [
        {
            "question": "What is a Process vs a Thread?",
            "area": "Operating Systems",
            "blueprint": {
                "context": "Fundamental OS knowledge regarding concurrency, memory isolation, and execution.",
                "what_to_say": "- A process is an executing program with its own isolated memory space.\n- A thread is a lightweight unit of execution within a process.\n- Threads share the same memory space, making communication faster but requiring synchronization (mutexes).",
                "what_not_to_say": "- Failing to mention memory isolation vs memory sharing.",
                "example_answer": "A process is a heavily isolated execution environment with its own memory space, making inter-process communication relatively slow. A thread exists within a process. Multiple threads share the same memory space and resources, which makes context switching and communication much faster, but requires careful synchronization to avoid race conditions.",
                "behavioral": "Use clear, deliberate pacing. This is a foundational definition."
            }
        },
        {
            "question": "Explain what happens when you type a URL into a browser.",
            "area": "Networking",
            "blueprint": {
                "context": "The ultimate test of full-stack networking knowledge. Spans DNS, TCP/IP, HTTP, and browser rendering.",
                "what_to_say": "- DNS Resolution (Browser cache -> OS cache -> Resolver).\n- TCP Handshake (SYN, SYN-ACK, ACK).\n- TLS Handshake (for HTTPS).\n- HTTP Request sent, Server processes and returns HTTP Response.\n- Browser parses HTML, builds DOM, fetches CSS/JS, and renders the page.",
                "what_not_to_say": "- Skipping the DNS or TCP steps and going straight to 'the server sends HTML'.",
                "example_answer": "First, the browser checks its cache for the IP address; if not found, it performs a DNS lookup. Once the IP is retrieved, the browser initiates a TCP connection via a 3-way handshake. If HTTPS, a TLS handshake establishes encryption. The browser sends an HTTP GET request. The server processes it and sends back an HTML response. The browser parses the HTML, constructs the DOM tree, fetches assets, and paints the pixels to the screen.",
                "behavioral": "Keep it high-level but structured. Offer to dive deeper into any specific step."
            }
        },
        {
            "question": "What is a Mutex?",
            "area": "Concurrency",
            "blueprint": {
                "context": "Tests understanding of thread synchronization and race conditions.",
                "what_to_say": "- Mutual Exclusion object.\n- Used to prevent multiple threads from accessing a shared resource simultaneously.\n- Contrast briefly with a Semaphore (locking vs signaling).",
                "what_not_to_say": "- Confusing a mutex with a deadlock.",
                "example_answer": "A mutex, or mutual exclusion lock, is a synchronization primitive used to prevent multiple threads from concurrently accessing a shared resource, which could cause race conditions. A thread acquires the lock before accessing the critical section and releases it afterward. If another thread tries to acquire an already held lock, it blocks until it's released.",
                "behavioral": "Use the 'bathroom key' analogy if you want to make it highly relatable."
            }
        }
    ],
    "leadership": [
        {
            "question": "How do you handle an underperforming team member?",
            "area": "People Management",
            "blueprint": {
                "context": "Tests empathy, direct communication, and performance management skills.",
                "what_to_say": "- Don't assume incompetence; look for blockers, burnout, or personal issues.\n- Have a private, empathetic 1-on-1 to identify root causes.\n- Set clear, measurable, and achievable goals together (PIP if necessary as a last resort).\n- Provide continuous feedback.",
                "what_not_to_say": "- 'I fire them immediately.'\n- 'I publicly reprimand them to set an example.'",
                "example_answer": "I approach underperformance with curiosity, not blame. I schedule a private 1-on-1 to understand if they lack resources, context, or are facing personal issues. If it's a skill gap, I provide mentorship or training. We collaborate on clear, measurable goals for the next month with weekly check-ins. My goal is always to coach them back to success.",
                "behavioral": "Show high EQ (Emotional Intelligence). Frame yourself as a coach, not a dictator."
            }
        },
        {
            "question": "Describe a time you had to make an unpopular decision.",
            "area": "Decision Making",
            "blueprint": {
                "context": "Evaluates backbone, communication, and how you align teams behind difficult calls.",
                "what_to_say": "- Explain the tough decision (e.g., cutting a beloved feature, enforcing a strict deadline).\n- Highlight HOW you communicated it: transparency, explaining the 'Why' (business value).\n- Mention listening to the team's frustrations but holding firm on the direction.",
                "what_not_to_say": "- 'I just told them to do it because I'm the boss.'",
                "example_answer": "We had to deprecate a legacy tool that a senior subset of the team loved, because maintaining it was draining engineering resources. It was highly unpopular. I called a meeting, transparently shared the data showing the maintenance cost vs business value, and explained the strategic 'why'. I acknowledged their frustration but stood firm. Eventually, the team respected the transparency and aligned.",
                "behavioral": "Demonstrate conviction balanced with empathy."
            }
        },
        {
            "question": "How do you balance technical debt with delivering new features?",
            "area": "Engineering Management",
            "blueprint": {
                "context": "The eternal struggle of engineering leadership. Tests pragmatism and business alignment.",
                "what_to_say": "- You can't ignore tech debt, but you can't stop product delivery either.\n- Advocate for the 'Boy Scout Rule' (leave code better than you found it).\n- Allocate a fixed percentage of every sprint (e.g., 20%) to tech debt and refactoring.",
                "what_not_to_say": "- 'I halt all feature work for a month to rewrite everything.'",
                "example_answer": "It requires continuous balance. I usually advocate for allocating 15-20% of every sprint's capacity explicitly to tech debt and infrastructure scaling. Additionally, I encourage the 'Boy Scout Rule' for daily PRs. If a piece of tech debt is severely impacting our deployment velocity, I quantify that cost in engineering hours to justify a larger refactoring initiative to stakeholders.",
                "behavioral": "Use percentages and frameworks to show you approach this systematically."
            }
        }
    ]
}

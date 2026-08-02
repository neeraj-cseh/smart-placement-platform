import re

new_dict = """INTERVIEW_QUESTIONS = {
    "general": [
        {
            "question": "Tell me about yourself and what motivated you to pursue a career in technology?", 
            "area": "Introduction",
            "blueprint": {
                "context": "Interviewers use this as an icebreaker to evaluate your communication skills, career trajectory, and genuine passion for the industry. They want to see a cohesive narrative connecting your past experiences to the role you are applying for.",
                "what_to_say": "1. Start with your current role/status (e.g., 'I am a recent CS graduate' or 'I am a full-stack developer').\n2. Highlight 1-2 key accomplishments or projects that showcase your core skills.\n3. Explain the 'Why'—what specifically drew you to technology (e.g., a fascination with building scalable systems, solving complex problems, or a specific project that sparked your interest).\n4. Conclude with why you are excited about *this* specific opportunity.",
                "what_not_to_say": "- Do not recount your entire life story starting from childhood.\n- Avoid reading off your resume chronologically.\n- Do not give generic reasons like 'I like computers' or 'I want to make a lot of money'.",
                "example_answer": "I’m currently a senior software engineer specializing in frontend development. My journey into tech started in college when I built a small app to help my study group share notes—seeing people use something I created hooked me instantly. Since then, I've focused on building intuitive user interfaces. Most recently, I led a project that reduced our app's load time by 40%, which significantly boosted user retention. I’m motivated by the challenge of solving complex UX problems, which is why I’m so excited about the opportunity to join your team and work on your highly interactive web platform.",
                "behavioral": "Maintain strong eye contact and speak with enthusiasm. This is your personal pitch—own your narrative with confidence."
            }
        },
        {
            "question": "Describe a project you built that you're most proud of. What was your role and what impact did it have?", 
            "area": "Project",
            "blueprint": {
                "context": "This question assesses your technical depth, your ability to take ownership, and whether you understand the broader business or user impact of your engineering work.",
                "what_to_say": "Use the STAR method:\n- **Situation**: Briefly set the context.\n- **Task**: Explain the specific problem you were trying to solve.\n- **Action**: Detail the technical decisions *you* made (architecture, stack, trade-offs).\n- **Result**: Quantify the impact (e.g., 'increased speed by 20%', 'gained 500 users').",
                "what_not_to_say": "- Don't spend too much time on the background context; get to the technical meat.\n- Avoid saying 'we built X' without clarifying what *your* specific contribution was.\n- Don't gloss over the challenges; interviewers love hearing about what went wrong and how you fixed it.",
                "example_answer": "In my last role, we were facing severe latency issues with our main reporting dashboard (Situation). I was tasked with optimizing the data retrieval process (Task). I analyzed the slow queries and realized we were doing N+1 queries. I refactored the backend to use batched database calls and implemented a Redis caching layer for frequently accessed reports (Action). As a result, the dashboard load time dropped from 8 seconds to under 1 second, and customer complaints about the dashboard completely stopped (Result).",
                "behavioral": "Lean forward slightly. Express genuine pride in your work. Be ready for follow-up technical questions on the specific technologies you mention."
            }
        },
        {
            "question": "How do you approach debugging a problem you've never seen before?", 
            "area": "Problem Solving",
            "blueprint": {
                "context": "Software engineering is mostly debugging. Interviewers want to see that you have a logical, systematic, and calm approach to unknown issues, rather than just randomly changing code.",
                "what_to_say": "1. **Reproduce**: State that you first reliably reproduce the bug.\n2. **Isolate**: Explain how you isolate variables using logs, breakpoints, or binary search (e.g., commenting out code).\n3. **Research**: Mention checking documentation, GitHub issues, or StackOverflow.\n4. **Fix & Test**: Explain that you write a test to prevent regressions before applying the fix.",
                "what_not_to_say": "- Never say 'I just try changing things until it works' or 'I immediately ask a senior developer' (show independence first).\n- Avoid blaming the language, the framework, or other developers unnecessarily.",
                "example_answer": "My first step is always to reliably reproduce the error and write a failing test case for it. Once I can reproduce it, I look at the stack trace and application logs to isolate where the failure occurs. If it's a completely new error, I'll often use a binary search approach—commenting out chunks of code to isolate the exact line. If I'm still stuck after 30 minutes of debugging and reading the official documentation, I'll write down what I've tried and reach out to a colleague for a fresh pair of eyes.",
                "behavioral": "Adopt a calm, methodical tone. Use hand gestures to indicate step-by-step processes."
            }
        },
        {
            "question": "What is your greatest strength as a developer and how has it helped you in your projects?", 
            "area": "Self Awareness",
            "blueprint": {
                "context": "This evaluates your self-awareness and how your unique skills bring value to the team. It’s an opportunity to highlight a core competency that aligns with the job description.",
                "what_to_say": "Pick a strength that is both genuine and highly relevant (e.g., 'Writing maintainable code', 'Fast learning capability', or 'Cross-team communication'). Immediately follow it up with a concrete example proving this strength.",
                "what_not_to_say": "- Avoid generic clichés like 'I am a hard worker' or 'I am a perfectionist'.\n- Do not list a strength without providing an example to back it up.\n- Avoid arrogant statements like 'I am the smartest coder in every room'.",
                "example_answer": "My greatest strength is my ability to bridge the gap between technical and non-technical stakeholders. As a developer, I not only write the code, but I actively translate complex engineering constraints into business terms. For example, during our last product launch, the marketing team wanted a feature that would have delayed our release by a month. I sat down with them, explained the technical bottleneck simply, and proposed a scaled-down V1 version. We launched on time, and they were thrilled with the compromise.",
                "behavioral": "Speak confidently but stay grounded. Ensure your example highlights collaboration or tangible results."
            }
        },
        {
            "question": "Where do you see yourself in 3 years and how does this role fit into your career plan?", 
            "area": "Career Goals",
            "blueprint": {
                "context": "Employers want to hire developers who are ambitious but also intend to stick around. They are checking if your long-term goals align with the opportunities they can provide.",
                "what_to_say": "Focus on skill mastery, taking on more responsibility, and contributing to the company's success. Mention goals like becoming a domain expert, mentoring juniors, or leading architecture design.",
                "what_not_to_say": "- Don't say you plan to leave and start your own company.\n- Don't give a title-focused answer like 'I want your job as CTO'.\n- Avoid saying 'I don't know' or 'I just want to be coding'.",
                "example_answer": "In three years, I see myself as a senior-level contributor who has mastered the company's tech stack and domain. I want to be the go-to person for complex architectural decisions and be heavily involved in mentoring junior developers. This role fits perfectly because your engineering team is tackling high-scale problems, which will push me to grow my backend architecture skills while allowing me to contribute to a product I genuinely believe in.",
                "behavioral": "Show forward-looking enthusiasm. Make it clear that your growth benefits the company."
            }
        },
    ],
    "technical": [
        {
            "question": "Explain the difference between a process and a thread in simple terms.", 
            "area": "OS Concepts",
            "blueprint": {
                "context": "This is a fundamental computer science concept. Interviewers use it to gauge your understanding of operating systems, concurrency, and memory management.",
                "what_to_say": "Define both clearly. Emphasize that a **process** is an independent execution environment with its own memory space, while a **thread** is a subset of a process that shares the parent process's memory and resources. Mention that inter-process communication (IPC) is expensive, whereas inter-thread communication is fast but risky (concurrency issues).",
                "what_not_to_say": "- Do not confuse the two or say they are basically the same thing.\n- Avoid diving into overly complex kernel scheduling details unless specifically asked.\n- Don't forget to mention the memory sharing aspect, as that's the key differentiator.",
                "example_answer": "Think of a process as a house, and a thread as a person living in that house. A process (the house) has its own isolated resources and memory. If you want to communicate with another process (another house), you have to send a letter (Inter-Process Communication), which is slow. A thread (the person) lives inside the process. Multiple threads in the same process share the same memory and resources (the living room, the kitchen). They can communicate instantly, but they have to be careful not to bump into each other, which is why we need thread synchronization like mutexes.",
                "behavioral": "Use analogies to demonstrate that you deeply understand the concept rather than just memorizing a textbook definition."
            }
        },
        {
            "question": "What is the difference between SQL and NoSQL databases? When would you choose one over the other?", 
            "area": "Database",
            "blueprint": {
                "context": "System design and database selection are critical engineering skills. This checks if you understand the CAP theorem trade-offs and data modeling principles.",
                "what_to_say": "**SQL (Relational)**: Structured data, strict schemas, ACID compliance, good for complex joins (e.g., Financial systems). \n**NoSQL (Non-relational)**: Flexible schemas, horizontally scalable, often eventually consistent, good for rapid development and massive unstructured data (e.g., Social media feeds, IoT logs).",
                "what_not_to_say": "- Avoid saying 'NoSQL is faster' or 'SQL is outdated'—neither is universally true.\n- Don't forget to mention scalability (SQL typically scales vertically; NoSQL scales horizontally).",
                "example_answer": "SQL databases are relational and use structured tables with strict schemas. They are ideal for applications requiring ACID compliance and complex queries, like a banking application where data integrity is paramount. NoSQL databases are non-relational and store data as documents, key-value pairs, or graphs. I would choose NoSQL when dealing with unstructured data, rapidly changing schemas, or when we need massive horizontal scalability, such as storing telemetry data from millions of IoT devices.",
                "behavioral": "Show pragmatic engineering judgment. Emphasize that the choice always depends on the specific use case."
            }
        },
        {
            "question": "Describe how HTTP works. What happens when you type a URL in your browser?", 
            "area": "Networking",
            "blueprint": {
                "context": "This is the classic web developer interview question. It tests your full-stack understanding of how the internet fundamentally operates, from DNS to DOM rendering.",
                "what_to_say": "Walk through the sequence:\n1. Browser checks cache, then asks DNS to resolve the domain to an IP.\n2. Browser initiates a TCP handshake (and TLS for HTTPS) with the server.\n3. Browser sends an HTTP GET request.\n4. Server processes the request and sends back an HTTP response (status code 200, HTML content).\n5. Browser parses HTML, requests additional assets (CSS/JS), and renders the DOM.",
                "what_not_to_say": "- Don't skip the DNS resolution step; it's crucial.\n- Don't forget the TCP handshake (SYN, SYN-ACK, ACK).\n- Avoid getting lost in extreme minutiae (like BGP routing) unless the role is network-specific.",
                "example_answer": "First, the browser checks its cache for the IP address. If it's not there, it queries a DNS server to resolve the URL into an IP address. Next, the browser establishes a TCP connection with the server via a three-way handshake. Since it's likely HTTPS, a TLS handshake also occurs for encryption. The browser then sends an HTTP GET request. The server processes this and returns an HTTP response containing the HTML document and a 200 OK status. Finally, the browser parses the HTML, builds the DOM, requests CSS/JS assets, and renders the page to the user.",
                "behavioral": "Structure your answer chronologically. Use your hands to map out the journey from the client to the server and back."
            }
        },
        {
            "question": "What is the difference between authentication and authorization? How does JWT work?", 
            "area": "Security",
            "blueprint": {
                "context": "Security is paramount. Mixing up AuthN and AuthZ is a massive red flag. Understanding JWTs shows you are familiar with modern stateless web architecture.",
                "what_to_say": "**Authentication** confirms *who* you are (login). **Authorization** determines *what* you can do (permissions). Explain that a JWT (JSON Web Token) is a stateless token composed of a Header, Payload, and Signature, used to verify the sender's identity without querying the database.",
                "what_not_to_say": "- Never conflate the two concepts.\n- **Crucial**: Do not say JWTs are encrypted and hide data. They are base64 *encoded*, meaning anyone can read the payload. They are only *signed* to prevent tampering.",
                "example_answer": "Authentication is proving your identity—like showing your ID card at the building entrance. Authorization is checking your permissions—like whether your ID card opens the server room door. \nA JWT is a stateless way to handle this. It consists of a header, a payload containing user claims, and a signature. Once a user authenticates, the server signs a JWT with a secret key and sends it to the client. The client sends it back on subsequent requests. The server simply verifies the signature using its secret key to ensure the token hasn't been tampered with, allowing stateless authorization.",
                "behavioral": "Speak authoritatively on security. Emphasize that sensitive data should never be placed inside a JWT payload."
            }
        },
        {
            "question": "Explain RESTful API design principles. What makes a good API?", 
            "area": "API Design",
            "blueprint": {
                "context": "If you are applying for a backend or full-stack role, you will be designing APIs. Interviewers want to see that you follow industry standards and prioritize developer experience (DX).",
                "what_to_say": "Mention the core constraints: Client-Server architecture, Statelessness, Cacheability, and a Uniform Interface. Practically, discuss using standard HTTP methods (GET, POST, PUT, PATCH, DELETE), resource-based URIs (nouns, not verbs), proper HTTP status codes, and versioning.",
                "what_not_to_say": "- Don't design endpoints with verbs (e.g., `POST /createArticle`). Use `POST /articles`.\n- Don't ignore error handling and status codes (returning 200 OK with an error message in the body is a major anti-pattern).",
                "example_answer": "A RESTful API is stateless, meaning every request must contain all info needed to process it. A good API relies on a uniform interface using resource-based URIs—for example, using `GET /users` to fetch users and `POST /users` to create one, rather than `GET /getUsers`. It must use standard HTTP verbs correctly and return semantic HTTP status codes, like 201 for Created or 404 for Not Found. Furthermore, a great API is heavily documented, versioned (like `/v1/users`), and uses consistent JSON structures for both successful responses and errors.",
                "behavioral": "Show empathy for the developers who will consume your API. Mentioning 'Developer Experience' scores extra points."
            }
        },
    ],
    "dsa": [
        {
            "question": "How would you explain time complexity to someone who has never studied computer science?", 
            "area": "Complexity",
            "blueprint": {
                "context": "This tests your fundamental understanding of Big-O notation, but more importantly, it tests your communication skills. Can you translate complex CS theory into plain English?",
                "what_to_say": "Focus on the concept of *how the time taken scales as the input grows*. Use a relatable real-world analogy. O(1) is instantaneous regardless of size. O(n) scales linearly. O(log n) halves the search space.",
                "what_not_to_say": "- Do not use mathematical jargon like 'asymptotic upper bound' or 'theta notation'.\n- Don't focus on exact seconds or hardware speed; emphasize scaling.",
                "example_answer": "Time complexity is a way to describe how much longer a task takes as the amount of work increases. Imagine you have a physical phone book. \nIf I ask you to find the first name on page 1, you open it and read it immediately. That takes the same amount of time whether the book has 10 pages or 10,000 pages. That’s constant time, or O(1).\nIf I ask you to count every single name in the book, the time it takes grows directly in proportion to the number of pages. That’s linear time, or O(n).\nBut if I ask you to find 'Smith', you open to the middle. If you see 'M', you tear the book in half, throw away the first half, and repeat. You find the name very quickly because you halve the work each step. That’s logarithmic time, or O(log n).",
                "behavioral": "Adopt a warm, patient, teaching tone. Smile and use hand gestures to illustrate your analogy."
            }
        },
        {
            "question": "When would you use a hash map over an array? Give a practical example.", 
            "area": "Data Structures",
            "blueprint": {
                "context": "Hash maps are the most frequently used data structure in technical interviews. You must demonstrate that you understand their O(1) lookup property and when to leverage it.",
                "what_to_say": "State that Arrays offer O(1) access *only if you know the index*, whereas Hash Maps offer O(1) access *based on a key*. Mention that Hash Maps are ideal for lookups, caching, and counting frequencies.",
                "what_not_to_say": "- Don't forget that Hash Maps generally do not maintain insertion order (unlike arrays).\n- Don't ignore the fact that Hash Maps consume more memory due to underlying sparse arrays and hashing overhead.",
                "example_answer": "I would use a hash map when I need ultra-fast, O(1) lookups based on a specific key, rather than sequential indices. For example, if I need to build a cache for user sessions, I would use a hash map where the Session ID is the key and the User Object is the value. If I used an array, I would have to iterate through the entire array in O(n) time to find the matching session. The trade-off is that hash maps use more memory and don't maintain order, but for caching or frequency counting, the lookup speed is absolutely worth it.",
                "behavioral": "Be concise. Always mention the time-complexity (Big-O) trade-offs when discussing data structures."
            }
        },
        {
            "question": "Describe a situation where recursion is the best approach and explain how it works.", 
            "area": "Recursion",
            "blueprint": {
                "context": "Recursion is a conceptual hurdle. Interviewers want to ensure you understand both the power of recursion (clean code for recursive data) and its dangers (stack overflow).",
                "what_to_say": "Define recursion (a function calling itself). Emphasize the absolute necessity of a **Base Case** to stop the recursion, and a **Recursive Step** to progress toward the base case. Give an example like parsing a nested file system or traversing a tree.",
                "what_not_to_say": "- Don't say recursion is 'faster' than iteration—it is almost always slower and uses more memory due to the call stack.\n- Don't provide an example where a simple `for` loop is clearly better (like printing numbers 1 to 10).",
                "example_answer": "Recursion is best used when dealing with data structures that are naturally recursive, like trees or nested JSON objects. \nFor example, if I need to write a script that deletes a folder and all its sub-folders, I don't know how deep the folders go. I would write a recursive function. \nThe function works in two parts: First, the **Base Case**, which stops the recursion—if the folder is empty, delete it and return. Second, the **Recursive Step**—if the folder contains sub-folders, the function calls itself on each sub-folder. This approach makes the code incredibly clean compared to maintaining a custom stack for an iterative approach. However, I always ensure the depth won't cause a stack overflow.",
                "behavioral": "Emphasize the 'Base Case' firmly. It shows you write safe code that doesn't cause infinite loops."
            }
        },
        {
            "question": "How do you decide between BFS and DFS for graph traversal?", 
            "area": "Graphs",
            "blueprint": {
                "context": "Graph traversal is a staple of DSA interviews. This question tests if you memorize algorithms or if you actually understand their practical applications and memory constraints.",
                "what_to_say": "**BFS (Breadth-First Search)** uses a Queue. It explores neighbors first. Use it to find the *shortest path* in unweighted graphs.\n**DFS (Depth-First Search)** uses a Stack (or recursion). It explores as far down a branch as possible. Use it for topological sorting, cycle detection, or exploring all paths.",
                "what_not_to_say": "- Don't mix up their underlying data structures (BFS = Queue, DFS = Stack).\n- Don't say BFS is strictly better; mention memory constraints (BFS can take massive memory if the tree is very wide).",
                "example_answer": "The choice depends entirely on the goal and the shape of the graph. \nI use BFS when I need to find the shortest path between two nodes in an unweighted graph, like finding the minimum degrees of separation on a social network. BFS explores level by level using a Queue, so the first time it hits the target, it's guaranteed to be the shortest path.\nI use DFS when I need to explore all possible paths, detect cycles, or when the graph is extremely wide. DFS dives deep into a branch using a Stack or recursion. If a tree is very wide but not very deep, BFS would consume too much memory storing the level, making DFS a more memory-efficient choice.",
                "behavioral": "Contrast the two methods clearly. Using the words 'Queue' for BFS and 'Stack/Recursion' for DFS shows technical mastery."
            }
        },
        {
            "question": "What is dynamic programming and when should you use it?", 
            "area": "Dynamic Programming",
            "blueprint": {
                "context": "DP is considered one of the hardest topics in DSA. Interviewers ask this to see if you can break down complex optimization problems without brute-forcing them.",
                "what_to_say": "Define it as an optimization technique. State the two requirements: **Overlapping Subproblems** (the same small problems are solved repeatedly) and **Optimal Substructure** (the optimal solution to the big problem is made of optimal solutions to small problems). Mention Memoization (Top-Down) and Tabulation (Bottom-Up).",
                "what_not_to_say": "- Don't confuse it with Divide and Conquer (Merge Sort uses Divide and Conquer because its subproblems do *not* overlap).\n- Don't make it sound like magic; explain it simply as 'remembering past results to avoid repeating work.'",
                "example_answer": "Dynamic programming is simply an optimization technique where you break a complex problem down, solve the smaller parts, and store their results so you don't have to compute them again. \nYou should use it when a problem has two properties: Overlapping Subproblems (you keep calculating the same thing) and Optimal Substructure (the global optimal solution is built from local optimal solutions). \nFor example, a naive recursive Fibonacci function calculates `fib(3)` multiple times, leading to exponential O(2^n) time. By using DP—specifically memoization—we store the result of `fib(3)` in a hash map the first time we calculate it. The next time we need it, we retrieve it in O(1) time, reducing the overall time complexity to O(n).",
                "behavioral": "Speak clearly and confidently. Breaking down the intimidating 'DP' acronym into plain English ('remembering past results') is highly impressive."
            }
        },
    ],
}
"""

with open("c:/Users/neera/OneDrive/Desktop/smart-placement-platform/core/views.py", "r", encoding="utf-8") as f:
    content = f.read()

# Find the INTERVIEW_QUESTIONS dict using regex
pattern = r"INTERVIEW_QUESTIONS\s*=\s*\{.*?\n\}\n"
match = re.search(pattern, content, flags=re.DOTALL)

if match:
    new_content = content[:match.start()] + new_dict + content[match.end():]
    with open("c:/Users/neera/OneDrive/Desktop/smart-placement-platform/core/views.py", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Successfully replaced INTERVIEW_QUESTIONS")
else:
    print("Could not find INTERVIEW_QUESTIONS dictionary.")

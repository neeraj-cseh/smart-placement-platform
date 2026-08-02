import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

TOPICS = ['Array', 'Hash Table', 'Linked List', 'Math', 'Two Pointers', 'String', 'Binary Search', 'Divide and Conquer', 'Dynamic Programming', 'Backtracking']
COMPANIES = ['Google', 'Facebook', 'Amazon', 'Apple', 'Microsoft', 'Bloomberg', 'Netflix', 'Uber', 'LinkedIn']

def generate_problem(idx, name, diff):
    slug = name.lower().replace(' ', '-')[:50].strip('-')
    topics = random.sample(TOPICS, k=random.randint(1, 3))
    companies = random.sample(COMPANIES, k=random.randint(1, 4))
    acc_rate = round(random.uniform(20.0, 85.0), 1)
    relevance = round(random.uniform(50.0, 99.9), 1)
    readiness = 1 if diff == 'Easy' else 3 if diff == 'Medium' else 5

    desc = f'''
### The Problem

You are given the required inputs to solve the **{name}** problem.
This is a classic problem frequently asked by companies like {", ".join(companies)}.

Your task is to implement an optimal solution using {" and ".join(topics)}.

---

### Examples

**Example 1:**
```text
Input: sample input
Output: sample output
Explanation: This is a placeholder explanation for {name}.
```

---

### Constraints
* $1 \le N \le 10^5$
* $-10^9 \le A[i] \le 10^9$
* Only one valid answer exists.

> [!TIP]
> Think about the constraints! A $O(n^2)$ approach will likely Time Out. Aim for $O(N)$ or $O(N \log N)$.
'''

    return {
        'slug': slug,
        'title': name,
        'difficulty': diff,
        'topics': topics,
        'companies': companies,
        'acceptance_rate': acc_rate,
        'readiness_impact': readiness,
        'relevance_score': relevance,
        'description': desc,
        'function_name': 'solve',
        'starter_code': {
            'python': 'class Solution:\n    def solve(self):\n        pass\n',
            'cpp': 'class Solution {\npublic:\n    void solve() {\n        \n    }\n};\n',
            'java': 'class Solution {\n    public void solve() {\n        \n    }\n}\n'
        },
        'test_cases': [
            {'input': 'sample', 'expected': 'sample', 'is_hidden': False}
        ]
    }

PROBLEM_LIST = [
    ("Two Sum", "Easy"), ("Add Two Numbers", "Medium"), ("Longest Substring Without Repeating Characters", "Medium"),
    ("Median of Two Sorted Arrays", "Hard"), ("Longest Palindromic Substring", "Medium"), ("Zigzag Conversion", "Medium"),
    ("Reverse Integer", "Medium"), ("String to Integer", "Medium"), ("Palindrome Number", "Easy"),
    ("Regular Expression Matching", "Hard"), ("Container With Most Water", "Medium"), ("Integer to Roman", "Medium"),
    ("Roman to Integer", "Easy"), ("Longest Common Prefix", "Easy"), ("3Sum", "Medium"), ("3Sum Closest", "Medium"),
    ("Letter Combinations of a Phone Number", "Medium"), ("4Sum", "Medium"), ("Remove Nth Node From End of List", "Medium"),
    ("Valid Parentheses", "Easy"), ("Merge Two Sorted Lists", "Easy"), ("Generate Parentheses", "Medium"),
    ("Merge k Sorted Lists", "Hard"), ("Swap Nodes in Pairs", "Medium"), ("Reverse Nodes in k-Group", "Hard"),
    ("Remove Duplicates from Sorted Array", "Easy"), ("Remove Element", "Easy"), ("Find the Index of the First Occurrence in a String", "Easy"),
    ("Divide Two Integers", "Medium"), ("Substring with Concatenation of All Words", "Hard"), ("Next Permutation", "Medium"),
    ("Longest Valid Parentheses", "Hard"), ("Search in Rotated Sorted Array", "Medium"), ("Find First and Last Position of Element in Sorted Array", "Medium"),
    ("Search Insert Position", "Easy"), ("Valid Sudoku", "Medium"), ("Sudoku Solver", "Hard"), ("Count and Say", "Medium"),
    ("Combination Sum", "Medium"), ("Combination Sum II", "Medium"), ("First Missing Positive", "Hard"),
    ("Trapping Rain Water", "Hard"), ("Multiply Strings", "Medium"), ("Wildcard Matching", "Hard"),
    ("Jump Game II", "Medium"), ("Permutations", "Medium"), ("Permutations II", "Medium"), ("Rotate Image", "Medium"),
    ("Group Anagrams", "Medium"), ("Pow(x, n)", "Medium"), ("N-Queens", "Hard"), ("N-Queens II", "Hard"),
    ("Maximum Subarray", "Medium"), ("Spiral Matrix", "Medium"), ("Jump Game", "Medium"), ("Merge Intervals", "Medium"),
    ("Insert Interval", "Medium"), ("Length of Last Word", "Easy"), ("Spiral Matrix II", "Medium"), ("Permutation Sequence", "Hard")
]

print("Deleting existing problems...")
CodingProblem.objects.all().delete()

print(f"Seeding {len(PROBLEM_LIST)} premium problems...")
for idx, (name, diff) in enumerate(PROBLEM_LIST):
    p_data = generate_problem(idx, name, diff)
    test_cases = p_data.pop('test_cases', [])
    
    problem = CodingProblem.objects.create(**p_data)
    for tc in test_cases:
        TestCase.objects.create(
            problem=problem,
            input_data=tc['input'],
            expected_output=tc['expected'],
            is_hidden=tc['is_hidden']
        )
    print(f"Created: {name}")

print("Successfully seeded 50+ problems!")

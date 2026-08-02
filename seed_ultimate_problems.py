import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

problems = [
    {
        'slug': 'two-sum',
        'title': 'Two Sum',
        'difficulty': 'Easy',
        'topics': ['Array', 'Hash Table'],
        'companies': ['Google', 'Facebook', 'Amazon', 'Apple'],
        'acceptance_rate': 53.2,
        'readiness_impact': 1,
        'relevance_score': 99.9,
        'description': '''
### The Problem

Given an array of integers `nums` and an integer `target`, return *indices of the two numbers such that they add up to `target`*.

You may assume that each input would have **exactly one solution**, and you may not use the *same* element twice.

You can return the answer in any order.

---

### Optimal Approach (Hint)
Can we achieve a time complexity better than $O(n^2)$? 
> [!TIP]
> A single pass using a **Hash Table** allows us to find the complement of the current element in $O(1)$ time, yielding an overall $O(n)$ time complexity!

---

### Examples

**Example 1:**
```text
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

**Example 2:**
```text
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

**Example 3:**
```text
Input: nums = [3,3], target = 6
Output: [0,1]
```

---

### Constraints
* $2 \le \text{nums.length} \le 10^4$
* $-10^9 \le \text{nums}[i] \le 10^9$
* $-10^9 \le \text{target} \le 10^9$
* **Only one valid answer exists.**
''',
        'function_name': 'twoSum',
        'starter_code': {
            'python': 'class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass\n',
            'cpp': 'class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};\n',
            'java': 'class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}\n'
        },
        'test_cases': [
            {'input': '2 7 11 15\n9', 'expected': '0 1', 'is_hidden': False},
            {'input': '3 2 4\n6', 'expected': '1 2', 'is_hidden': False},
            {'input': '3 3\n6', 'expected': '0 1', 'is_hidden': True},
            {'input': '-1 -2 -3 -4 -5\n-8', 'expected': '2 4', 'is_hidden': True}
        ]
    },
    {
        'slug': 'reverse-linked-list',
        'title': 'Reverse Linked List',
        'difficulty': 'Easy',
        'topics': ['Linked List', 'Recursion'],
        'companies': ['Microsoft', 'Amazon', 'Bloomberg'],
        'acceptance_rate': 78.4,
        'readiness_impact': 2,
        'relevance_score': 95.0,
        'description': '''
### The Problem

Given the `head` of a singly linked list, reverse the list, and return *the reversed list*.

---

### Visualizing the Operation

Before Reversing:
```mermaid
graph LR
    A((1)) --> B((2))
    B --> C((3))
    C --> D((4))
    D --> E((5))
    E --> F[null]
    style A fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    style B fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    style C fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    style D fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
    style E fill:#3b82f6,stroke:#1d4ed8,stroke-width:2px,color:#fff
```

After Reversing:
```mermaid
graph LR
    E((5)) --> D((4))
    D --> C((3))
    C --> B((2))
    B --> A((1))
    A --> F[null]
    style A fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    style B fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    style C fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    style D fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
    style E fill:#10b981,stroke:#047857,stroke-width:2px,color:#fff
```

> [!NOTE]
> A linked list can be reversed either iteratively or recursively. Could you implement both?

---

### Examples

**Example 1:**
```text
Input: head = [1,2,3,4,5]
Output: [5,4,3,2,1]
```

**Example 2:**
```text
Input: head = [1,2]
Output: [2,1]
```

**Example 3:**
```text
Input: head = []
Output: []
```

---

### Constraints
* The number of nodes in the list is the range `[0, 5000]`.
* `-5000 <= Node.val <= 5000`
''',
        'function_name': 'reverseList',
        'starter_code': {
            'python': '# Definition for singly-linked list.\n# class ListNode:\n#     def __init__(self, val=0, next=None):\n#         self.val = val\n#         self.next = next\nclass Solution:\n    def reverseList(self, head: Optional[ListNode]) -> Optional[ListNode]:\n        pass\n',
            'cpp': '/**\n * Definition for singly-linked list.\n * struct ListNode {\n *     int val;\n *     ListNode *next;\n *     ListNode() : val(0), next(nullptr) {}\n *     ListNode(int x) : val(x), next(nullptr) {}\n *     ListNode(int x, ListNode *next) : val(x), next(next) {}\n * };\n */\nclass Solution {\npublic:\n    ListNode* reverseList(ListNode* head) {\n        \n    }\n};\n',
            'java': '/**\n * Definition for singly-linked list.\n * public class ListNode {\n *     int val;\n *     ListNode next;\n *     ListNode() {}\n *     ListNode(int val) { this.val = val; }\n *     ListNode(int val, ListNode next) { this.val = val; this.next = next; }\n * }\n */\nclass Solution {\n    public ListNode reverseList(ListNode head) {\n        \n    }\n}\n'
        },
        'test_cases': [
            {'input': '1 2 3 4 5', 'expected': '5 4 3 2 1', 'is_hidden': False},
            {'input': '1 2', 'expected': '2 1', 'is_hidden': False},
            {'input': '', 'expected': '', 'is_hidden': False},
            {'input': '-1 -2 -3', 'expected': '-3 -2 -1', 'is_hidden': True}
        ]
    },
    {
        'slug': 'valid-parentheses',
        'title': 'Valid Parentheses',
        'difficulty': 'Easy',
        'topics': ['String', 'Stack'],
        'companies': ['Google', 'Facebook', 'Bloomberg'],
        'acceptance_rate': 40.2,
        'readiness_impact': 1,
        'relevance_score': 98.5,
        'description': '''
### The Problem

Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

---

### Examples

**Example 1:**
```text
Input: s = "()"
Output: true
```

**Example 2:**
```text
Input: s = "()[]{}"
Output: true
```

**Example 3:**
```text
Input: s = "(]"
Output: false
```

> [!TIP]
> Think about using a **Stack**. As you encounter an opening bracket, push it to the stack. When you encounter a closing bracket, check if the top of the stack is the matching opening bracket!

---

### Constraints
* `1 <= s.length <= 10^4`
* `s` consists of parentheses only `'()[]{}'`.
''',
        'function_name': 'isValid',
        'starter_code': {
            'python': 'class Solution:\n    def isValid(self, s: str) -> bool:\n        pass\n',
            'cpp': 'class Solution {\npublic:\n    bool isValid(string s) {\n        \n    }\n};\n',
            'java': 'class Solution {\n    public boolean isValid(String s) {\n        \n    }\n}\n'
        },
        'test_cases': [
            {'input': '()', 'expected': 'true', 'is_hidden': False},
            {'input': '()[]{}', 'expected': 'true', 'is_hidden': False},
            {'input': '(]', 'expected': 'false', 'is_hidden': False},
            {'input': '([)]', 'expected': 'false', 'is_hidden': True},
            {'input': '{[]}', 'expected': 'true', 'is_hidden': True}
        ]
    },
    {
        'slug': 'trapping-rain-water',
        'title': 'Trapping Rain Water',
        'difficulty': 'Hard',
        'topics': ['Arrays', 'Two Pointers', 'Stack', 'DP'],
        'companies': ['Amazon', 'Bloomberg', 'Google', 'Meta'],
        'acceptance_rate': 60.1,
        'readiness_impact': 5,
        'relevance_score': 92.5,
        'function_name': 'trap',
        'description': '''
### The Problem

Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.

---

### Visualizing the Elevation Map

```mermaid
xychart-beta
    title "Elevation Map"
    x-axis [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    y-axis "Height" 0 --> 4
    bar [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]
```

*Water gets trapped between the bars where there are boundaries higher on both sides!*

---

### Examples

**Example 1:**
```text
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The elevation map is represented by the array. 6 units of rain water are trapped.
```

**Example 2:**
```text
Input: height = [4,2,0,3,2,5]
Output: 9
```

> [!TIP]
> Think about calculating the max height to the left and right of every bar. The trapped water above a bar is `min(max_left, max_right) - height`.

---

### Constraints
* `n == height.length`
* `1 <= n <= 2 * 10^4`
* `0 <= height[i] <= 10^5`
''',
        'starter_code': {
            'python': 'class Solution:\n    def trap(self, height: List[int]) -> int:\n        pass\n',
            'cpp': 'class Solution {\npublic:\n    int trap(vector<int>& height) {\n        \n    }\n};\n',
            'java': 'class Solution {\n    public int trap(int[] height) {\n        \n    }\n}\n'
        },
        'test_cases': [
            {'input': '0 1 0 2 1 0 1 3 2 1 2 1', 'expected': '6', 'is_hidden': False}, 
            {'input': '4 2 0 3 2 5', 'expected': '9', 'is_hidden': False},
            {'input': '1 0 1', 'expected': '1', 'is_hidden': True}
        ]
    }
]

print("Deleting existing problems to apply the Limitless Premium Overhaul...")
CodingProblem.objects.all().delete()

for p_data in problems:
    test_cases = p_data.pop('test_cases', [])
    problem = CodingProblem.objects.create(**p_data)
    for tc in test_cases:
        TestCase.objects.create(
            problem=problem,
            input_data=tc['input'],
            expected_output=tc['expected'],
            is_hidden=tc['is_hidden']
        )
    print(f'Created premium problem: {problem.title}')
print("Database seed complete.")

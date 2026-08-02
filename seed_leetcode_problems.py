import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

PROBLEMS = [
    {
        "title": "Two Sum",
        "difficulty": "Easy",
        "topics": ["Array", "Hash Table"],
        "companies": ["Amazon", "Google", "Apple", "Adobe", "Microsoft"],
        "acceptance_rate": 51.4,
        "description": """
Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.

You may assume that each input would have ***exactly* one solution**, and you may not use the same element twice.

You can return the answer in any order.

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

### Constraints

* $2 \le \text{nums.length} \le 10^4$
* $-10^9 \le \text{nums}[i] \le 10^9$
* $-10^9 \le \text{target} \le 10^9$
* **Only one valid answer exists.**
""",
        "starter_code": {
            "python": "class Solution:\n    def solve(self, nums: list[int], target: int) -> list[int]:\n        pass\n",
            "javascript": "var twoSum = function(nums, target) {\n    \n};\n",
            "java": "class Solution {\n    public int[] solve(int[] nums, int target) {\n        \n    }\n}\n",
            "cpp": "class Solution {\npublic:\n    vector<int> solve(vector<int>& nums, int target) {\n        \n    }\n};\n"
        },
        "test_cases": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1], "is_hidden": False},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2], "is_hidden": False},
            {"input": {"nums": [3, 3], "target": 6}, "expected": [0, 1], "is_hidden": False},
            {"input": {"nums": [2, 5, 5, 11], "target": 10}, "expected": [1, 2], "is_hidden": True}
        ]
    },
    {
        "title": "Valid Parentheses",
        "difficulty": "Easy",
        "topics": ["String", "Stack"],
        "companies": ["Amazon", "LinkedIn", "Microsoft", "Facebook"],
        "acceptance_rate": 40.5,
        "description": """
Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

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

### Constraints

* $1 \le s.\text{length} \le 10^4$
* `s` consists of parentheses only `'()[]{}'`.
""",
        "starter_code": {
            "python": "class Solution:\n    def solve(self, s: str) -> bool:\n        pass\n",
            "javascript": "var isValid = function(s) {\n    \n};\n"
        },
        "test_cases": [
            {"input": {"s": "()"}, "expected": True, "is_hidden": False},
            {"input": {"s": "()[]{}"}, "expected": True, "is_hidden": False},
            {"input": {"s": "(]"}, "expected": False, "is_hidden": False},
            {"input": {"s": "([)]"}, "expected": False, "is_hidden": True},
            {"input": {"s": "{[]}"}, "expected": True, "is_hidden": True}
        ]
    },
    {
        "title": "Merge Intervals",
        "difficulty": "Medium",
        "topics": ["Array", "Sorting"],
        "companies": ["JPMorgan", "Amazon", "Bloomberg", "Google"],
        "acceptance_rate": 46.8,
        "description": """
Given an array of `intervals` where $\text{intervals}[i] = [\text{start}_i, \text{end}_i]$, merge all overlapping intervals, and return *an array of the non-overlapping intervals that cover all the intervals in the input*.

### Examples

**Example 1:**
```text
Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
Output: [[1,6],[8,10],[15,18]]
Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].
```

**Example 2:**
```text
Input: intervals = [[1,4],[4,5]]
Output: [[1,5]]
Explanation: Intervals [1,4] and [4,5] are considered overlapping.
```

### Constraints

* $1 \le \text{intervals.length} \le 10^4$
* $\text{intervals}[i].\text{length} == 2$
* $0 \le \text{start}_i \le \text{end}_i \le 10^4$
""",
        "starter_code": {
            "python": "class Solution:\n    def solve(self, intervals: list[list[int]]) -> list[list[int]]:\n        pass\n"
        },
        "test_cases": [
            {"input": {"intervals": [[1,3],[2,6],[8,10],[15,18]]}, "expected": [[1,6],[8,10],[15,18]], "is_hidden": False},
            {"input": {"intervals": [[1,4],[4,5]]}, "expected": [[1,5]], "is_hidden": False},
            {"input": {"intervals": [[1,4],[2,3]]}, "expected": [[1,4]], "is_hidden": True}
        ]
    },
    {
        "title": "Trapping Rain Water",
        "difficulty": "Hard",
        "topics": ["Array", "Two Pointers", "Dynamic Programming", "Stack"],
        "companies": ["Amazon", "Goldman Sachs", "Google", "Microsoft"],
        "acceptance_rate": 59.9,
        "description": """
Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.

### Examples

**Example 1:**
```text
Input: height = [0,1,0,2,1,0,1,3,2,1,2,1]
Output: 6
Explanation: The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water are being trapped.
```

**Example 2:**
```text
Input: height = [4,2,0,3,2,5]
Output: 9
```

### Constraints

* $n == \text{height.length}$
* $1 \le n \le 2 \times 10^4$
* $0 \le \text{height}[i] \le 10^5$
""",
        "starter_code": {
            "python": "class Solution:\n    def solve(self, height: list[int]) -> int:\n        pass\n"
        },
        "test_cases": [
            {"input": {"height": [0,1,0,2,1,0,1,3,2,1,2,1]}, "expected": 6, "is_hidden": False},
            {"input": {"height": [4,2,0,3,2,5]}, "expected": 9, "is_hidden": False},
            {"input": {"height": [4,2,3]}, "expected": 1, "is_hidden": True}
        ]
    }
]

def run_seed():
    print("Clearing existing problems...")
    CodingProblem.objects.all().delete()
    
    for p_data in PROBLEMS:
        print(f"Creating {p_data['title']}...")
        slug = p_data['title'].lower().replace(' ', '-')[:50].strip('-')
        
        test_cases = p_data.pop('test_cases', [])
        
        problem = CodingProblem.objects.create(
            title=p_data['title'],
            slug=slug,
            difficulty=p_data['difficulty'],
            topics=p_data['topics'],
            companies=p_data['companies'],
            acceptance_rate=p_data['acceptance_rate'],
            description=p_data['description'],
            starter_code=p_data['starter_code'],
            relevance_score=85 + len(p_data['companies']) * 2,
            readiness_impact=5 if p_data['difficulty'] == 'Hard' else 3,
        )
        
        for idx, tc in enumerate(test_cases):
            TestCase.objects.create(
                problem=problem,
                input_data=tc['input'],
                expected_output=tc['expected'],
                is_hidden=tc['is_hidden'],
                order=idx
            )
            
    print("Successfully seeded LeetCode problems with exact constraints and content.")

if __name__ == "__main__":
    run_seed()

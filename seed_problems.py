import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

def seed_real_problems():
    print("Clearing old problems...")
    CodingProblem.objects.all().delete()
    
    problems = [
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "difficulty": "Easy",
            "topics": ["Arrays", "Hashing"],
            "companies": ["Amazon", "Google", "Apple"],
            "acceptance_rate": 52.4,
            "readiness_impact": 2,
            "description": "Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to `target`.\n\nYou may assume that each input would have exactly one solution, and you may not use the same element twice.\n\nYou can return the answer in any order.",
            "constraints": [
                "2 <= nums.length <= 10^4",
                "-10^9 <= nums[i] <= 10^9",
                "-10^9 <= target <= 10^9",
                "Only one valid answer exists."
            ],
            "examples": [
                {
                    "input": "nums = [2,7,11,15], target = 9",
                    "output": "[0,1]",
                    "explanation": "Because nums[0] + nums[1] == 9, we return [0, 1]."
                },
                {
                    "input": "nums = [3,2,4], target = 6",
                    "output": "[1,2]"
                }
            ],
            "hints": ["A really brute force way would be to search for all possible pairs of numbers but that would be too slow. Again, it's best to try out brute force solutions for just for completeness. It is from these brute force solutions that you can come up with optimizations.", "So, if we fix one of the numbers, say x, we have to scan the entire array to find the next number y which is value - x where value is the input parameter. Can we change our array keeping so that this search becomes faster?", "The second train of thought is, without changing the array, can we use additional space somehow? Like maybe a hash map to speed up the search?"],
            "starter_code": {
                "python": "class Solution:\n    def twoSum(self, nums: List[int], target: int) -> List[int]:\n        pass\n",
                "javascript": "/**\n * @param {number[]} nums\n * @param {number} target\n * @return {number[]}\n */\nvar twoSum = function(nums, target) {\n    \n};\n",
                "java": "class Solution {\n    public int[] twoSum(int[] nums, int target) {\n        \n    }\n}\n",
                "cpp": "class Solution {\npublic:\n    vector<int> twoSum(vector<int>& nums, int target) {\n        \n    }\n};\n"
            },
            "test_cases": [
                {"input": "[2,7,11,15]\n9", "expected": "[0,1]", "is_hidden": False},
                {"input": "[3,2,4]\n6", "expected": "[1,2]", "is_hidden": False},
                {"input": "[3,3]\n6", "expected": "[0,1]", "is_hidden": True}
            ]
        },
        {
            "slug": "merge-intervals",
            "title": "Merge Intervals",
            "difficulty": "Medium",
            "topics": ["Arrays", "Sorting"],
            "companies": ["Bloomberg", "Facebook", "Microsoft"],
            "acceptance_rate": 46.8,
            "readiness_impact": 4,
            "description": "Given an array of `intervals` where `intervals[i] = [starti, endi]`, merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.",
            "constraints": [
                "1 <= intervals.length <= 10^4",
                "intervals[i].length == 2",
                "0 <= starti <= endi <= 10^4"
            ],
            "examples": [
                {
                    "input": "intervals = [[1,3],[2,6],[8,10],[15,18]]",
                    "output": "[[1,6],[8,10],[15,18]]",
                    "explanation": "Since intervals [1,3] and [2,6] overlap, merge them into [1,6]."
                }
            ],
            "hints": ["Sort the intervals by their start time."],
            "starter_code": {
                "python": "class Solution:\n    def merge(self, intervals: List[List[int]]) -> List[List[int]]:\n        pass\n",
                "javascript": "/**\n * @param {number[][]} intervals\n * @return {number[][]}\n */\nvar merge = function(intervals) {\n    \n};\n",
                "java": "class Solution {\n    public int[][] merge(int[][] intervals) {\n        \n    }\n}\n",
                "cpp": "class Solution {\npublic:\n    vector<vector<int>> merge(vector<vector<int>>& intervals) {\n        \n    }\n};\n"
            },
            "test_cases": [
                {"input": "[[1,3],[2,6],[8,10],[15,18]]", "expected": "[[1,6],[8,10],[15,18]]", "is_hidden": False},
                {"input": "[[1,4],[4,5]]", "expected": "[[1,5]]", "is_hidden": False}
            ]
        },
        {
            "slug": "lru-cache",
            "title": "LRU Cache",
            "difficulty": "Hard",
            "topics": ["Hash Table", "Linked List", "Design"],
            "companies": ["Amazon", "Google", "Microsoft"],
            "acceptance_rate": 42.1,
            "readiness_impact": 5,
            "description": "Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.\n\nImplement the `LRUCache` class:\n* `LRUCache(int capacity)` Initialize the LRU cache with positive size capacity.\n* `int get(int key)` Return the value of the key if the key exists, otherwise return `-1`.\n* `void put(int key, int value)` Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this operation, evict the least recently used key.\n\nThe functions `get` and `put` must each run in O(1) average time complexity.",
            "constraints": [
                "1 <= capacity <= 3000",
                "0 <= key <= 10^4",
                "0 <= value <= 10^5",
                "At most 2 * 10^5 calls will be made to get and put."
            ],
            "examples": [
                {
                    "input": '["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]\n[[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]',
                    "output": "[null, null, null, 1, null, -1, null, -1, 3, 4]"
                }
            ],
            "hints": ["Use a HashMap to store the key-value pairs.", "Use a Doubly Linked List to maintain the order of keys based on their usage."],
            "starter_code": {
                "python": "class LRUCache:\n    def __init__(self, capacity: int):\n        pass\n\n    def get(self, key: int) -> int:\n        pass\n\n    def put(self, key: int, value: int) -> None:\n        pass\n",
                "javascript": "/**\n * @param {number} capacity\n */\nvar LRUCache = function(capacity) {\n    \n};\n\n/** \n * @param {number} key\n * @return {number}\n */\nLRUCache.prototype.get = function(key) {\n    \n};\n\n/** \n * @param {number} key \n * @param {number} value\n * @return {void}\n */\nLRUCache.prototype.put = function(key, value) {\n    \n};\n",
                "java": "class LRUCache {\n    public LRUCache(int capacity) {\n        \n    }\n    \n    public int get(int key) {\n        \n    }\n    \n    public void put(int key, int value) {\n        \n    }\n}\n",
                "cpp": "class LRUCache {\npublic:\n    LRUCache(int capacity) {\n        \n    }\n    \n    int get(int key) {\n        \n    }\n    \n    void put(int key, int value) {\n        \n    }\n};\n"
            },
            "test_cases": [
                {"input": "capacity=2\nput(1,1)\nput(2,2)\nget(1)", "expected": "1", "is_hidden": False}
            ]
        }
    ]
    
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
        print(f"Created problem: {problem.title}")
        
    print("Seeding complete.")

if __name__ == '__main__':
    seed_real_problems()

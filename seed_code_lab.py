import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase, CodingContest
from django.utils import timezone
from datetime import timedelta

def seed_code_lab():
    print("Clearing old problems and contests...")
    CodingProblem.objects.all().delete()
    CodingContest.objects.all().delete()
    
    problems = [
        {
            "slug": "two-sum",
            "title": "Two Sum",
            "difficulty": "Easy",
            "topics": ["Arrays", "Hashing"],
            "companies": ["Amazon", "Google", "Apple"],
            "acceptance_rate": 52.4,
            "readiness_impact": 2,
            "function_name": "twoSum",
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
            "hints": ["Use a hash map to speed up the search."],
            "starter_code": {
                "python": "class Solution:\n    def twoSum(self, nums, target):\n        pass\n",
                "javascript": "var twoSum = function(nums, target) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [[2,7,11,15], 9], "expected": [0,1], "is_hidden": False},
                {"input": [[3,2,4], 6], "expected": [1,2], "is_hidden": False},
                {"input": [[3,3], 6], "expected": [0,1], "is_hidden": True}
            ]
        },
        {
            "slug": "best-time-to-buy-and-sell-stock",
            "title": "Best Time to Buy and Sell Stock",
            "difficulty": "Easy",
            "topics": ["Arrays", "DP"],
            "companies": ["Amazon", "Facebook", "Microsoft"],
            "acceptance_rate": 54.1,
            "readiness_impact": 3,
            "function_name": "maxProfit",
            "description": "You are given an array `prices` where `prices[i]` is the price of a given stock on the `i`th day.\n\nYou want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.\n\nReturn the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.",
            "constraints": [
                "1 <= prices.length <= 10^5",
                "0 <= prices[i] <= 10^4"
            ],
            "examples": [
                {
                    "input": "prices = [7,1,5,3,6,4]",
                    "output": "5",
                    "explanation": "Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5."
                }
            ],
            "hints": ["Keep track of the minimum price seen so far."],
            "starter_code": {
                "python": "class Solution:\n    def maxProfit(self, prices):\n        pass\n",
                "javascript": "var maxProfit = function(prices) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [[7,1,5,3,6,4]], "expected": 5, "is_hidden": False},
                {"input": [[7,6,4,3,1]], "expected": 0, "is_hidden": False},
                {"input": [[1,2,4,2,5,7,2,4,9,0,9]], "expected": 9, "is_hidden": True}
            ]
        },
        {
            "slug": "contains-duplicate",
            "title": "Contains Duplicate",
            "difficulty": "Easy",
            "topics": ["Arrays", "Hashing"],
            "companies": ["Apple", "Amazon", "Microsoft"],
            "acceptance_rate": 61.2,
            "readiness_impact": 1,
            "function_name": "containsDuplicate",
            "description": "Given an integer array `nums`, return `true` if any value appears at least twice in the array, and return `false` if every element is distinct.",
            "constraints": [
                "1 <= nums.length <= 10^5",
                "-10^9 <= nums[i] <= 10^9"
            ],
            "examples": [
                {
                    "input": "nums = [1,2,3,1]",
                    "output": "true"
                },
                {
                    "input": "nums = [1,2,3,4]",
                    "output": "false"
                }
            ],
            "hints": ["Use a set to keep track of seen elements."],
            "starter_code": {
                "python": "class Solution:\n    def containsDuplicate(self, nums):\n        pass\n",
                "javascript": "var containsDuplicate = function(nums) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [[1,2,3,1]], "expected": True, "is_hidden": False},
                {"input": [[1,2,3,4]], "expected": False, "is_hidden": False},
                {"input": [[1,1,1,3,3,4,3,2,4,2]], "expected": True, "is_hidden": True}
            ]
        },
        {
            "slug": "valid-anagram",
            "title": "Valid Anagram",
            "difficulty": "Easy",
            "topics": ["Hashing", "String"],
            "companies": ["Uber", "Google", "Amazon"],
            "acceptance_rate": 63.4,
            "readiness_impact": 2,
            "function_name": "isAnagram",
            "description": "Given two strings `s` and `t`, return `true` if `t` is an anagram of `s`, and `false` otherwise.",
            "constraints": [
                "1 <= s.length, t.length <= 5 * 10^4",
                "s and t consist of lowercase English letters."
            ],
            "examples": [
                {
                    "input": "s = \"anagram\", t = \"nagaram\"",
                    "output": "true"
                }
            ],
            "hints": ["Count the frequency of each character."],
            "starter_code": {
                "python": "class Solution:\n    def isAnagram(self, s, t):\n        pass\n",
                "javascript": "var isAnagram = function(s, t) {\n    \n};\n"
            },
            "test_cases": [
                {"input": ["anagram", "nagaram"], "expected": True, "is_hidden": False},
                {"input": ["rat", "car"], "expected": False, "is_hidden": False},
                {"input": ["aacc", "ccac"], "expected": False, "is_hidden": True}
            ]
        },
        {
            "slug": "group-anagrams",
            "title": "Group Anagrams",
            "difficulty": "Medium",
            "topics": ["Arrays", "Hashing", "String"],
            "companies": ["Amazon", "Microsoft", "Goldman Sachs"],
            "acceptance_rate": 67.8,
            "readiness_impact": 4,
            "function_name": "groupAnagrams",
            "description": "Given an array of strings `strs`, group the anagrams together. You can return the answer in any order.",
            "constraints": [
                "1 <= strs.length <= 10^4",
                "0 <= strs[i].length <= 100",
                "strs[i] consists of lowercase English letters."
            ],
            "examples": [
                {
                    "input": "strs = [\"eat\",\"tea\",\"tan\",\"ate\",\"nat\",\"bat\"]",
                    "output": "[[\"bat\"],[\"nat\",\"tan\"],[\"ate\",\"eat\",\"tea\"]]"
                }
            ],
            "hints": ["Use a hash map where the key is the sorted string."],
            "starter_code": {
                "python": "class Solution:\n    def groupAnagrams(self, strs):\n        pass\n",
                "javascript": "var groupAnagrams = function(strs) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [["eat","tea","tan","ate","nat","bat"]], "expected": [["bat"],["nat","tan"],["ate","eat","tea"]], "is_hidden": False}
                # Since output order doesn't matter, testing this rigorously requires custom judge logic. For now we assume sorted order.
            ]
        },
        {
            "slug": "valid-parentheses",
            "title": "Valid Parentheses",
            "difficulty": "Easy",
            "topics": ["Stack", "String"],
            "companies": ["Amazon", "LinkedIn", "Facebook"],
            "acceptance_rate": 40.4,
            "readiness_impact": 3,
            "function_name": "isValid",
            "description": "Given a string `s` containing just the characters `'('`, `')'`, `'{'`, `'}'`, `'['` and `']'`, determine if the input string is valid.\n\nAn input string is valid if:\n1. Open brackets must be closed by the same type of brackets.\n2. Open brackets must be closed in the correct order.\n3. Every close bracket has a corresponding open bracket of the same type.",
            "constraints": [
                "1 <= s.length <= 10^4",
                "s consists of parentheses only '()[]{}'."
            ],
            "examples": [
                {"input": "s = \"()\"", "output": "true"},
                {"input": "s = \"()[]{}\"", "output": "true"},
                {"input": "s = \"(]\"", "output": "false"}
            ],
            "hints": ["Use a stack to push open parentheses and pop when matching closing parentheses are found."],
            "starter_code": {
                "python": "class Solution:\n    def isValid(self, s):\n        pass\n",
                "javascript": "var isValid = function(s) {\n    \n};\n"
            },
            "test_cases": [
                {"input": ["()"], "expected": True, "is_hidden": False},
                {"input": ["()[]{}"], "expected": True, "is_hidden": False},
                {"input": ["(]"], "expected": False, "is_hidden": False},
                {"input": ["([)]"], "expected": False, "is_hidden": True},
                {"input": ["{[]}"], "expected": True, "is_hidden": True}
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
            "function_name": "merge",
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
                "python": "class Solution:\n    def merge(self, intervals):\n        pass\n",
                "javascript": "var merge = function(intervals) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [[[1,3],[2,6],[8,10],[15,18]]], "expected": [[1,6],[8,10],[15,18]], "is_hidden": False},
                {"input": [[[1,4],[4,5]]], "expected": [[1,5]], "is_hidden": False},
                {"input": [[[1,4],[2,3]]], "expected": [[1,4]], "is_hidden": True}
            ]
        },
        {
            "slug": "climbing-stairs",
            "title": "Climbing Stairs",
            "difficulty": "Easy",
            "topics": ["DP", "Math"],
            "companies": ["Amazon", "Google", "Apple"],
            "acceptance_rate": 52.8,
            "readiness_impact": 2,
            "function_name": "climbStairs",
            "description": "You are climbing a staircase. It takes `n` steps to reach the top.\n\nEach time you can either climb 1 or 2 steps. In how many distinct ways can you climb to the top?",
            "constraints": [
                "1 <= n <= 45"
            ],
            "examples": [
                {
                    "input": "n = 2",
                    "output": "2",
                    "explanation": "1. 1 step + 1 step\n2. 2 steps"
                },
                {
                    "input": "n = 3",
                    "output": "3",
                    "explanation": "1. 1 step + 1 step + 1 step\n2. 1 step + 2 steps\n3. 2 steps + 1 step"
                }
            ],
            "hints": ["This is essentially the Fibonacci sequence."],
            "starter_code": {
                "python": "class Solution:\n    def climbStairs(self, n):\n        pass\n",
                "javascript": "var climbStairs = function(n) {\n    \n};\n"
            },
            "test_cases": [
                {"input": [2], "expected": 2, "is_hidden": False},
                {"input": [3], "expected": 3, "is_hidden": False},
                {"input": [4], "expected": 5, "is_hidden": True},
                {"input": [5], "expected": 8, "is_hidden": True}
            ]
        },
        {
            "slug": "longest-substring-without-repeating-characters",
            "title": "Longest Substring Without Repeating Characters",
            "difficulty": "Medium",
            "topics": ["Hash Table", "String", "Sliding Window"],
            "companies": ["Amazon", "Bloomberg", "Spotify"],
            "acceptance_rate": 34.2,
            "readiness_impact": 4,
            "function_name": "lengthOfLongestSubstring",
            "description": "Given a string `s`, find the length of the **longest substring** without repeating characters.",
            "constraints": [
                "0 <= s.length <= 5 * 10^4",
                "s consists of English letters, digits, symbols and spaces."
            ],
            "examples": [
                {
                    "input": "s = \"abcabcbb\"",
                    "output": "3",
                    "explanation": "The answer is \"abc\", with the length of 3."
                },
                {
                    "input": "s = \"bbbbb\"",
                    "output": "1",
                    "explanation": "The answer is \"b\", with the length of 1."
                }
            ],
            "hints": ["Use a sliding window and a set/map to track characters."],
            "starter_code": {
                "python": "class Solution:\n    def lengthOfLongestSubstring(self, s):\n        pass\n",
                "javascript": "var lengthOfLongestSubstring = function(s) {\n    \n};\n"
            },
            "test_cases": [
                {"input": ["abcabcbb"], "expected": 3, "is_hidden": False},
                {"input": ["bbbbb"], "expected": 1, "is_hidden": False},
                {"input": ["pwwkew"], "expected": 3, "is_hidden": False},
                {"input": ["dvdf"], "expected": 3, "is_hidden": True}
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
        
    print(f"Seeded {len(problems)} problems.")
    
    now = timezone.now()
    contests = [
        {
            "title": "Weekly Contest 389",
            "description": "Compete against thousands of developers.",
            "start_time": now + timedelta(days=2),
            "end_time": now + timedelta(days=2, hours=1, minutes=30),
        },
        {
            "title": "Biweekly Contest 126",
            "description": "Compete against thousands of developers.",
            "start_time": now + timedelta(days=5),
            "end_time": now + timedelta(days=5, hours=1, minutes=30),
        },
        {
            "title": "Weekly Contest 388",
            "description": "Past contest.",
            "start_time": now - timedelta(days=5),
            "end_time": now - timedelta(days=5, hours=-1, minutes=-30),
        }
    ]
    for c in contests:
        CodingContest.objects.create(**c)
    print(f"Seeded {len(contests)} contests.")
        
    print("Seeding complete.")

if __name__ == '__main__':
    seed_code_lab()

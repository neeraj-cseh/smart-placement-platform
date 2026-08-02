import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

problems = [
    {
        'slug': 'reverse-linked-list',
        'title': 'Reverse Linked List',
        'difficulty': 'Easy',
        'topics': ['Linked Lists', 'Recursion'],
        'companies': ['Apple', 'Microsoft'],
        'acceptance_rate': 74.8,
        'readiness_impact': 5,
        'function_name': 'reverseList',
        'description': 'Given the `head` of a singly linked list, reverse the list, and return the reversed list.',
        'constraints': ['The number of nodes in the list is the range [0, 5000].', '-5000 <= Node.val <= 5000'],
        'examples': [{'input': 'head = [1,2,3,4,5]', 'output': '[5,4,3,2,1]'}],
        'hints': ['Can you do it iteratively and recursively?'],
        'starter_code': {'python': 'class Solution:\n    def reverseList(self, head):\n        pass\n'},
        'test_cases': [{'input': [[1,2,3,4,5]], 'expected': [5,4,3,2,1], 'is_hidden': False}]
    },
    {
        'slug': 'invert-binary-tree',
        'title': 'Invert Binary Tree',
        'difficulty': 'Easy',
        'topics': ['Trees', 'Binary Tree'],
        'companies': ['Google', 'Meta'],
        'acceptance_rate': 76.5,
        'readiness_impact': 4,
        'function_name': 'invertTree',
        'description': 'Given the `root` of a binary tree, invert the tree, and return its root.',
        'constraints': ['The number of nodes in the tree is in the range [0, 100].', '-100 <= Node.val <= 100'],
        'examples': [{'input': 'root = [4,2,7,1,3,6,9]', 'output': '[4,7,2,9,6,3,1]'}],
        'hints': ['Think about swapping the left and right children for every node.'],
        'starter_code': {'python': 'class Solution:\n    def invertTree(self, root):\n        pass\n'},
        'test_cases': [{'input': [[4,2,7,1,3,6,9]], 'expected': [4,7,2,9,6,3,1], 'is_hidden': False}]
    },
    {
        'slug': 'number-of-islands',
        'title': 'Number of Islands',
        'difficulty': 'Medium',
        'topics': ['Graphs', 'Matrix', 'DFS', 'BFS'],
        'companies': ['Amazon', 'Bloomberg'],
        'acceptance_rate': 58.3,
        'readiness_impact': 5,
        'function_name': 'numIslands',
        'description': 'Given an `m x n` 2D binary grid `grid` which represents a map of `1`s (land) and `0`s (water), return the number of islands.\n\nAn island is surrounded by water and is formed by connecting adjacent lands horizontally or vertically.',
        'constraints': ['m == grid.length', 'n == grid[i].length', '1 <= m, n <= 300', 'grid[i][j] is 0 or 1.'],
        'examples': [{'input': 'grid = [["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]', 'output': '3'}],
        'hints': ['Use DFS or BFS to traverse all connected 1s.'],
        'starter_code': {'python': 'class Solution:\n    def numIslands(self, grid):\n        pass\n'},
        'test_cases': [{'input': [[["1","1","0","0","0"],["1","1","0","0","0"],["0","0","1","0","0"],["0","0","0","1","1"]]], 'expected': 3, 'is_hidden': False}]
    },
    {
        'slug': 'jump-game',
        'title': 'Jump Game',
        'difficulty': 'Medium',
        'topics': ['Greedy', 'DP', 'Arrays'],
        'companies': ['Microsoft', 'Amazon'],
        'acceptance_rate': 38.6,
        'readiness_impact': 3,
        'function_name': 'canJump',
        'description': 'You are given an integer array `nums`. You are initially positioned at the arrays first index, and each element in the array represents your maximum jump length at that position.\n\nReturn `true` if you can reach the last index, or `false` otherwise.',
        'constraints': ['1 <= nums.length <= 10^4', '0 <= nums[i] <= 10^5'],
        'examples': [{'input': 'nums = [2,3,1,1,4]', 'output': 'true'}],
        'hints': ['Keep track of the maximum reachable index.'],
        'starter_code': {'python': 'class Solution:\n    def canJump(self, nums):\n        pass\n'},
        'test_cases': [{'input': [[2,3,1,1,4]], 'expected': True, 'is_hidden': False}, {'input': [[3,2,1,0,4]], 'expected': False, 'is_hidden': False}]
    },
    {
        'slug': 'kth-largest-element-in-an-array',
        'title': 'Kth Largest Element in an Array',
        'difficulty': 'Medium',
        'topics': ['Heap', 'Sorting', 'Arrays'],
        'companies': ['Facebook', 'Spotify'],
        'acceptance_rate': 66.8,
        'readiness_impact': 4,
        'function_name': 'findKthLargest',
        'description': 'Given an integer array `nums` and an integer `k`, return the `k`th largest element in the array.\n\nNote that it is the `k`th largest element in the sorted order, not the `k`th distinct element.',
        'constraints': ['1 <= k <= nums.length <= 10^5', '-10^4 <= nums[i] <= 10^4'],
        'examples': [{'input': 'nums = [3,2,1,5,6,4], k = 2', 'output': '5'}],
        'hints': ['Can you solve it using a min-heap?'],
        'starter_code': {'python': 'class Solution:\n    def findKthLargest(self, nums, k):\n        pass\n'},
        'test_cases': [{'input': [[3,2,1,5,6,4], 2], 'expected': 5, 'is_hidden': False}]
    }
]

for p_data in problems:
    test_cases = p_data.pop('test_cases', [])
    # Update if exists
    problem, created = CodingProblem.objects.update_or_create(slug=p_data['slug'], defaults=p_data)
    TestCase.objects.filter(problem=problem).delete()
    for tc in test_cases:
        TestCase.objects.create(
            problem=problem,
            input_data=tc['input'],
            expected_output=tc['expected'],
            is_hidden=tc['is_hidden']
        )
    print(f'Created/Updated problem: {problem.title}')

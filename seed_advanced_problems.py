import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from core.models import CodingProblem, TestCase

problems = [
    {
        'slug': 'median-of-two-sorted-arrays',
        'title': 'Median of Two Sorted Arrays',
        'difficulty': 'Hard',
        'topics': ['Arrays', 'Binary Search', 'Divide and Conquer'],
        'companies': ['Amazon', 'Google', 'Apple', 'Microsoft'],
        'acceptance_rate': 38.2,
        'readiness_impact': 5,
        'function_name': 'findMedianSortedArrays',
        'description': 'Given two sorted arrays `nums1` and `nums2` of size `m` and `n` respectively, return the median of the two sorted arrays.\n\nThe overall run time complexity should be `O(log (m+n))`.' ,
        'constraints': ['nums1.length == m', 'nums2.length == n', '0 <= m <= 1000', '0 <= n <= 1000', '1 <= m + n <= 2000', '-10^6 <= nums1[i], nums2[i] <= 10^6'],
        'examples': [{'input': 'nums1 = [1,3], nums2 = [2]', 'output': '2.00000', 'explanation': 'merged array = [1,2,3] and median is 2.'}, {'input': 'nums1 = [1,2], nums2 = [3,4]', 'output': '2.50000', 'explanation': 'merged array = [1,2,3,4] and median is (2 + 3) / 2 = 2.5.'}],
        'hints': ['Use binary search to partition the two arrays.'],
        'starter_code': {'python': 'class Solution:\n    def findMedianSortedArrays(self, nums1, nums2):\n        pass\n'},
        'test_cases': [
            {'input': [[1,3], [2]], 'expected': 2.00000, 'is_hidden': False}, 
            {'input': [[1,2], [3,4]], 'expected': 2.50000, 'is_hidden': False},
            {'input': [[0,0], [0,0]], 'expected': 0.00000, 'is_hidden': True}
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
        'function_name': 'trap',
        'description': 'Given `n` non-negative integers representing an elevation map where the width of each bar is `1`, compute how much water it can trap after raining.',
        'constraints': ['n == height.length', '1 <= n <= 2 * 10^4', '0 <= height[i] <= 10^5'],
        'examples': [{'input': 'height = [0,1,0,2,1,0,1,3,2,1,2,1]', 'output': '6', 'explanation': 'The above elevation map is represented by array [0,1,0,2,1,0,1,3,2,1,2,1]. In this case, 6 units of rain water are being trapped.'}],
        'hints': ['Think about calculating the max height to the left and right of every bar.'],
        'starter_code': {'python': 'class Solution:\n    def trap(self, height):\n        pass\n'},
        'test_cases': [
            {'input': [[0,1,0,2,1,0,1,3,2,1,2,1]], 'expected': 6, 'is_hidden': False}, 
            {'input': [[4,2,0,3,2,5]], 'expected': 9, 'is_hidden': False},
            {'input': [[1,0,1]], 'expected': 1, 'is_hidden': True}
        ]
    },
    {
        'slug': 'n-queens',
        'title': 'N-Queens',
        'difficulty': 'Hard',
        'topics': ['Backtracking', 'Arrays'],
        'companies': ['Microsoft', 'Amazon', 'Adobe'],
        'acceptance_rate': 66.1,
        'readiness_impact': 4,
        'function_name': 'solveNQueens',
        'description': 'The n-queens puzzle is the problem of placing `n` queens on an `n x n` chessboard such that no two queens attack each other.\n\nGiven an integer `n`, return all distinct solutions to the n-queens puzzle. You may return the answer in any order.\n\nEach solution contains a distinct board configuration of the n-queens placement, where `"Q"` and `"."` both indicate a queen and an empty space, respectively.',
        'constraints': ['1 <= n <= 9'],
        'examples': [{'input': 'n = 4', 'output': '[[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]]', 'explanation': 'There exist two distinct solutions to the 4-queens puzzle.'}],
        'hints': ['Use backtracking and maintain a set of occupied diagonals and columns.'],
        'starter_code': {'python': 'class Solution:\n    def solveNQueens(self, n):\n        pass\n'},
        'test_cases': [
            {'input': [4], 'expected': [[".Q..","...Q","Q...","..Q."],["..Q.","Q...","...Q",".Q.."]], 'is_hidden': False}, 
            {'input': [1], 'expected': [["Q"]], 'is_hidden': False}
        ]
    },
    {
        'slug': 'word-ladder',
        'title': 'Word Ladder',
        'difficulty': 'Hard',
        'topics': ['Graphs', 'BFS', 'Hash Table', 'String'],
        'companies': ['Amazon', 'LinkedIn', 'Google'],
        'acceptance_rate': 38.1,
        'readiness_impact': 5,
        'function_name': 'ladderLength',
        'description': 'A transformation sequence from word `beginWord` to word `endWord` using a dictionary `wordList` is a sequence of words `beginWord -> s1 -> s2 -> ... -> sk` such that:\n\n- Every adjacent pair of words differs by a single letter.\n- Every `si` for `1 <= i <= k` is in `wordList`. Note that `beginWord` does not need to be in `wordList`.\n- `sk == endWord`\n\nGiven two words, `beginWord` and `endWord`, and a dictionary `wordList`, return the number of words in the shortest transformation sequence from `beginWord` to `endWord`, or `0` if no such sequence exists.',
        'constraints': ['1 <= beginWord.length <= 10', 'endWord.length == beginWord.length', '1 <= wordList.length <= 5000', 'wordList[i].length == beginWord.length', 'beginWord, endWord, and wordList[i] consist of lowercase English letters.', 'beginWord != endWord', 'All the words in wordList are unique.'],
        'examples': [{'input': 'beginWord = "hit", endWord = "cog", wordList = ["hot","dot","dog","lot","log","cog"]', 'output': '5', 'explanation': 'One shortest transformation sequence is "hit" -> "hot" -> "dot" -> "dog" -> "cog", which is 5 words long.'}],
        'hints': ['Use Breadth First Search (BFS) to find the shortest path.'],
        'starter_code': {'python': 'class Solution:\n    def ladderLength(self, beginWord, endWord, wordList):\n        pass\n'},
        'test_cases': [
            {'input': ["hit", "cog", ["hot","dot","dog","lot","log","cog"]], 'expected': 5, 'is_hidden': False}, 
            {'input': ["hit", "cog", ["hot","dot","dog","lot","log"]], 'expected': 0, 'is_hidden': False}
        ]
    },
    {
        'slug': 'lru-cache',
        'title': 'LRU Cache',
        'difficulty': 'Medium',
        'topics': ['Hash Table', 'Linked Lists', 'Design'],
        'companies': ['Amazon', 'Microsoft', 'Bloomberg'],
        'acceptance_rate': 41.7,
        'readiness_impact': 5,
        'function_name': 'LRUCache', # This implies class based execution which our runner might not support well, but let's assume we can mock it or the user implements a single function for arrays
        'description': 'Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.\n\nImplement the `LRUCache` class:\n\n- `LRUCache(int capacity)` Initialize the LRU cache with positive size `capacity`.\n- `int get(int key)` Return the value of the `key` if the key exists, otherwise return `-1`.\n- `void put(int key, int value)` Update the value of the `key` if the `key` exists. Otherwise, add the `key-value` pair to the cache. If the number of keys exceeds the `capacity` from this operation, evict the least recently used key.\n\nThe functions `get` and `put` must each run in `O(1)` average time complexity.',
        'constraints': ['1 <= capacity <= 3000', '0 <= key <= 10^4', '0 <= value <= 10^5', 'At most 2 * 10^5 calls will be made to get and put.'],
        'examples': [],
        'hints': ['Use a doubly linked list combined with a hash map.'],
        'starter_code': {'python': 'class LRUCache:\n    def __init__(self, capacity: int):\n        pass\n    def get(self, key: int) -> int:\n        pass\n    def put(self, key: int, value: int) -> None:\n        pass\n'},
        'test_cases': [] # Skipped actual execution test cases for design problem for now, but added to DB for UI
    },
    {
        'slug': 'merge-k-sorted-lists',
        'title': 'Merge k Sorted Lists',
        'difficulty': 'Hard',
        'topics': ['Linked Lists', 'Divide and Conquer', 'Heap', 'Merge Sort'],
        'companies': ['Amazon', 'Facebook', 'Microsoft'],
        'acceptance_rate': 50.8,
        'readiness_impact': 5,
        'function_name': 'mergeKLists',
        'description': 'You are given an array of `k` linked-lists `lists`, each linked-list is sorted in ascending order.\n\nMerge all the linked-lists into one sorted linked-list and return it.',
        'constraints': ['k == lists.length', '0 <= k <= 10^4', '0 <= lists[i].length <= 500', '-10^4 <= lists[i][j] <= 10^4', 'lists[i] is sorted in ascending order.', 'The sum of lists[i].length will not exceed 10^4.'],
        'examples': [{'input': 'lists = [[1,4,5],[1,3,4],[2,6]]', 'output': '[1,1,2,3,4,4,5,6]', 'explanation': 'The linked-lists are:\n[\n  1->4->5,\n  1->3->4,\n  2->6\n]\nmerging them into one sorted list:\n1->1->2->3->4->4->5->6'}],
        'hints': ['Use a priority queue (min heap) to constantly get the minimum element among the heads of all linked lists.'],
        'starter_code': {'python': 'class Solution:\n    def mergeKLists(self, lists):\n        pass\n'},
        'test_cases': [
            {'input': [[[1,4,5],[1,3,4],[2,6]]], 'expected': [1,1,2,3,4,4,5,6], 'is_hidden': False}, 
            {'input': [[]], 'expected': [], 'is_hidden': False}
        ]
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

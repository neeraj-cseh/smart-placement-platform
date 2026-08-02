import os
import re

filepath = 'c:/Users/neera/OneDrive/Desktop/smart-placement-platform/core/views.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace two-sum wrapper
old_two_sum = '''    "two-sum": """
import sys

# User code starts here
{user_code}
# User code ends here

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        nums = list(map(int, lines[0].split()))
        target = int(lines[1])
        sol = Solution()
        res = sol.twoSum(nums, target)
        print(" ".join(map(str, res)))
""","""'''

new_two_sum = '''    "two-sum": """
import sys
import ast

# User code starts here
{user_code}
# User code ends here

if __name__ == "__main__":
    lines = sys.stdin.read().splitlines()
    if len(lines) >= 2:
        try:
            nums_str = lines[0].split("=")[-1].strip() if "=" in lines[0] else lines[0]
            nums = ast.literal_eval(nums_str)
        except:
            nums = list(map(int, lines[0].replace("[","").replace("]","").replace(","," ").split()))
            
        try:
            target_str = lines[1].split("=")[-1].strip() if "=" in lines[1] else lines[1]
            target = int(target_str)
        except:
            target = int(lines[1])
            
        sol = Solution()
        # Support both solve and twoSum for compatibility with different templates
        func = getattr(sol, "solve", getattr(sol, "twoSum", None))
        if func:
            res = func(nums, target)
            if hasattr(res, "__iter__"):
                print(str(list(res)).replace(" ",""))
            else:
                print(res)
        else:
            print("Error: Solution class must have a solve() or twoSum() method")
""","""'''

content = content.replace(old_two_sum, new_two_sum)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Wrappers updated successfully.")

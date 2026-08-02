import os
import re

filepath = 'c:/Users/neera/OneDrive/Desktop/smart-placement-platform/core/views.py'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix linked-list-cycle wrapper
old_llc = '''        sol = Solution()
        print("true" if sol.hasCycle(nodes[0]) else "false")
"""'''
new_llc = '''        sol = Solution()
        func = getattr(sol, "solve", getattr(sol, "hasCycle", None))
        if func:
            print("true" if func(nodes[0]) else "false")
        else:
            print("Error: Solution class must have a solve() or hasCycle() method")
"""'''
content = content.replace(old_llc, new_llc)

# Fix invert-binary-tree wrapper
old_ibt = '''    root = build_tree(vals)
    sol = Solution()
    inverted = sol.invertTree(root)
    print(serialize(inverted))
"""'''
new_ibt = '''    root = build_tree(vals)
    sol = Solution()
    func = getattr(sol, "solve", getattr(sol, "invertTree", None))
    if func:
        inverted = func(root)
        print(serialize(inverted))
    else:
        print("Error: Solution class must have a solve() or invertTree() method")
"""'''
content = content.replace(old_ibt, new_ibt)

# Fix number-of-islands wrapper
old_noi = '''    grid = [list(line.strip().split()) for line in lines]
    sol = Solution()
    print(sol.numIslands(grid))
"""'''
new_noi = '''    grid = [list(line.strip().split()) for line in lines]
    sol = Solution()
    func = getattr(sol, "solve", getattr(sol, "numIslands", None))
    if func:
        print(func(grid))
    else:
        print("Error: Solution class must have a solve() or numIslands() method")
"""'''
content = content.replace(old_noi, new_noi)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)

print("Wrappers updated successfully.")

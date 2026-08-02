#!/usr/bin/env python
import sys
import os
sys.path.insert(0, 'c:\\Users\\neera\\OneDrive\\Desktop\\smart-placement-platform.worktrees\\agents-ui-revision-and-error-checking')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

try:
    import django
    django.setup()
    from core.views import CodeExecuteView, CodeExecutionThrottle
    print("✓ CodeExecuteView imported successfully")
    print("✓ CodeExecutionThrottle imported successfully")
    print("✓ All imports validated")
    sys.exit(0)
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Unexpected error: {e}")
    sys.exit(1)

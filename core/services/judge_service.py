import json
import sys
from core.models import CodingProblem, TestCase, CodeSubmission
from core.views import execute_code_locally

def build_runner_code(language, user_code, function_name="solve"):
    """
    Wraps the user code in a language-specific runner template.
    """
    if language == 'python':
        runner = f"""
{user_code}

import sys, json

if __name__ == '__main__':
    try:
        input_data = json.loads(sys.stdin.read())
        sol = Solution()
        # Assume input_data is a list of args or a dict of kwargs
        if isinstance(input_data, dict):
            res = getattr(sol, '{function_name}')(**input_data)
        elif isinstance(input_data, list):
            res = getattr(sol, '{function_name}')(*input_data)
        else:
            res = getattr(sol, '{function_name}')(input_data)
        print(json.dumps(res))
    except Exception as e:
        print(f"Runner Error: {{str(e)}}", file=sys.stderr)
        sys.exit(1)
"""
        return runner
    
    if language == 'javascript':
        runner = f"""
{user_code}

const fs = require('fs');

try {{
    // Read from standard input (file descriptor 0)
    const input_data = JSON.parse(fs.readFileSync(0, 'utf-8'));
    let res;
    if (Array.isArray(input_data)) {{
        res = {function_name}(...input_data);
    }} else if (typeof input_data === 'object' && input_data !== null) {{
        res = {function_name}(...Object.values(input_data));
    }} else {{
        res = {function_name}(input_data);
    }}
    console.log(JSON.stringify(res));
}} catch (e) {{
    console.error("Runner Error: " + e.message);
    process.exit(1);
}}
"""
        return runner
        
    return user_code # Fallback

def evaluate_submission(submission_id, is_submit=False):
    submission = CodeSubmission.objects.get(id=submission_id)
    problem = submission.problem
    
    if not problem:
        submission.status = "Error: No problem linked"
        submission.save()
        return submission
        
    # Get test cases
    test_cases = problem.test_cases.all()
    if not is_submit:
        test_cases = test_cases.filter(is_hidden=False)
        
    if not test_cases.exists():
        submission.status = "Error: No test cases"
        submission.save()
        return submission
        
    max_time = 0
    max_memory = 0
    
    runner_code = build_runner_code(submission.language, submission.code, getattr(problem, 'function_name', 'solve'))
    
    for tc in test_cases:
        # Pass input_data as JSON string in stdin
        stdin_json = json.dumps(tc.input_data)
        
        # Execute using existing view function
        res = execute_code_locally(runner_code, stdin_json, submission.language, timeout=5)
        
        if res.get('execution_time_ms'):
            max_time = max(max_time, res['execution_time_ms'])
            
        if not res['success']:
            if res.get('timeout'):
                submission.status = "Time Limit Exceeded"
            else:
                submission.status = "Runtime Error"
            submission.error_output = res['error']
            submission.save()
            return submission
            
        # Parse output
        output_str = res['output'].strip()
        try:
            actual_output = json.loads(output_str)
            # Compare output
            if actual_output != tc.expected_output:
                submission.status = "Wrong Answer"
                submission.error_output = json.dumps({
                    "expected": tc.expected_output,
                    "actual": actual_output,
                    "input": tc.input_data
                })
                submission.save()
                return submission
        except json.JSONDecodeError:
            submission.status = "Wrong Answer"
            submission.error_output = json.dumps({
                "expected": tc.expected_output,
                "actual": output_str,
                "input": tc.input_data,
                "note": "Failed to parse JSON output"
            })
            submission.save()
            return submission
            
    submission.status = "Accepted"
    submission.execution_time_ms = max_time
    submission.memory_kb = 1024 + max_time * 2 # Mocking memory for now
    submission.save()
    
    return submission

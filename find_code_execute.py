with open('core/views.py') as f:
    for i, line in enumerate(f, 1):
        if 'class CodeExecuteView' in line:
            print(f"Found at line {i}")
            # Print next 50 lines
            for j in range(50):
                next_line = f.readline()
                if not next_line:
                    break
                print(f"{i+j+1}: {next_line}", end="")
            break

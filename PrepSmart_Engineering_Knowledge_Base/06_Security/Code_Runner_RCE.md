# Security Risk: Remote Code Execution (RCE)
* **Objective**: Execute untrusted user Python/JS code.
* **Implementation**: Currently uses Python `subprocess.run()`.
* **Risk**: Extremely critical. Malicious users can execute arbitrary shell commands.
* **Mitigation Implementation**: Must transition to isolated, ephemeral Docker containers with stripped network access.

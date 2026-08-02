# Security Considerations

## Code Runner
The `subprocess` implementation is vulnerable to RCE. Mitigation requires Docker sandboxing.
## Authentication
JWT tokens are stored in localStorage, making them vulnerable to XSS.
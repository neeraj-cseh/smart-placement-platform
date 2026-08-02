# Authentication

## Flow
1. POST /login
2. Receive JWT
3. Attach to Authorization header
4. POST /refresh when expired.
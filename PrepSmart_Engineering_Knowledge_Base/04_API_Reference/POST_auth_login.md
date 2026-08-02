# API: Login
* **Purpose**: Authenticate user and issue JWT.
* **Method**: POST
* **URL**: `/api/auth/login/`
* **Headers**: `Content-Type: application/json`
* **Authentication**: `AllowAny`
* **Request**: `{"email": "x", "password": "y"}`
* **Response**: `{"access": "...", "refresh": "..."}`
* **Validation**: Checks email existence.
* **Database Interaction**: Reads `accounts_user`.
* **Possible Errors**: 401 Unauthorized.

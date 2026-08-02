# Implementation: JWT Security
* **Objective**: Stateless session management.
* **Internal Architecture**: `djangorestframework-simplejwt`.
* **Validation**: Cryptographic HMAC signature verification against `SECRET_KEY`.
* **Vulnerabilities**: Stored in `localStorage` making it vulnerable to XSS.
* **Future Optimization**: Move to `HttpOnly` secure cookies.

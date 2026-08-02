# Diagram: Entity Relationship
```mermaid
erDiagram
    USER ||--o| USER_PROFILE : has
    USER ||--o{ USER_ANSWER : attempts
    QUESTION ||--o{ USER_ANSWER : receives
    TOPIC ||--o{ QUESTION : contains
```

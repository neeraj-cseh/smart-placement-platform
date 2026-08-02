# Diagram: System Architecture
```mermaid
graph TD
    React[Vite React SPA] -->|HTTPS| DRF[Django REST API]
    DRF --> MySQL[(MySQL DB)]
    DRF --> LLM(OpenAI/Gemini)
    DRF -.->|Vulnerable Subprocess| CodeRunner(Local Sandbox)
```

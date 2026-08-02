# Algorithm: LLM Interview Evaluation
* **Objective**: Grade a user's typed response dynamically.
* **Workflow**:
  1. Retrieve chat history (`InterviewQA` table).
  2. Format strict system prompt instructing JSON output (`{"score": X, "feedback": "Y"}`).
  3. POST to LLM API (OpenAI/Gemini).
  4. Parse JSON string from response.
  5. Update `InterviewSession` state.

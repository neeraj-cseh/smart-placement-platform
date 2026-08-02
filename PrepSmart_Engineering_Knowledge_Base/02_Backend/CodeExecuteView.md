# View: CodeExecuteView
* **Objective**: Evaluate user code against test cases.
* **Internal Architecture**: `APIView`
* **Business Logic**: 
  1. Fetch `CodingProblem`.
  2. Fetch related `TestCase` records.
  3. Execute subprocess passing `TestCase.input_data` to `stdin`.
  4. Compare `stdout` to `TestCase.expected_output`.
* **Validation**: DRF Serializer validates `language` and `code`.
* **Authentication**: `IsAuthenticated`.
* **Error Handling**: Catches `TimeoutError` for TLE (Time Limit Exceeded).

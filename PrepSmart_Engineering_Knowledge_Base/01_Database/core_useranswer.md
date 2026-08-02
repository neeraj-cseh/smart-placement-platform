# Table: core_useranswer
* **Database**: MySQL
* **Purpose**: Historical ledger of MCQ attempts for analytics.
* **Normalization**: 3NF

## Fields
* `id`: Integer (PK)
* `user_id`: Integer (FK -> accounts_user)
* `question_id`: Integer (FK -> core_question)
* `selected_answer`: VARCHAR(1)
* `is_correct`: BOOLEAN
* `created_at`: DATETIME

## Indexes
* `idx_user_correct`: Index on `(user_id, is_correct)`
* `idx_created_at`: Index on `(created_at)`

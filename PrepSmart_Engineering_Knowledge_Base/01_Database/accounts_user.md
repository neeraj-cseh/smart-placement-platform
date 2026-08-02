# Table: accounts_user
* **Database**: MySQL
* **Purpose**: Primary identity table overriding Django `AbstractBaseUser`.
* **Normalization**: 3NF

## Fields
* `id`: Integer (PK, Auto-Increment)
* `email`: VARCHAR(254) (Unique)
* `password`: VARCHAR(128) (Hashed PBKDF2)
* `name`: VARCHAR(255)
* `is_active`: BOOLEAN (Default: True)
* `is_staff`: BOOLEAN (Default: False)
* `created_at`: DATETIME

## Indexes
* `email` (Unique Index)

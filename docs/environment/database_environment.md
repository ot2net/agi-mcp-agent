# Database Environment

The `DatabaseEnvironment` provides a secure interface for agents to interact with various database systems, supporting SQL queries, transactions, and connection management.

## Overview

Database operations are fundamental for many agent tasks involving persistent data storage and retrieval. The `DatabaseEnvironment` provides a consistent interface to:

- Execute SQL queries and statements
- Manage database connections
- Handle transactions
- Process query results
- Support multiple database engines
- Ensure secure parameter handling

## Initialization

```python
from agi_mcp_agent.environment import DatabaseEnvironment

# SQLite database
db_env = DatabaseEnvironment(
    name="example-db",
    connection_string="sqlite:///data/example.db"
)

# PostgreSQL database
postgres_env = DatabaseEnvironment(
    name="postgres-db",
    connection_string="postgresql://username:password@localhost:5432/dbname",
    pool_size=5,
    max_overflow=10,
    pool_timeout=30
)

# MySQL database
mysql_env = DatabaseEnvironment(
    name="mysql-db",
    connection_string="mysql+pymysql://username:password@localhost:3306/dbname"
)
```

## Basic Operations

### Executing Queries

```python
# Simple SELECT query
result = db_env.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM users WHERE status = 'active'",
    "fetch": "all"
})

# Access the query results
if result["success"]:
    rows = result["rows"]
    columns = result["columns"]
    row_count = result["row_count"]
    
    print(f"Found {row_count} rows")
    for row in rows:
        print(f"User: {row['name']}, Email: {row['email']}")
else:
    print(f"Error: {result['error']}")

# Fetch a single row
single_result = db_env.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM users WHERE id = 42",
    "fetch": "one"
})
if single_result["success"] and single_result["row"]:
    user = single_result["row"]
    print(f"User: {user['name']}")
```

### Parameterized Queries

```python
# Using parameters to prevent SQL injection
param_result = db_env.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM products WHERE category = :category AND price <= :max_price",
    "parameters": {
        "category": "electronics",
        "max_price": 500
    },
    "fetch": "all"
})

# Positional parameters
pos_param_result = db_env.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM orders WHERE user_id = ? AND status = ?",
    "parameters": [42, "shipped"],
    "fetch": "all"
})
```

### Data Modification

```python
# INSERT operation
insert_result = db_env.execute_action({
    "operation": "execute",
    "sql": "INSERT INTO users (name, email, created_at) VALUES (:name, :email, :created_at)",
    "parameters": {
        "name": "Jane Smith",
        "email": "jane@example.com",
        "created_at": "2023-05-15T14:30:00"
    }
})

if insert_result["success"]:
    last_id = insert_result["last_id"]
    affected_rows = insert_result["affected_rows"]
    print(f"Inserted user with ID {last_id}")
else:
    print(f"Error: {insert_result['error']}")

# UPDATE operation
update_result = db_env.execute_action({
    "operation": "execute",
    "sql": "UPDATE products SET price = :price WHERE id = :id",
    "parameters": {
        "price": 199.99,
        "id": 123
    }
})
print(f"Updated {update_result['affected_rows']} rows")

# DELETE operation
delete_result = db_env.execute_action({
    "operation": "execute",
    "sql": "DELETE FROM cart_items WHERE user_id = :user_id AND added_at < :expiry_time",
    "parameters": {
        "user_id": 42,
        "expiry_time": "2023-04-01T00:00:00"
    }
})
print(f"Deleted {delete_result['affected_rows']} expired cart items")
```

## Advanced Features

### Transactions

```python
# Start a transaction
tx_start = db_env.execute_action({
    "operation": "begin_transaction"
})

try:
    # Execute multiple operations in the transaction
    db_env.execute_action({
        "operation": "execute",
        "sql": "UPDATE accounts SET balance = balance - :amount WHERE id = :from_id",
        "parameters": {
            "amount": 100,
            "from_id": 1
        }
    })
    
    db_env.execute_action({
        "operation": "execute",
        "sql": "UPDATE accounts SET balance = balance + :amount WHERE id = :to_id",
        "parameters": {
            "amount": 100,
            "to_id": 2
        }
    })
    
    # Commit the transaction
    db_env.execute_action({
        "operation": "commit_transaction"
    })
    print("Transaction committed successfully")
except Exception as e:
    # Rollback on error
    db_env.execute_action({
        "operation": "rollback_transaction"
    })
    print(f"Transaction rolled back due to error: {str(e)}")
```

### Batch Operations

```python
# Execute batch INSERT
batch_insert = db_env.execute_action({
    "operation": "batch_execute",
    "sql": "INSERT INTO log_entries (level, message, timestamp) VALUES (:level, :message, :timestamp)",
    "parameters_list": [
        {"level": "INFO", "message": "Application started", "timestamp": "2023-05-15T08:00:00"},
        {"level": "WARNING", "message": "High memory usage", "timestamp": "2023-05-15T08:15:30"},
        {"level": "ERROR", "message": "Database connection failed", "timestamp": "2023-05-15T08:16:45"}
    ]
})
print(f"Inserted {batch_insert['affected_rows']} log entries")
```

### Schema Operations

```python
# Create a table
create_table = db_env.execute_action({
    "operation": "execute",
    "sql": """
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        price REAL NOT NULL,
        category TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """
})

# Add a column
add_column = db_env.execute_action({
    "operation": "execute",
    "sql": "ALTER TABLE products ADD COLUMN description TEXT"
})

# Create an index
create_index = db_env.execute_action({
    "operation": "execute",
    "sql": "CREATE INDEX idx_products_category ON products (category)"
})
```

### Raw Execution

For operations that don't return standard results:

```python
# Execute a raw command
raw_result = db_env.execute_action({
    "operation": "raw_execute",
    "sql": "VACUUM"  # Example SQLite command
})
```

## Security Features

The `DatabaseEnvironment` implements several security features:

- **Parameterized queries**: Prevents SQL injection attacks
- **Connection string masking**: Hides credentials in logs and error messages
- **Permission controls**: Can restrict operations based on configured permissions
- **Query timeouts**: Prevents long-running queries from consuming resources
- **Connection pooling**: Efficiently manages database connections

## Working with Multiple Databases

```python
# Create environments for different databases
main_db = DatabaseEnvironment(
    name="main-db",
    connection_string="postgresql://user:pass@main-db:5432/main"
)

analytics_db = DatabaseEnvironment(
    name="analytics-db",
    connection_string="postgresql://user:pass@analytics-db:5432/analytics"
)

# Execute queries on different databases
user_result = main_db.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM users WHERE id = :id",
    "parameters": {"id": 42},
    "fetch": "one"
})

analytics_result = analytics_db.execute_action({
    "operation": "query",
    "sql": "SELECT COUNT(*) as visit_count FROM page_visits WHERE user_id = :user_id",
    "parameters": {"user_id": 42},
    "fetch": "one"
})

print(f"User: {user_result['row']['name']}")
print(f"Visit count: {analytics_result['row']['visit_count']}")
```

## Testing Helpers

For testing database operations:

```python
# Create an in-memory SQLite database for testing
test_db = DatabaseEnvironment(
    name="test-db",
    connection_string="sqlite:///:memory:"
)

# Initialize with test schema
test_db.execute_action({
    "operation": "execute",
    "sql": """
    CREATE TABLE test_users (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT
    )
    """
})

# Insert test data
test_db.execute_action({
    "operation": "execute",
    "sql": "INSERT INTO test_users (name, email) VALUES (:name, :email)",
    "parameters": {
        "name": "Test User",
        "email": "test@example.com"
    }
})

# Run test queries
test_result = test_db.execute_action({
    "operation": "query",
    "sql": "SELECT * FROM test_users",
    "fetch": "all"
})
assert len(test_result["rows"]) == 1
assert test_result["rows"][0]["name"] == "Test User"
```

## Example Usage

Complete example of using the `DatabaseEnvironment`:

```python
from agi_mcp_agent.environment import DatabaseEnvironment

# Initialize the environment with SQLite database
db_env = DatabaseEnvironment(
    name="example-db",
    connection_string="sqlite:///example.db"
)

try:
    # Create a table if it doesn't exist
    db_env.execute_action({
        "operation": "execute",
        "sql": """
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
    })
    
    # Insert a new contact
    insert_result = db_env.execute_action({
        "operation": "execute",
        "sql": "INSERT INTO contacts (name, email, phone) VALUES (:name, :email, :phone)",
        "parameters": {
            "name": "John Doe",
            "email": "john@example.com",
            "phone": "555-123-4567"
        }
    })
    print(f"Inserted contact with ID: {insert_result['last_id']}")
    
    # Query all contacts
    query_result = db_env.execute_action({
        "operation": "query",
        "sql": "SELECT * FROM contacts ORDER BY name",
        "fetch": "all"
    })
    
    print(f"Found {query_result['row_count']} contacts:")
    for contact in query_result["rows"]:
        print(f"  {contact['name']} - {contact['email']}")
        
    # Perform an update
    db_env.execute_action({
        "operation": "execute",
        "sql": "UPDATE contacts SET phone = :phone WHERE email = :email",
        "parameters": {
            "phone": "555-987-6543",
            "email": "john@example.com"
        }
    })
    print("Updated contact information")
    
finally:
    # Clean up resources
    db_env.close()
``` 
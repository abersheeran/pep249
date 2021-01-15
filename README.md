# pep249

Provide minimum implementation check and connection pool of PEP249.

## Usage

### Connection Pool

Sample using [phoenixdb](https://pypi.org/project/phoenixdb/) with connection pool:

```python
from pep249 import ConnectionPool

conn_pool = ConnectionPool(
    maxsize=12,
    connection_factory=lambda: phoenixdb.connect(
        "http://localhost:8765/", autocommit=True
    ),
)

with conn_pool.connect() as connection:
    ...
```

**Note**: The connection pool does not actively initialize the connection, it is initialized only when it is needed.

### Minimum implementation check

```python
from pep249 import Connection, Cursor

assert issubclass(YOUR_CONNECTION_CLASS, Connection)
assert isinstance(YOUR_CONNECTION, Connection)

assert issubclass(YOUR_CURSOR_CLASS, Cursor)
assert isinstance(YOUR_CURSOR, Cursor)
```

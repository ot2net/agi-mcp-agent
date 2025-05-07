"""Database environment implementation for agent interactions with databases."""

import logging
import json
from typing import Any, Dict, List, Optional, Union, Tuple

import sqlalchemy
from sqlalchemy import create_engine, text, Table, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError

from agi_mcp_agent.environment.base import Environment

logger = logging.getLogger(__name__)


class DatabaseEnvironment(Environment):
    """Environment that provides access to databases."""

    def __init__(
        self, 
        name: str, 
        connection_string: str,
        max_results: int = 1000,
        echo: bool = False,
        schema: str = None
    ):
        """Initialize the database environment.

        Args:
            name: The name of the environment
            connection_string: SQLAlchemy connection string
            max_results: Maximum number of results to return for queries
            echo: Whether to echo SQL queries (for debugging)
            schema: The database schema to use
        """
        super().__init__(name)
        self.connection_string = connection_string
        self.max_results = max_results
        self.echo = echo
        self.schema = schema
        self.engine = None
        self.metadata = None
        self.connection = None
        self.state = {
            "connected": False,
            "last_query": None,
            "last_result": None,
            "last_error": None
        }
        
        # Initialize the database connection
        self._initialize_connection()
        
        logger.info(f"Database Environment {self.name} initialized")

    def _initialize_connection(self):
        """Initialize the database connection."""
        try:
            self.engine = create_engine(self.connection_string, echo=self.echo)
            self.metadata = MetaData(schema=self.schema)
            self.metadata.reflect(bind=self.engine)
            self.state["connected"] = True
            logger.info(f"Connected to database ({self.connection_string.split('@')[-1]})")
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            self.state["last_error"] = str(e)
            self.state["connected"] = False

    def _get_connection(self):
        """Get a database connection, creating it if necessary."""
        if not self.engine or not self.state["connected"]:
            self._initialize_connection()
            
        if not self.connection or self.connection.closed:
            self.connection = self.engine.connect()
            
        return self.connection

    def execute_action(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a database operation.

        Args:
            action: The operation to execute with the following keys:
                - operation: The operation to perform (query, execute, etc.)
                - additional operation-specific parameters

        Returns:
            The result of the operation
        """
        operation = action.get("operation", "").lower()
        
        try:
            if operation == "query":
                return self._execute_query(
                    query=action.get("query", ""),
                    params=action.get("params", {}),
                    max_results=action.get("max_results", self.max_results)
                )
            elif operation == "execute":
                return self._execute_statement(
                    statement=action.get("statement", ""),
                    params=action.get("params", {})
                )
            elif operation == "list_tables":
                return self._list_tables()
            elif operation == "describe_table":
                return self._describe_table(action.get("table", ""))
            elif operation == "count":
                return self._count_records(
                    table=action.get("table", ""),
                    condition=action.get("condition", None)
                )
            elif operation == "connect":
                return self._test_connection()
            else:
                logger.warning(f"Unknown database operation: {operation}")
                return {"success": False, "error": f"Unknown operation: {operation}"}
                
        except Exception as e:
            logger.error(f"Error in database operation {operation}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}

    def _execute_query(self, query: str, params: Dict[str, Any] = None, max_results: int = None) -> Dict[str, Any]:
        """Execute a SELECT query.

        Args:
            query: The SQL query to execute
            params: Query parameters
            max_results: Maximum number of results to return

        Returns:
            The query results
        """
        if not query:
            return {"success": False, "error": "No query provided"}
        
        if not max_results:
            max_results = self.max_results
            
        params = params or {}
        
        try:
            conn = self._get_connection()
            
            # Store for reference
            self.state["last_query"] = query
            
            # Execute the query
            result = conn.execute(text(query), params)
            
            # Get column names
            columns = result.keys()
            
            # Fetch results
            rows = result.fetchmany(max_results)
            
            # Convert to list of dicts for easier consumption
            records = []
            for row in rows:
                record = {}
                for i, column in enumerate(columns):
                    value = row[i]
                    # Handle non-serializable types
                    if isinstance(value, (sqlalchemy.Numeric, sqlalchemy.Integer, sqlalchemy.Float, sqlalchemy.Boolean)):
                        value = float(value) if isinstance(value, sqlalchemy.Numeric) else value
                    elif hasattr(value, 'isoformat'):  # datetime-like objects
                        value = value.isoformat()
                    record[column] = value
                records.append(record)
            
            # Store results for reference
            self.state["last_result"] = {
                "columns": list(columns),
                "record_count": len(records)
            }
            
            return {
                "success": True,
                "columns": list(columns),
                "records": records,
                "record_count": len(records),
                "truncated": result.rowcount > max_results if result.rowcount >= 0 else None
            }
            
        except SQLAlchemyError as e:
            logger.error(f"SQL error executing query: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}

    def _execute_statement(self, statement: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a non-SELECT SQL statement (INSERT, UPDATE, DELETE, etc.).

        Args:
            statement: The SQL statement to execute
            params: Statement parameters

        Returns:
            The execution result
        """
        if not statement:
            return {"success": False, "error": "No statement provided"}
            
        params = params or {}
        
        try:
            conn = self._get_connection()
            
            # Store for reference
            self.state["last_query"] = statement
            
            # Execute the statement
            result = conn.execute(text(statement), params)
            
            # Get affected rows
            rowcount = result.rowcount
            
            # Store results for reference
            self.state["last_result"] = {
                "rowcount": rowcount
            }
            
            return {
                "success": True,
                "rowcount": rowcount,
                "lastrowid": getattr(result, 'lastrowid', None)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"SQL error executing statement: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}
            
    def _list_tables(self) -> Dict[str, Any]:
        """List all tables in the database.

        Returns:
            List of tables
        """
        try:
            inspector = inspect(self.engine)
            
            tables = []
            for table_name in inspector.get_table_names(schema=self.schema):
                tables.append({
                    "name": table_name,
                    "schema": self.schema
                })
            
            return {
                "success": True,
                "tables": tables,
                "count": len(tables)
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error listing tables: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}

    def _describe_table(self, table: str) -> Dict[str, Any]:
        """Describe a table's structure.

        Args:
            table: The table name

        Returns:
            Table structure information
        """
        if not table:
            return {"success": False, "error": "No table name provided"}
            
        try:
            inspector = inspect(self.engine)
            
            if table not in inspector.get_table_names(schema=self.schema):
                return {"success": False, "error": f"Table '{table}' not found"}
            
            # Get columns
            columns = []
            for column in inspector.get_columns(table, schema=self.schema):
                columns.append({
                    "name": column["name"],
                    "type": str(column["type"]),
                    "nullable": column.get("nullable", True),
                    "default": str(column.get("default", "None")),
                    "primary_key": column.get("primary_key", False)
                })
            
            # Get primary key
            pk = inspector.get_pk_constraint(table, schema=self.schema)
            
            # Get foreign keys
            fks = []
            for fk in inspector.get_foreign_keys(table, schema=self.schema):
                fks.append({
                    "name": fk.get("name"),
                    "referred_schema": fk.get("referred_schema"),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns"),
                    "constrained_columns": fk.get("constrained_columns")
                })
            
            # Get indexes
            indexes = []
            for idx in inspector.get_indexes(table, schema=self.schema):
                indexes.append({
                    "name": idx.get("name"),
                    "unique": idx.get("unique", False),
                    "columns": idx.get("column_names", [])
                })
            
            return {
                "success": True,
                "table": table,
                "schema": self.schema,
                "columns": columns,
                "primary_key": pk.get("constrained_columns", []) if pk else [],
                "foreign_keys": fks,
                "indexes": indexes
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error describing table {table}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}

    def _count_records(self, table: str, condition: str = None) -> Dict[str, Any]:
        """Count records in a table.

        Args:
            table: The table name
            condition: Optional WHERE condition

        Returns:
            Record count
        """
        if not table:
            return {"success": False, "error": "No table name provided"}
            
        try:
            query = f"SELECT COUNT(*) as count FROM {table}"
            if condition:
                query += f" WHERE {condition}"
                
            conn = self._get_connection()
            result = conn.execute(text(query))
            count = result.scalar()
            
            return {
                "success": True,
                "table": table,
                "count": count
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Error counting records in table {table}: {str(e)}")
            self.state["last_error"] = str(e)
            return {"success": False, "error": str(e)}
            
    def _test_connection(self) -> Dict[str, Any]:
        """Test the database connection.

        Returns:
            Connection status
        """
        try:
            conn = self._get_connection()
            
            # Try a simple query to test the connection
            conn.execute(text("SELECT 1"))
            
            return {
                "success": True,
                "connected": True,
                "connection_string": self._mask_connection_string()
            }
            
        except SQLAlchemyError as e:
            logger.error(f"Connection test failed: {str(e)}")
            self.state["last_error"] = str(e)
            return {
                "success": False,
                "connected": False,
                "error": str(e),
                "connection_string": self._mask_connection_string()
            }
            
    def _mask_connection_string(self) -> str:
        """Mask sensitive information in the connection string.

        Returns:
            Masked connection string
        """
        # This is a simple implementation that might need customization
        # based on the specific format of your connection strings
        if "://" not in self.connection_string:
            return self.connection_string
            
        parts = self.connection_string.split("://", 1)
        prefix = parts[0]
        
        if "@" in parts[1]:
            auth, rest = parts[1].split("@", 1)
            if ":" in auth:
                user, _ = auth.split(":", 1)
                return f"{prefix}://{user}:******@{rest}"
        
        return self.connection_string

    def get_observation(self) -> Dict[str, Any]:
        """Get the current state of the database environment.

        Returns:
            The current state
        """
        return {
            "connected": self.state["connected"],
            "last_error": self.state["last_error"]
        }

    def reset(self) -> Dict[str, Any]:
        """Reset the environment state.

        Returns:
            The initial state
        """
        # Close existing connection
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
            
        self.state = {
            "connected": self.state["connected"],  # Keep connection status
            "last_query": None,
            "last_result": None,
            "last_error": None
        }
        
        return self.get_observation()
        
    def close(self) -> None:
        """Close the database connection."""
        if self.connection and not self.connection.closed:
            self.connection.close()
            self.connection = None
            
        self.state["connected"] = False
        logger.info(f"Closed database connection for environment {self.name}")
        
    def __del__(self):
        """Destructor to ensure connection is closed."""
        self.close() 
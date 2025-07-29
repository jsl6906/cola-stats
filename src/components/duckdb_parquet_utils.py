"""
Generic utilities for querying DuckDB and outputting parquet files
for Observable Framework data loaders.
"""

import sys
import os
import duckdb
import uuid
from dotenv import load_dotenv
from typing import Optional, Dict, Any

class DuckDBParquetExporter:
    """
    A utility class for executing DuckDB queries and outputting parquet files
    to stdout for Observable Framework data loaders.
    """
    
    def __init__(self, 
                 motherduck_token: Optional[str] = None,
                 database_name: str = 'ttb_public_data'):
        """
        Initialize the exporter.
        
        Args:
            motherduck_token: MotherDuck token (if None, will try to load from env)
            database_name: Name of the MotherDuck database
        """
        # Load environment variables
        load_dotenv()
        
        self.motherduck_token = motherduck_token or os.getenv('MOTHERDUCK_TOKEN')
        self.database_name = database_name
        self.connection = None
        
        if not self.motherduck_token:
            raise ValueError("MOTHERDUCK_TOKEN must be provided or set in environment")
    
    def connect(self):
        """Establish connection to MotherDuck"""
        if self.connection is None:
            connection_string = f'md:{self.database_name}?motherduck_token={self.motherduck_token}'
            self.connection = duckdb.connect(connection_string)
        return self.connection
    
    def close(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def execute_query_to_parquet(self, 
                                query: str, 
                                error_context: Optional[Dict[str, Any]] = None):
        """
        Execute a SQL query and output the results as parquet to stdout.
        
        Args:
            query: SQL query to execute
            error_context: Additional context to include in error output
        """
        try:
            conn = self.connect()
            
            # Generate a unique temporary filename to avoid conflicts
            temp_filename = f'temp_output_{uuid.uuid4().hex[:8]}.parquet'
            
            # Execute query and write to temporary parquet file
            copy_query = f"""
            COPY (
                {query}
            ) TO '{temp_filename}' (FORMAT PARQUET);
            """
            
            conn.execute(copy_query)
            
            # Read the parquet file and output to stdout
            with open(temp_filename, 'rb') as f:
                sys.stdout.buffer.write(f.read())
            
            # Clean up temp file
            os.remove(temp_filename)
            
        except Exception as e:
            self._output_error_parquet(e, error_context)
    
    def _output_error_parquet(self, 
                             error: Exception, 
                             context: Optional[Dict[str, Any]] = None):
        """
        Output an error as a parquet file to stdout.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        try:
            conn = self.connect()
            
            # Build error information
            error_info = {
                'error': str(error).replace("'", "''"),  # Escape single quotes for SQL
                'error_type': type(error).__name__,
                'database': self.database_name
            }
            
            # Add context information if provided
            if context:
                for key, value in context.items():
                    error_info[f'context_{key}'] = str(value).replace("'", "''")
            
            # Create error query
            error_columns = []
            for key, value in error_info.items():
                error_columns.append(f"'{value}' as {key}")
            
            error_query = f"SELECT {', '.join(error_columns)}"
            
            # Generate unique temp filename for error output
            error_filename = f'error_output_{uuid.uuid4().hex[:8]}.parquet'
            
            conn.execute(f"""
                COPY (
                    {error_query}
                ) TO '{error_filename}' (FORMAT PARQUET);
            """)
            
            with open(error_filename, 'rb') as f:
                sys.stdout.buffer.write(f.read())
            
            os.remove(error_filename)
            
        except Exception as nested_error:
            # If we can't even create an error parquet, create minimal empty output
            self._create_minimal_error_output(error, nested_error)
    
    def _create_minimal_error_output(self, original_error, nested_error):
        """Create a minimal error output when all else fails"""
        try:
            # Create an empty parquet file with just error info
            minimal_filename = f'minimal_error_{uuid.uuid4().hex[:8]}.parquet'
            
            # Use a simple local DuckDB connection for minimal error output
            local_conn = duckdb.connect()
            local_conn.execute(f"""
                COPY (
                    SELECT 
                        'Error occurred' as status,
                        '{str(original_error)[:100]}' as original_error,
                        '{str(nested_error)[:100]}' as nested_error
                ) TO '{minimal_filename}' (FORMAT PARQUET);
            """)
            
            with open(minimal_filename, 'rb') as f:
                sys.stdout.buffer.write(f.read())
            
            os.remove(minimal_filename)
            local_conn.close()
            
        except Exception:
            # Ultimate fallback - just exit
            pass
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def create_parquet_loader(query: str, 
                         database_name: str = 'ttb_public_data',
                         error_context: Optional[Dict[str, Any]] = None):
    """
    Convenience function to create a parquet data loader.
    
    Args:
        query: SQL query to execute
        database_name: MotherDuck database name
        error_context: Additional context for error reporting
    
    Example usage in a data loader script:
    
    ```python
    from duckdb_parquet_utils import create_parquet_loader
    
    query = "SELECT * FROM schema.table WHERE condition = 'value'"
    create_parquet_loader(query, error_context={'schema': 'my_schema'})
    ```
    """
    with DuckDBParquetExporter(database_name=database_name) as exporter:
        exporter.execute_query_to_parquet(query, error_context)

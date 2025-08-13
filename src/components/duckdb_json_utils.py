"""
Generic utilities for querying DuckDB and outputting JSON files
for Observable Framework data loaders.
"""

import sys
import os
import duckdb
import json
from dotenv import load_dotenv
from typing import Optional, Dict, Any

class DuckDBJSONExporter:
    """
    A utility class for executing DuckDB queries and outputting JSON files
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
    
    def execute_query_to_json(self, 
                             query: str, 
                             error_context: Optional[Dict[str, Any]] = None):
        """
        Execute a SQL query and output the results as JSON to stdout.
        
        Args:
            query: SQL query to execute
            error_context: Additional context to include in error output
        """
        try:
            conn = self.connect()
            
            # Execute query and fetch results
            result = conn.execute(query).fetchall()
            columns = [desc[0] for desc in conn.description]
            
            # Convert to list of dictionaries
            data = []
            for row in result:
                row_dict = {}
                for i, value in enumerate(row):
                    row_dict[columns[i]] = value
                data.append(row_dict)
            
            # Output JSON to stdout
            json.dump(data, sys.stdout, default=str, indent=2)
            
        except Exception as e:
            self._output_error_json(e, error_context)
    
    def _output_error_json(self, 
                          error: Exception, 
                          context: Optional[Dict[str, Any]] = None):
        """
        Output an error as JSON to stdout.
        
        Args:
            error: The exception that occurred
            context: Additional context information
        """
        try:
            # Build error information
            error_info = {
                'error': str(error),
                'error_type': type(error).__name__,
                'database': self.database_name,
                'status': 'error'
            }
            
            # Add context information if provided
            if context:
                error_info['context'] = context
            
            # Output error as JSON
            json.dump([error_info], sys.stdout, indent=2)
            
        except Exception as nested_error:
            # If we can't even create an error JSON, create minimal output
            self._create_minimal_error_output(error, nested_error)
    
    def _create_minimal_error_output(self, original_error, nested_error):
        """Create a minimal error output when all else fails"""
        try:
            minimal_error = {
                'status': 'error',
                'original_error': str(original_error)[:200],
                'nested_error': str(nested_error)[:200]
            }
            json.dump([minimal_error], sys.stdout, indent=2)
        except Exception:
            # Ultimate fallback - just print empty array
            print("[]")
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


def create_json_loader(query: str, 
                      database_name: str = 'ttb_public_data',
                      error_context: Optional[Dict[str, Any]] = None):
    """
    Convenience function to create a JSON data loader.
    
    Args:
        query: SQL query to execute
        database_name: MotherDuck database name
        error_context: Additional context for error reporting
    
    Example usage in a data loader script:
    
    ```python
    from duckdb_json_utils import create_json_loader
    
    query = "SELECT * FROM schema.table WHERE condition = 'value'"
    create_json_loader(query, error_context={'schema': 'my_schema'})
    ```
    """
    with DuckDBJSONExporter(database_name=database_name) as exporter:
        exporter.execute_query_to_json(query, error_context)

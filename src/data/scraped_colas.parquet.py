"""
Data loader for COLA (Certificate of Label Approval) data from MotherDuck.
Uses the generic DuckDB parquet utility for consistent data loading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
from duckdb_parquet_utils import create_parquet_loader

# Define the SQL query
query = """
SELECT * FROM cola_images.vw_colas
"""

# Error context for better debugging
error_context = {
    'schema': 'cola_images',
    'table': 'vw_colas',
    'loader': 'scraped_colas'
}

# Execute query and output parquet to stdout
create_parquet_loader(query, error_context=error_context)
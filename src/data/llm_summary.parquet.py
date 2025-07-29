"""
Data loader for COLA LLM Analysis Summary data from MotherDuck.
Uses the generic DuckDB parquet utility for consistent data loading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
from duckdb_parquet_utils import create_parquet_loader

# Define the SQL query for summary statistics
query = """--sql
SELECT
  model_version,
  analysis_type,
  ct_commodity,
  total_colas_analyzed,
  num_colas_with_violations,
  percent_colas_with_violations,
  tokens_per_cola,
  first_analysis_date as first_analysis,
  last_analysis_date as last_analysis
FROM cola_images.vw_llm_summary
"""

# Error context for better debugging
error_context = {
    'schema': 'cola_images',
    'table': 'vw_llm_summary',
    'loader': 'llm_summary'
}

# Execute query and output parquet to stdout
create_parquet_loader(query, error_context=error_context)

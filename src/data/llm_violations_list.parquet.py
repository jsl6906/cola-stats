"""
Data loader for COLA LLM Analysis Violations data from MotherDuck.
Uses the generic DuckDB parquet utility for consistent data loading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
from duckdb_parquet_utils import create_parquet_loader

# Define the SQL query for summary statistics
query = """--sql
SELECT
  cola_id,
  cola_form_url,
  cola_internal_url,
  ct_commodity,
  ct_source,
  violation_comment,
  violation_type,
  violation_group,
  violation_subgroup,
  cfr_ref,
  analysis_type,
  analysis_model
FROM cola_images.vw_cola_violations_list
"""

# Error context for better debugging
error_context = {
    'schema': 'cola_images',
    'table': 'vw_cola_violations_list',
    'loader': 'llm_violations_list'
}

# Execute query and output parquet to stdout
create_parquet_loader(query, error_context=error_context)

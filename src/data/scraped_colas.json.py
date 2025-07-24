import json
import sys
import os
import duckdb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
MOTHERDUCK_TOKEN = os.getenv('MOTHERDUCK_TOKEN')
MD_DB_NAME = 'ttb_public_data'
MD_SCHEMA_NAME = 'cola_images'

try:
    # Connect to MotherDuck
    conn = duckdb.connect(f'md:{MD_DB_NAME}?motherduck_token={MOTHERDUCK_TOKEN}')
    
    query = f"""
    SELECT * FROM {MD_SCHEMA_NAME}.vw_colas
    """
    result = conn.execute(query).fetchall()
    columns = [desc[0] for desc in conn.description]
    
    # Convert to list of dictionaries
    data = [dict(zip(columns, row)) for row in result]
    
    # Convert dates to strings for JSON serialization
    for record in data:
        for key, value in record.items():
            if hasattr(value, 'isoformat'):  # datetime or date object
                record[key] = value.isoformat()
    
    # Output JSON
    json.dump(data, sys.stdout, default=str)
    
except Exception as e:
    # Output error information
    error_data = {
        "error": str(e),
        "error_type": type(e).__name__,
        "database": MD_DB_NAME,
        "schema": MD_SCHEMA_NAME
    }
    json.dump(error_data, sys.stdout, indent=2)
    
finally:
    if 'conn' in locals():
        conn.close()
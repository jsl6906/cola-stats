"""
Data loader for Public Comments data from MotherDuck.
Uses the generic DuckDB JSON utility for consistent data loading.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'components'))
from duckdb_json_utils import create_json_loader

# Define the SQL query for public comments with document details and attachments
query = """--sql
USE ttb_public_comments;
SELECT
    -- Count of attachments for this comment
    (SELECT COUNT(*) 
     FROM attachments a 
     WHERE a.comment_id = c.comment_id) as attachment_count,
    -- Create array of objects containing comment text and attachment texts
    ARRAY(
      -- Always include the comment text as the first element with source 'default'
      SELECT {'source': 'DIRECT (NON-ATTACHMENT)', 'text': c.comment_text}
      UNION ALL
      -- Add attachment texts with their file URLs as sources
      SELECT {'source': a.attachment_file_url, 'text': a.attachment_parsed_text}
      FROM attachments a
      WHERE a.comment_id = c.comment_id
        AND a.attachment_parsed_text IS NOT NULL
        AND a.attachment_parsed_text != ''
    ) as comment_text_sources,
    c.*,
    -- Document details
    d.document_type,
    d.document_title,
    d.document_posted_date,
    d.docket_id,
    d.document_subtype,
    d.agency_id,
    d.comment_start_date,
    d.comment_end_date,
    d.within_comment_period,
    d.open_for_comment,
    d.cfr_part,
    d.fr_doc_num,
    d.fr_vol_num,
    d.start_end_page,
    d.abstract as document_abstract
  FROM comments c
  LEFT JOIN documents d ON c.document_id = d.document_id
"""

# Error context for better debugging
error_context = {
    'schema': 'public_comments',
    'tables': ['comments', 'documents', 'attachments'],
    'loader': 'public_comments'
}

# Execute query and output JSON to stdout
create_json_loader(query, error_context=error_context)
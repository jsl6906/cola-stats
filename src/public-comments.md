# TTB Public Comments via Regulations.gov

```js
const comments_file = FileAttachment("./data/public_comments.json").json();
```

```js
// Load the actual comments data
const comments = await comments_file;
```

```js
// Get file metadata for display with error handling
const commentsFile = FileAttachment("./data/public_comments.json");
const fileSize = commentsFile.size ? (commentsFile.size / 1024).toFixed(1) : "Unknown"; // Convert to KB
const lastModified = commentsFile.lastModified ? new Date(commentsFile.lastModified) : null;
const href = commentsFile.href;
const downloadName = "public_comments_" + lastModified.toISOString().replace(/[:.]/g, "-") + ".json";
```

<div style="margin-bottom: 1rem;">
  <small style="color: #666; font-size: 0.75em;">
    Data as of ${lastModified.toLocaleString()} | <a href="./data/public_comments.json" download="public_comments.json" style="color: #0066cc;">Download raw data</a>
  </small>
</div>


```js
// Group comments by document and get all documents with comment counts
const documentSummary = Array.from(
  d3.rollup(
    comments.filter(d => d.document_posted_date), // Only include documents with valid posted dates
    v => {
      // Calculate count of comments with any attachments for this document
      const commentsWithAttachments = v.filter(d => (d.attachment_count || 0) > 0).length;
      
      // Find the most recent comment date for this document
      const commentDates = v.map(d => d.comment_received_date || d.comment_posted_date).filter(d => d);
      const lastCommentDate = commentDates.length > 0 ? 
        new Date(Math.max(...commentDates.map(d => new Date(d)))) : null;
      
      return {
        comment_count: v.length,
        document_title: v[0].document_title || "Unknown Title",
        document_type: v[0].document_type || "Unknown",
        document_posted_date: v[0].document_posted_date,
        docket_id: v[0].docket_id || "Unknown",
        comments_with_attachments: commentsWithAttachments,
        last_comment_date: lastCommentDate
      };
    },
    d => d.document_id
  ),
  ([document_id, data]) => ({
    document_id,
    ...data
  })
)
.sort((a, b) => b.comment_count - a.comment_count); // Sort by most comments first

// Show detailed table of all documents
display(html`<h4>All Documents Detail</h4>`);
display(Inputs.table(documentSummary, {
  columns: [
    "document_title",
    "comment_count", 
    "comments_with_attachments",
    "document_posted_date",
    "last_comment_date",
    "document_type",
    "docket_id"
  ],
  header: {
    document_title: "Document Title",
    comment_count: "Comments",
    comments_with_attachments: "W/ Attachments",
    document_posted_date: "Posted Date",
    last_comment_date: "Last Comment",
    document_type: "Type",
    docket_id: "Docket ID"
  },
  format: {
    document_posted_date: d => new Date(d).toLocaleDateString(),
    last_comment_date: d => d ? new Date(d).toLocaleDateString() : "N/A",
    comment_count: d => d.toLocaleString(),
    comments_with_attachments: d => d.toLocaleString()
  },
  width: {
    document_title: 350,
    comment_count: 80,
    comments_with_attachments: 90,
    document_posted_date: 100,
    last_comment_date: 100,
    document_type: 120,
    docket_id: 120
  }
}));
```

```js
display(comments);
```

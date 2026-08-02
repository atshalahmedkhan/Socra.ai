# Authorization policies

Identity and classroom tables intentionally have no anonymous policies. Phase 1 product access goes through FastAPI using the backend-only database connection. If direct authenticated Supabase reads are added later, add narrowly scoped `auth.uid()` policies in a new migration; backend authorization remains mandatory.

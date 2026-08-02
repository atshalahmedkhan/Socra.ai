-- Clear test chat and calendar comments (run in Supabase SQL Editor)
-- Safe to re-run.

delete from public.chat_messages;
delete from public.day_comments;

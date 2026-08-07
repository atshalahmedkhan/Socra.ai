# Legacy — Research Collaboration Site

This directory contains a static multi-page research-project collaboration
website built before the Socra tutoring platform existed. It predates the
FastAPI backend, the Next.js frontend, and the tutoring domain schema.

## What this is

A browser-only application (no build step) that uses the Supabase JavaScript
client directly from a CDN. It provides:

- `index.html` — team overview and phase status
- `login.html` — client-side mock login
- `calendar.html` — calendar with phase markers and day comments
- `gantt.html` — Gantt timeline and progress tracker
- `chat.html` — team chat with three channels and date pins
- `project_timeline_gantt_dates.html` — alternate Gantt view

## Supabase schema

`supabase_schema.sql` creates the tables used by this site:
`chat_messages`, `day_comments`, `phase_statuses`, `chat_perms`.

**This schema is entirely separate from the product tutoring schema.**
Do not merge it with `backend/database/migrations/`.

## Setup

1. Copy `.env.example` → the ignored `.env` file and set `SUPABASE_URL` and
   `SUPABASE_PUBLISHABLE_KEY` (or `SUPABASE_ANON_KEY`) from the Supabase
   dashboard for the **research** project (not the tutoring product project).
2. Run `supabase_schema.sql` in the Supabase SQL editor for the research project.
3. Open `login.html` in a browser or run `npm start` from the repository root.

The legacy build step (`npm run build` at root) runs
`legacy/scripts/generate-config.js` to produce a `config.js` file from
environment variables. This file is git-ignored.

## Mock credentials

| User ID | Password | Role   |
|---------|----------|--------|
| PD01    | 0202     | owner  |
| TG05    | 1515     | tejas  |
| AK03    | 0909     | atshal |

## Deployment

`legacy/vercel.json` configures the Vercel deployment for this static site.
Move it to the repository root if deploying this site from Vercel.

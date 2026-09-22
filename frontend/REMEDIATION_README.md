# Socra Remediation Module - UI Demo

A Next.js MVP UI for the Socra Remediation Module - a student-facing feature that helps CS students practice their weak points identified during lab sessions.

## Features

### Dashboard (`/dashboard`)
- Displays student's weak points from recent lab sessions
- Shows 3 mock topic cards with difficulty indicators
- "Start a Custom Topic" input for self-directed practice
- Clean, focused design with deep navy background and teal accents

### Practice Session (`/practice/[topic]`)
- **Chat Mode**: Socratic AI conversation interface
  - AI asks guiding questions, never gives direct answers
  - Mock conversations for Binary Search Trees and Recursion Depth
  - Real-time message input
- **Quiz Mode**: Multiple choice questions with progress tracking
  - Visual progress indicator
  - Interactive answer selection
  - Mock questions for different topics
- **Flashcards Mode**: UI placeholder (not implemented)

### Components
- `Navbar`: Top navigation with Socra branding
- `TopicCard`: Displays weak point topics with difficulty indicators
- `ChatBubble`: Message bubbles for AI and student
- `QuizCard`: Quiz interface with options and progress

## Design System

**Colors:**
- Background: Deep Navy (`#0f172a`)
- Cards: White (`#ffffff`)
- Accent: Teal (`#0d9488`)
- Text: White on navy, Gray on white

**Typography:**
- Font: Inter (Google Fonts)
- Weights: 300, 400, 500, 600, 700

**Layout:**
- Fully responsive
- Tailwind CSS for styling
- Clean, minimal design - focused and calm

## Getting Started

### Install Dependencies
```bash
cd frontend
npm install
```

### Run Development Server
```bash
npm run dev
```

Open [http://localhost:3000/dashboard](http://localhost:3000/dashboard) in your browser.

## Routes

- `/dashboard` - Main landing page after lab session
- `/practice/[topic]` - Practice session page (chat mode)
- `/practice/[topic]?mode=quiz` - Quiz mode for a topic

## Mock Data

All data is hardcoded for demo purposes:

**Weak Points:**
1. Binary Search Trees (high difficulty)
2. Recursion Depth (medium difficulty)
3. Big-O Analysis (low difficulty)

**Sample Conversations:**
- Pre-loaded Socratic dialogues for BST and Recursion topics

**Quiz Questions:**
- Mock multiple choice questions for each topic

## Tech Stack

- **Framework**: Next.js 16.2.10
- **React**: 19.2.4
- **Styling**: Tailwind CSS 4
- **TypeScript**: 5.x
- **Fonts**: Inter via Google Fonts

## Notes

- No API calls - all state is client-side with `useState`
- No backend integration needed
- No authentication flow (assumes student is logged in)
- Ready for professor demo - clean, professional UI

## File Structure

```
frontend/
├── app/
│   ├── dashboard/
│   │   └── page.tsx          # Main dashboard
│   ├── practice/
│   │   └── [topic]/
│   │       └── page.tsx      # Practice session
│   ├── layout.tsx            # Root layout
│   └── globals.css           # Global styles
└── components/
    ├── Navbar.tsx            # Top navigation
    ├── TopicCard.tsx         # Weak point card
    ├── ChatBubble.tsx        # Chat message bubble
    └── QuizCard.tsx          # Quiz question card
```

## Demo Tips

When showing to a professor:
1. Start on `/dashboard` - the weak points cards make the concept immediately visual
2. Click "Practice This" on any card to show the Socratic chat interface
3. Toggle to Quiz mode to demonstrate different practice formats
4. Highlight that the AI never gives direct answers - only guiding questions
5. Show custom topic input to demonstrate flexibility

## Future Enhancements (Not in MVP)

- Real API integration with backend
- Actual AI model integration
- Flashcards mode implementation
- Progress tracking and analytics
- Session history
- Spaced repetition algorithm
- Collaborative study features

# STORY BLOCKS

> A web-based interactive storytelling platform — build branching narratives with a visual node editor, AI co-pilot, and instant playback. Think **Twine**, but with a brutal edge.

![Django](https://img.shields.io/badge/Django-4.2-092E20?style=flat-square&logo=django)
![HTMX](https://img.shields.io/badge/HTMX-1.9-3366CC?style=flat-square)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-CDN-06B6D4?style=flat-square&logo=tailwindcss)
![Groq AI](https://img.shields.io/badge/Groq_AI-LLaMA_3.3-F55036?style=flat-square)

---

## Overview

**Story Blocks** is a full-stack Django application for creating, editing, and playing interactive fiction. Authors build branching stories using a visual infinite-canvas editor where narrative nodes are connected by player choices. A built-in AI co-pilot (powered by Groq/LLaMA 3.3) assists with writing — enhancing prose, suggesting branching choices, and expanding scenes.

### Key Features

| Feature | Description |
|---|---|
| **Infinite Canvas Editor** | Drag, pan, and zoom across a dot-grid workspace. Nodes are positioned freely and connected by SVG bezier curves. Edges are clickable for easy deletion. |
| **Visual Node System** | Five node types — Start, Passage, Riddle, Death, Ending, Checkpoint — each color-coded on the canvas. |
| **Riddle Branching** | Create puzzles where edges dynamically branch based on the player's correct or incorrect answer. |
| **AI Co-Pilot** | Three AI writing modes: *Enhance Tone*, *Suggest Choices*, and *Expand Scene*, powered by Groq API. |
| **Live Player Engine** | Play through published stories in a dedicated reader interface with state tracking. |
| **Password Protection** | Creators can lock their unpublished or private stories behind a custom access password. |
| **Real-time Sync** | Node edits, deletions, and edge changes update the canvas instantly without page reloads (HTMX + Fetch). |
| **Community Gallery** | Browse and play published stories from other creators. |
| **Neo-Brutalist Design** | A bold aesthetic system with thick borders, hard-offset shadows, high-contrast accents, and zero rounded corners. |

---

## Design System

The entire UI follows a **Neo-brutalist** design language:

- **Typography:** Epilogue (headings, bold UI) + Space Grotesk (body, metadata)
- **Palette:** `#FFEE00` yellow primary · `#0448FF` blue secondary · `#BA1A1A` error red · `#006A6A` teal tertiary
- **Spacing:** 4px/8px rhythm, hard black borders (2px–4px), offset box-shadows
- **Motion:** Slide-in panels, fade-in cards, press-down button states

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 (Python) |
| Frontend Interactivity | HTMX 1.9 + Vanilla JavaScript |
| Styling | Tailwind CSS (CDN) |
| AI Service | Groq API (LLaMA 3.3 70B Versatile) |
| Database | SQLite (development) |
| Canvas Rendering | CSS Transforms + SVG (bezier curves) |

---

## Project Structure

```
StoryBoard/
├── engine/                  # Core Django app
│   ├── models.py            # Story, Node, Choice, GameState
│   ├── views.py             # All endpoints (CRUD, HTMX, AI, Player)
│   ├── urls.py              # URL routing
│   ├── forms.py             # Django forms for Node, Choice, Story
│   ├── services.py          # Groq AI integration layer
│   ├── admin.py             # Django admin configuration
│   └── seed_demo.py         # Demo story seeder script
├── storyboard/              # Django project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/
│   ├── engine/
│   │   ├── base.html        # Base template (design system, nav, fonts)
│   │   ├── dashboard.html   # Creator dashboard — project grid
│   │   ├── canvas.html      # Infinite canvas editor (core feature)
│   │   ├── community.html   # Public templates gallery
│   │   ├── player.html      # Story player interface
│   │   └── partials/
│   │       ├── node_editor.html      # Writer panel slide-out
│   │       ├── canvas_node.html      # Node HTML partial
│   │       ├── player_content.html   # Player passage partial
│   │       └── ai_result.html        # AI response partial
│   └── registration/
│       └── login.html       # Auth login page
├── static/                  # Static assets
├── manage.py
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Tarvel/Story-Blocks.git
cd Story-Blocks

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install django groq

# 4. Run migrations
python manage.py migrate

# 5. Create a superuser
python manage.py createsuperuser

# 6. (Optional) Seed the demo story
python manage.py shell < engine/seed_demo.py

# 7. Start the development server
python manage.py runserver
```

Then visit **http://127.0.0.1:8000/** to log in and start building stories.

### Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Optional | API key for the Groq AI co-pilot features. Get one at [console.groq.com](https://console.groq.com). Without it, the AI buttons will show a setup prompt instead of generating content. |

```bash
export GROQ_API_KEY='gsk_your_key_here'
```

---

## Usage

### Creating a Story

1. Log in and click **Create New** from the dashboard.
2. Fill in the title and description, then open the **Canvas Editor**.
3. **Double-click** the canvas to place new passage nodes.
4. Click a node header to open the **Writer Panel** and compose content.
5. Use **Add Edge** to connect nodes with player choices.
6. Hit **Playtest** to experience your story from a reader's perspective.

### Canvas Controls

| Action | Input |
|---|---|
| Create node | Double-click empty canvas **or** sidebar button |
| Move node | Drag the node body |
| Edit node | Click the node header |
| Edit edge | Click the edge line to select, edit, or delete |
| Pan canvas | Click and drag empty canvas |
| Zoom | `+` / `−` buttons (bottom-left) |
| Reset view | Center button (bottom-left) |
| Story settings | Click **Story Settings** in the sidebar to toggle publish status or set a password |
| Close editor | Click outside the panel or the `×` button |

### AI Co-Pilot

From inside the Writer Panel, use the three AI actions:

- **Enhance Tone** — Rewrites the passage with richer atmosphere and sensory detail.
- **Suggest Choices** — Generates 3 branching decisions for the current passage.
- **Expand Scene** — Adds a continuation paragraph that builds tension.

Click **Apply** on any AI result to inject it directly into the editor.

---

## Data Models

```
Story ──┬── Node (Start)
        ├── Node (Passage) ──── Choice ──→ Node (Passage)
        ├── Node (Passage) ──── Choice ──→ Node (Death)
        ├── Node (Ending)
        └── GameState (per user, tracks current_node + variables)
```

| Model | Purpose |
|---|---|
| `Story` | Top-level container. Has title, description, author, publish status, slug, UUID, and an optional access password. |
| `Node` | A single passage/scene. Stores content, type, canvas x/y coordinates, and optional correct answers for riddles. |
| `Choice` | An edge connecting two nodes. Stores the player-facing choice text. Can be marked as a correct or wrong path for riddle nodes. |
| `GameState` | Tracks player progress — current node and a JSON field for custom variables (health, inventory, flags). |

---

## API Endpoints

| Method | URL | Description |
|---|---|---|
| `GET` | `/` | Creator Dashboard |
| `GET` | `/story/<id>/canvas/` | Canvas Editor |
| `POST` | `/story/<id>/settings/` | Update story settings (publish, password) |
| `POST` | `/story/<id>/node/create/` | Create a node |
| `POST/PATCH` | `/node/<id>/update/` | Update node content or position |
| `DELETE` | `/node/<id>/delete/` | Delete a node |
| `GET` | `/node/<id>/detail/` | Load node editor panel (HTMX) |
| `POST` | `/story/<id>/choice/create/` | Create an edge |
| `DELETE` | `/choice/<id>/delete/` | Delete an edge |
| `POST` | `/ai/enhance/` | AI: Enhance passage |
| `POST` | `/ai/choices/` | AI: Suggest choices |
| `POST` | `/ai/expand/` | AI: Expand scene |
| `GET` | `/play/<slug>-<uuid>/` | Play a story |
| `GET` | `/play/choice/<id>/` | Make a player choice |
| `POST` | `/play/riddle/<id>/check/` | Validate a player's riddle answer |
| `GET` | `/community/` | Community templates gallery |

---

## Screenshots

> *Coming soon — screenshots of the Canvas Editor, Player Engine, and Community Gallery.*

---

## Roadmap

- [ ] Conditional choices (e.g., "only show if health > 5")
- [ ] Variable system UI for the `GameState` JSONField
- [ ] Story forking / "Use Template" from the Community Gallery
- [ ] PostgreSQL migration for production
- [ ] Static asset pipeline (Whitenoise / CDN)
- [ ] Story export (JSON / Twine format)

---

## License

This project is for educational and personal use.

---

**Built with 🟡 by [Tarvel](https://github.com/Tarvel)**

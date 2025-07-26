# SIGMA - Project Summary

## Project Overview

SIGMA is a cybersecurity-themed game with a terminal-style interface built using Pygame. The game features a mission-based system where players complete various cybersecurity challenges. The project follows a client-server architecture with a Python backend and a Next.js frontend.

## Project Structure

```bash

SIGMA/
├── backend/                     # Python backend server
│   ├── Game/                   # Main game package
│   │   ├── __init__.py
│   │   ├── main.py            # Main game loop and UI
│   │   └── sounds.py          # Sound management
│   ├── Database/               # Database operations
│   │   ├── __init__.py
│   │   ├── mission_store.py   # Mission data handling
│   │   └── init_schema.py     # Database schema initialization
│   ├── requirements.txt        # Python dependencies
│   └── assets/                # Game assets (sounds, images)
│       └── sounds/            # Sound effects and music
└── frontend/                   # Next.js web interface
    ├── public/                # Static assets
    ├── src/                   # Source code
    └── package.json           # Frontend dependencies
```

## Key Components

### 1. Game Engine (`backend/Game/main.py`)

The core game loop and UI rendering. Handles:

- Game state management
- User input processing
- Screen rendering
- Mission selection and progression

Key Classes:

- `GameEngine`: Main game controller
- `Mission`: Represents a playable mission
- `LoadingAnimation`: Handles loading screen animations

### 2. Sound System (`backend/Game/sounds.py`)

Manages all audio aspects of the game:

- Background music
- Sound effects
- Audio mixing and playback

Key Classes:

- `SoundManager`: Central sound controller
- Methods for playing, stopping, and managing audio resources

### 3. Database Layer (`backend/Database/`)

Handles data persistence and mission management:

- `mission_store.py`: CRUD operations for missions
- `init_schema.py`: Database schema definition and initialization

## How It Works

### Game Flow

1. **Initialization**:

   - Database connection is established
   - Game assets are loaded
   - Sound system is initialized

2. **Main Menu**:

   - Displays available missions
   - Shows mission details and difficulty
   - Handles user navigation

3. **Mission Execution**:

   - Loads selected mission
   - Presents challenge to player
   - Tracks progress and success/failure

4. **Completion**:
   - Updates player progress
   - Returns to mission selection

## Technical Details

### Dependencies

- **Backend**:

  - Python 3.13.2
  - Pygame 2.6.1
  - SQLAlchemy (for database operations)

- **Frontend**:
  - Next.js
  - TypeScript
  - Tailwind CSS

### Key Design Patterns

- **Singleton Pattern**: Used for SoundManager to ensure single audio context
- **State Pattern**: Manages different game states (menu, playing, loading)
- **Observer Pattern**: For event handling and UI updates

## Important Code Locations

1. **Game Initialization**:

   - `GameEngine.__init__()` in `main.py`
   - Sound system setup in `sounds.py`

2. **UI Rendering**:

   - `draw_mission_list()` in `main.py` (mission selection screen)
   - Text rendering and layout functions

3. **Mission Management**:

   - `Mission` class in `main.py`
   - Database operations in `mission_store.py`

4. **Audio Management**:
   - `SoundManager` class in `sounds.py`
   - Sound effect generation and playback

## Known Issues

1. Sound initialization error: `'pygame.mixer.Channel' object has no attribute 'fade'`
2. Some UI elements may need further refinement for different screen sizes

## Next Steps

1. Implement remaining mission types
2. Add player progression system
3. Enhance UI/UX with more visual feedback
4. Add sound effects for game events
5. Implement save/load functionality

## Running the Project

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m Game.main
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

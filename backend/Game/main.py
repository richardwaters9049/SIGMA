# File: /SIGMA/backend/game/main.py

import pygame
from engine import GameEngine


def main():
    # Initialise pygame
    pygame.init()
    # Create game engine instance
    game = GameEngine()
    # Run the main game loop
    game.run()
    # Quit pygame cleanly
    pygame.quit()


if __name__ == "__main__":
    main()

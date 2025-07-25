# File: /SIGMA/backend/game/engine.py

import pygame
import sys


class GameEngine:
    """Core game engine handling game loop, events and rendering."""

    def __init__(self, width=800, height=600):
        """Initialise game window and state."""
        # Set window size
        self.width = width
        self.height = height
        # Initialise display surface
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SIGMA: AI Hacker Protocol")
        # Clock for controlling frame rate
        self.clock = pygame.time.Clock()
        # Running state
        self.running = True

    def handle_events(self):
        """Process input events like keyboard and mouse."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        """Update game logic per frame (placeholder for now)."""
        pass

    def draw(self):
        """Draw game elements on the screen."""
        # Fill screen with black
        self.screen.fill((0, 0, 0))
        # Placeholder: draw text or game elements here
        pygame.display.flip()

    def run(self):
        """Main game loop running at 60 FPS."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)
        # Exit cleanly
        pygame.quit()
        sys.exit()

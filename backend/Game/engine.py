import pygame
import sys
from Database.mission_store import fetch_all_missions


class GameEngine:
    """Core game engine handling game loop, mission selection and rendering."""

    def __init__(self, width=800, height=600):
        """Initialise the game window, font, missions, and states."""
        # Set up window
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SIGMA: AI Hacker Protocol")
        self.clock = pygame.time.Clock()
        self.running = True

        # Initialise Pygame font system before creating fonts
        pygame.font.init()
        self.font = pygame.font.SysFont("Courier New", 20)

        # Fetch missions from database
        self.missions = fetch_all_missions()
        self.selected_index = 0  # Which mission is currently highlighted

        # State flags
        self.in_loading_screen = False
        self.loading_counter = 0  # For animation frames during loading

    def handle_events(self):
        """Handle input events for quitting, navigation, and selection."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if not self.in_loading_screen:
                    # Navigation with arrow keys only if not loading
                    if event.key == pygame.K_UP:
                        # Move selection up, wrap around if needed
                        self.selected_index = (self.selected_index - 1) % len(
                            self.missions
                        )

                    elif event.key == pygame.K_DOWN:
                        # Move selection down, wrap around if needed
                        self.selected_index = (self.selected_index + 1) % len(
                            self.missions
                        )

                    elif event.key == pygame.K_RETURN:
                        # Enter pressed: start loading screen for selected mission
                        self.in_loading_screen = True
                        self.loading_counter = 0

                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                else:
                    # If in loading screen, maybe ESC can cancel
                    if event.key == pygame.K_ESCAPE:
                        self.in_loading_screen = False

    def update(self):
        """Update game state."""
        if self.in_loading_screen:
            # Increment loading animation counter
            self.loading_counter += 1
            if self.loading_counter > 180:  # e.g. 3 seconds at 60 FPS
                # Loading complete - exit loading screen and back to menu (or next phase)
                self.in_loading_screen = False

    def draw_mission_list(self):
        """Draw the list of missions, highlighting the selected one."""
        y_offset = 50  # Starting y position for mission list

        header = self.font.render("Available Missions", True, (0, 255, 0))
        self.screen.blit(header, (20, 10))

        for idx, mission in enumerate(self.missions):
            # Format mission text with difficulty and name
            mission_text = f"[{mission['difficulty'].upper()}] {mission['name']}"

            # Highlight the selected mission differently
            if idx == self.selected_index:
                # Highlight background rectangle for selection
                pygame.draw.rect(
                    self.screen, (0, 100, 100), pygame.Rect(15, y_offset - 5, 770, 28)
                )

                # Draw selected text in bright cyan
                text_surface = self.font.render(mission_text, True, (0, 255, 255))
            else:
                # Normal text for other missions
                text_surface = self.font.render(mission_text, True, (0, 150, 150))

            self.screen.blit(text_surface, (20, y_offset))
            y_offset += 30

    def draw_loading_screen(self):
        """Display an animated loading screen with retro hacker style."""
        self.screen.fill((0, 0, 0))

        # Loading text animation (dots cycling)
        base_text = "LOADING MISSION"
        dots = (
            self.loading_counter // 15
        ) % 4  # Change dots every 15 frames (~0.25 sec)
        loading_text = base_text + ("." * dots)

        # Render loading text in green
        loading_surface = self.font.render(loading_text, True, (0, 255, 0))

        # Center loading text on screen
        rect = loading_surface.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(loading_surface, rect)

        # Optional: add flickering matrix-style vertical bars or scanlines
        for i in range(0, self.width, 20):
            alpha = 50 + (self.loading_counter * 10) % 205  # flicker effect
            line_surface = pygame.Surface((2, self.height))
            line_surface.set_alpha(alpha)
            line_surface.fill((0, 255, 0))
            self.screen.blit(line_surface, (i, 0))

    def draw(self):
        """Draw current screen depending on state."""
        if self.in_loading_screen:
            self.draw_loading_screen()
        else:
            self.screen.fill((0, 0, 0))  # Clear screen for menu
            self.draw_mission_list()

        pygame.display.flip()

    def run(self):
        """Main game loop running at 60 FPS."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # Limit to 60 FPS

        # Clean exit
        pygame.quit()
        sys.exit()

import pygame
import sys
import random
import math
import numpy
from Database.mission_store import fetch_all_missions


class GameEngine:
    """Core game engine with mission selection, hacker-style loading animation,
    CRT scanlines, typing effects, beep sounds, and glitch flickering."""

    def __init__(self, width=800, height=600):
        pygame.init()  # Initialise pygame

        # Window setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SIGMA: AI Hacker Protocol")
        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts: retro courier
        self.font = pygame.font.SysFont("Courier New", 20, bold=True)
        self.large_font = pygame.font.SysFont("Courier New", 28, bold=True)

        # Load missions from database
        self.missions = fetch_all_missions()
        self.selected_index = 0

        # Sound init
        pygame.mixer.init()
        self.beep_sound = self.create_beep_sound(frequency=880, duration=50)

        # For glitch flicker effect timing
        self.flicker_timer = 0

        # Pre-generate CRT scanline overlay surface
        self.scanline_overlay = self.create_scanline_overlay()

        print(f"[✅] Retrieved {len(self.missions)} mission(s).")

    def create_beep_sound(self, frequency=880, duration=100):
        """Generate a short beep sound programmatically."""
        sample_rate = 44100
        n_samples = int(sample_rate * duration / 1000)
        
        # Create a stereo sound buffer (2D array for left and right channels)
        buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
        
        # Fill both channels with the same sine wave
        for i in range(n_samples):
            val = int(32767 * 0.5 * math.sin(2.0 * math.pi * frequency * i / sample_rate))
            buf[i][0] = val  # Left channel
            buf[i][1] = val  # Right channel
            
        # Convert to a pygame sound
        sound = pygame.sndarray.make_sound(buf)
        return sound

    def play_beep(self):
        """Play beep sound (non-blocking)."""
        if self.beep_sound:
            self.beep_sound.play()

    def create_scanline_overlay(self):
        """Create semi-transparent black horizontal lines to simulate CRT scanlines."""
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 0))  # Fully transparent initially
        line_color = (0, 255, 0, 20)  # Very faint green line

        for y in range(0, self.height, 3):  # Every 3 pixels
            pygame.draw.line(overlay, line_color, (0, y), (self.width, y))
        return overlay

    def handle_events(self):
        """Process key and quit events with sound feedback."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.confirm_exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.confirm_exit()
                elif event.key == pygame.K_UP:
                    self.selected_index = max(0, self.selected_index - 1)
                    self.play_beep()
                elif event.key == pygame.K_DOWN:
                    self.selected_index = min(
                        len(self.missions) - 1, self.selected_index + 1
                    )
                    self.play_beep()
                elif event.key == pygame.K_RETURN:
                    self.play_beep()
                    selected = self.missions[self.selected_index]
                    print(f"[🚀] Mission Selected: {selected['name']}")
                    self.loading_screen(selected)

    def confirm_exit(self):
        """Show exit confirmation dialog."""
        confirm_font = pygame.font.SysFont("Courier New", 22, bold=True)
        confirming = True
        while confirming:
            self.screen.fill((0, 0, 0))
            msg1 = confirm_font.render("Exit SIGMA?", True, (0, 255, 0))
            msg2 = confirm_font.render("Y = Yes    N = No", True, (0, 255, 0))
            self.screen.blit(msg1, (self.width // 2 - 100, self.height // 2 - 30))
            self.screen.blit(msg2, (self.width // 2 - 120, self.height // 2 + 10))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        pygame.quit()
                        sys.exit()
                    elif event.key == pygame.K_n:
                        confirming = False

    def glitch_text(self, text, base_color=(0, 255, 0)):
        """Create a text surface with random flicker glitches."""
        # Render normal text
        base_surf = self.font.render(text, True, base_color)

        # Occasionally draw glitch rectangles
        glitch_surf = pygame.Surface(base_surf.get_size(), pygame.SRCALPHA)
        glitch_surf.fill((0, 0, 0, 0))

        # Flicker chance for glitch rectangles
        if random.random() < 0.15:
            for _ in range(random.randint(1, 3)):
                x = random.randint(0, base_surf.get_width() - 10)
                y = random.randint(0, base_surf.get_height() - 5)
                w = random.randint(5, 15)
                h = random.randint(1, 3)
                color = (0, 255, 0, random.randint(100, 180))
                pygame.draw.rect(glitch_surf, color, (x, y, w, h))
        base_surf.blit(glitch_surf, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        return base_surf

    def draw_mission_list(self):
        """Draw missions with selection highlight, glitch flicker, and scanline overlay."""
        self.screen.fill((0, 0, 0))  # Black background
        header = self.large_font.render("AVAILABLE MISSIONS", True, (0, 255, 0))
        self.screen.blit(header, (self.width // 2 - 180, 30))

        y_offset = 100
        for i, mission in enumerate(self.missions):
            prefix = "➤ " if i == self.selected_index else "   "
            base_color = (0, 255, 0) if i == self.selected_index else (0, 200, 200)
            mission_text = (
                f"{prefix}[{mission['difficulty'].upper()}] {mission['name']}"
            )

            # Flicker the selected mission text for glitch effect
            if i == self.selected_index:
                text_surface = self.glitch_text(mission_text, base_color)
            else:
                text_surface = self.font.render(mission_text, True, base_color)

            self.screen.blit(text_surface, (60, y_offset))
            y_offset += 35

        # Apply CRT scanline overlay on top
        self.screen.blit(self.scanline_overlay, (0, 0))

        pygame.display.flip()

    def type_text(self, text, pos, delay=30):
        """Render text with typing animation effect."""
        displayed_text = ""
        for char in text:
            displayed_text += char
            self.screen.fill(
                (0, 0, 0), (pos[0], pos[1], self.width, 40)
            )  # Clear previous text line
            rendered = self.font.render(displayed_text, True, (0, 255, 0))
            self.screen.blit(rendered, pos)
            pygame.display.flip()
            pygame.time.delay(delay)

    def loading_screen(self, mission):
        """Show retro hacker loading screen with typing animation and sounds."""
        messages = [
            f"// Booting mission kernel: {mission['name'].upper()}",
            "// Establishing neural link...",
            "// Injecting payload...",
            "// Running SIGMA_ENGAGE()",
            "// Breaching firewall layers",
            "// Access granted ✅",
        ]

        self.screen.fill((0, 0, 0))
        y_start = 100
        line_height = 40

        # Play beep for launch
        self.play_beep()
        pygame.time.delay(200)

        for i, msg in enumerate(messages):
            self.type_text(msg, (50, y_start + i * line_height), delay=40)
            self.play_beep()
            pygame.time.delay(150)

        # Final splash with flicker effect
        final_msg = f">>> MISSION: {mission['name'].upper()} LOADED <<<"
        for _ in range(15):
            self.screen.fill((0, 0, 0))
            flicker_color = (0, random.randint(150, 255), 0)
            splash = self.large_font.render(final_msg, True, flicker_color)
            self.screen.blit(splash, (self.width // 2 - 280, self.height // 2))
            self.screen.blit(self.scanline_overlay, (0, 0))
            pygame.display.flip()
            pygame.time.delay(80)

        # Pause 1 second before returning to menu
        pygame.time.delay(1000)
        self.selected_index = 0

    def run(self):
        """Main game loop: handle events, draw screen, control FPS."""
        while self.running:
            self.handle_events()
            self.draw_mission_list()
            self.clock.tick(60)
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    # Create and run the game
    game = GameEngine()
    game.run()

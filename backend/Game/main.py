import pygame
import sys
import random
import math
import numpy
import time
from typing import Dict, Any, Optional, List
import sys
import os

# Add parent directory to path to allow imports from Database
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Database.mission_store import fetch_all_missions
from sounds import SoundManager
from loading_animations import get_animation_for_mission, LoadingAnimation


class GameEngine:
    """Core game engine with mission selection, hacker-style loading animation,
    CRT scanlines, typing effects, beep sounds, and glitch flickering."""

    def __init__(self, width=800, height=600):
        pygame.init()  # Initialize pygame
        pygame.mixer.pre_init(44100, -16, 2, 2048)  # Better sound settings
        
        # Window setup
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SIGMA: AI Hacker Protocol")
        self.clock = pygame.time.Clock()
        self.running = True
        self.state = 'menu'  # 'menu', 'loading', 'game'
        
        # Initialize sound system
        self.sound_manager = SoundManager()
        
        # Fonts: retro courier with white color and letter spacing
        self.font_size = 24
        self.large_font_size = 32
        self.title_font_size = 56
        self.letter_spacing = 2
        self.text_color = (255, 255, 255)  # White
        self.highlight_color = (100, 255, 100)  # Light green for highlights
        
        # Create fonts with anti-aliasing for smoother text
        self.font = pygame.font.SysFont("Courier New", self.font_size, bold=True)
        self.large_font = pygame.font.SysFont("Courier New", self.large_font_size, bold=True)
        self.title_font = pygame.font.SysFont("Courier New", self.title_font_size, bold=True)
        
        # Load missions from database
        self.missions = fetch_all_missions()
        self.selected_index = 0
        
        # Animation state
        self.loading_animation: Optional[LoadingAnimation] = None
        self.loading_start_time = 0
        self.current_mission: Optional[Dict[str, Any]] = None
        
        # For glitch flicker effect timing
        self.flicker_timer = 0
        
        # Pre-generate CRT scanline overlay surface
        self.scanline_overlay = self.create_scanline_overlay()
        
        # Game state
        self.particle_systems: List[Any] = []
        
        print(f"[✅] Retrieved {len(self.missions)} mission(s).")

    def play_sound(self, sound_name: str, volume: float = 0.5):
        """Play a sound by name with optional volume control"""
        self.sound_manager.play(sound_name, volume)
        
    def toggle_mute(self):
        """Toggle sound on/off"""
        return self.sound_manager.toggle_mute()

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
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # Handle global key events
                if event.key == pygame.K_ESCAPE:
                    if not self.confirm_exit():
                        continue
                    self.running = False
                    
                # Handle menu navigation
                elif self.state == 'menu':
                    if event.key == pygame.K_RETURN:
                        self.play_sound('confirm')
                        if 0 <= self.selected_index < len(self.missions):
                            self.start_loading(self.missions[self.selected_index])
                            
                    elif event.key == pygame.K_DOWN:
                        self.play_sound('select')
                        self.selected_index = (self.selected_index + 1) % len(self.missions)
                        
                    elif event.key == pygame.K_UP:
                        self.play_sound('select')
                        self.selected_index = (self.selected_index - 1) % len(self.missions)
                        
                    elif event.key == pygame.K_m:
                        is_muted = self.toggle_mute()
                        print(f"Sound {'muted' if is_muted else 'unmuted'}")
                
                # Handle loading screen (skip with any key)
                elif self.state == 'loading' and event.key:
                    self.complete_loading()

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

    def render_text_with_spacing(self, text, font, color, x, y, spacing=0):
        """Render text with custom letter spacing"""
        x_offset = 0
        for char in text:
            if char == ' ':
                x_offset += font.size(' ')[0] + spacing
                continue
                
            char_surface = font.render(char, True, color)
            self.screen.blit(char_surface, (x + x_offset, y))
            x_offset += font.size(char)[0] + spacing
        
        # Return the total width of the rendered text
        return x_offset

    def draw_mission_list(self):
        """Draw missions with animated selection, glitch effects, and visual feedback."""
        # Draw animated background
        current_time = pygame.time.get_ticks()
        self.draw_background_effects(current_time)
        
        # Draw title with subtle animation
        title_alpha = 200 + 55 * math.sin(current_time * 0.002)
        title_color = (0, min(255, int(title_alpha)), 0)
        title = self.title_font.render("MISSION SELECT", True, title_color)
        title_shadow = self.title_font.render("MISSION SELECT", True, (0, 50, 0))
        
        # Draw title with shadow for depth
        self.screen.blit(title_shadow, (self.width // 2 - title.get_width()//2 + 3, 33))
        self.screen.blit(title, (self.width // 2 - title.get_width()//2, 30))
        
        # Draw mission list with smooth scrolling
        visible_missions = 5  # Number of missions visible at once
        start_idx = max(0, min(self.selected_index - visible_missions // 2, 
                             len(self.missions) - visible_missions))
        end_idx = min(start_idx + visible_missions, len(self.missions))
        
        # Calculate vertical center position for the list
        list_height = visible_missions * 50
        y_start = (self.height - list_height) // 2
        
        # Draw mission list background
        list_bg = pygame.Surface((self.width - 100, list_height + 20), pygame.SRCALPHA)
        list_bg.fill((0, 20, 0, 100))  # Semi-transparent dark background
        pygame.draw.rect(list_bg, (0, 100, 0, 100), list_bg.get_rect(), 1)  # Border
        self.screen.blit(list_bg, (50, y_start - 10))
        
        # Draw visible missions with smooth animations
        for i in range(start_idx, end_idx):
            mission = self.missions[i]
            is_selected = i == self.selected_index
            y_pos = y_start + (i - start_idx) * 50
            
            # Animate selected mission
            if is_selected:
                # Pulsing highlight effect
                highlight_alpha = 80 + 40 * math.sin(current_time * 0.005)
                highlight = pygame.Surface((self.width - 120, 45), pygame.SRCALPHA)
                highlight.fill((0, 150, 0, highlight_alpha))
                
                # Draw selection arrow
                arrow = self.large_font.render(">", True, (0, 255, 0))
                self.screen.blit(arrow, (60, y_pos + 10))
                
                # Draw highlight with border
                pygame.draw.rect(highlight, (0, 200, 0, 100), highlight.get_rect(), 1)
                self.screen.blit(highlight, (60, y_pos))
                
                # Add subtle glow effect
                glow = pygame.Surface((self.width - 100, 50), pygame.SRCALPHA)
                pygame.draw.rect(glow, (0, 100, 0, 30), glow.get_rect(), 0, 5)
                self.screen.blit(glow, (50, y_start - 10), special_flags=pygame.BLEND_ADD)
            
            # Draw mission name with glitch effect when selected
            if is_selected and random.random() < 0.1:  # 10% chance of glitch
                mission_text = self.glitch_text(f"{mission['name']}")
            else:
                # Different colors based on mission type
                if mission.get('type') == 'download':
                    color = (100, 200, 255)  # Blue for downloads
                elif mission.get('type') == 'decrypt':
                    color = (255, 100, 200)  # Pink for decryption
                else:
                    color = (0, 255, 0)  # Green for standard missions
                
                if not is_selected:
                    # Fade out unselected missions slightly
                    color = tuple(max(50, c - 50) for c in color)
                
                mission_text = self.font.render(mission['name'], True, color)
            
            # Draw mission text with shadow for better readability
            text_shadow = self.font.render(mission['name'], True, (0, 30, 0))
            self.screen.blit(text_shadow, (85, y_pos + 12))
            self.screen.blit(mission_text, (85, y_pos + 10))
            
            # Draw difficulty indicator
            difficulty = mission.get('difficulty', 'normal').upper()
            diff_color = {
                'EASY': (0, 255, 0),
                'NORMAL': (255, 255, 0),
                'HARD': (255, 100, 0),
                'EXTREME': (255, 0, 0)
            }.get(difficulty, (200, 200, 200))
            
            diff_text = self.font.render(f"[{difficulty}]", True, diff_color)
            self.screen.blit(diff_text, (self.width - 150, y_pos + 10))
        
        # Draw instructions at the bottom
        instructions = [
            "↑/↓: Select Mission",
            "ENTER: Start Mission",
            "M: Toggle Mute",
            "ESC: Quit"
        ]
        
        for i, text in enumerate(instructions):
            text_surface = self.font.render(text, True, (100, 200, 100))
            self.screen.blit(text_surface, (self.width - 250, self.height - 30 - i * 25))
        
        # Apply CRT scanline overlay for retro effect
        self.screen.blit(self.scanline_overlay, (0, 0))

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

    def start_loading(self, mission: Dict[str, Any]):
        """Start loading a mission with appropriate animation."""
        self.state = 'loading'
        self.current_mission = mission
        self.loading_start_time = pygame.time.get_ticks()
        
        # Get the appropriate animation based on mission type
        mission_type = mission.get('type', 'hack')
        self.loading_animation = get_animation_for_mission(
            mission_type, self.screen, self.width, self.height
        )
        self.loading_animation.start()
        
        # Play appropriate sound
        if mission_type == 'download':
            self.play_sound('download')
        elif mission_type == 'decrypt':
            self.play_sound('decrypt')
        else:
            self.play_sound('hack_start')
    
    def complete_loading(self):
        """Complete the loading process and transition to the game."""
        self.state = 'menu'
        self.loading_animation = None
        self.play_sound('confirm')
        
        # Show completion message
        if self.current_mission:
            self.show_mission_start(self.current_mission)
    
    def show_mission_start(self, mission: Dict[str, Any]):
        """Show mission start screen."""
        self.screen.fill((0, 0, 0))
        
        # Display mission info
        title = self.title_font.render(mission['name'].upper(), True, (0, 255, 0))
        title_rect = title.get_rect(centerx=self.width//2, centery=self.height//2 - 50)
        self.screen.blit(title, title_rect)
        
        # Display mission description
        desc = self.large_font.render("MISSION STARTED", True, (0, 200, 0))
        desc_rect = desc.get_rect(centerx=self.width//2, centery=self.height//2 + 20)
        self.screen.blit(desc, desc_rect)
        
        # Display press any key to continue
        prompt = self.font.render("Press any key to continue...", True, (100, 200, 100))
        prompt_rect = prompt.get_rect(centerx=self.width//2, bottom=self.height - 50)
        self.screen.blit(prompt, prompt_rect)
        
        pygame.display.flip()
        
        # Wait for key press
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    waiting = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                        waiting = False
                    else:
                        waiting = False
                        self.play_sound('select')
                        
            self.clock.tick(60)

    def run(self):
        """Main game loop: handle events, update state, draw, control FPS."""
        while self.running:
            self.handle_events()
            
            # Update game state
            current_time = pygame.time.get_ticks()
            
            # Update current state
            if self.state == 'menu':
                self.update_menu(current_time)
            elif self.state == 'loading' and self.loading_animation:
                if self.loading_animation.update():
                    self.complete_loading()
            
            # Draw the current state
            self.screen.fill((0, 0, 0))  # Clear screen
            
            if self.state == 'menu':
                self.draw_mission_list()
            elif self.state == 'loading' and self.loading_animation:
                self.loading_animation.draw()
            
            # Apply scanline overlay for retro effect
            self.screen.blit(self.scanline_overlay, (0, 0))
            
            # Update display
            pygame.display.flip()
            self.clock.tick(60)
            
        # Clean up
        pygame.quit()
        sys.exit()
    
    def update_menu(self, current_time: int):
        """Update menu state (animations, etc.)"""
        # Update flicker effect for selected mission
        self.flicker_timer = (self.flicker_timer + 1) % 30
        
        # Add subtle background animation
        self.draw_background_effects(current_time)
    
    def draw_background_effects(self, current_time: int):
        """Draw subtle background effects for the menu"""
        # Draw a subtle grid
        for x in range(0, self.width, 20):
            alpha = 5 + 5 * math.sin(current_time / 1000 + x / 100)
            pygame.draw.line(self.screen, (0, 20, 0), (x, 0), (x, self.height))
        for y in range(0, self.height, 20):
            alpha = 5 + 5 * math.sin(current_time / 1000 + y / 100)
            pygame.draw.line(self.screen, (0, 20, 0), (0, y), (self.width, y))


if __name__ == "__main__":
    # Create and run the game
    game = GameEngine()
    game.run()

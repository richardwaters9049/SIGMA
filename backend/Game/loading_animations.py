import pygame
import math
import random
from typing import List, Dict, Callable, Any, Tuple

class LoadingAnimation:
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        self.screen = screen
        self.width = width
        self.height = height
        self.progress = 0.0  # 0.0 to 1.0
        self.complete = False
        self.start_time = 0
        self.duration = 3000  # Default duration in ms
    
    def start(self):
        """Start the animation"""
        self.progress = 0.0
        self.complete = False
        self.start_time = pygame.time.get_ticks()
    
    def update(self) -> bool:
        """Update animation progress. Returns True if complete."""
        if self.complete:
            return True
            
        elapsed = pygame.time.get_ticks() - self.start_time
        self.progress = min(1.0, elapsed / self.duration)
        self.complete = self.progress >= 1.0
        return self.complete
    
    def draw(self):
        """Draw the animation. Should be overridden by subclasses."""
        pass


class HackingAnimation(LoadingAnimation):
    """Matrix-style binary rain animation"""
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        super().__init__(screen, width, height)
        self.duration = 3500
        self.chars = "01"
        self.streams: List[Dict] = []
        self.font = pygame.font.SysFont("Courier New", 18, bold=True)
        self.setup_streams()
    
    def setup_streams(self):
        """Initialize the binary rain streams"""
        stream_count = self.width // 20  # One stream every 20 pixels
        for i in range(stream_count):
            x = random.randint(0, self.width)
            speed = random.uniform(2, 5)
            length = random.randint(5, 15)
            self.streams.append({
                'x': x,
                'y': random.randint(-100, 0),
                'speed': speed,
                'chars': [random.choice(self.chars) for _ in range(length)],
                'brightness': [255] * length
            })
    
    def update(self) -> bool:
        super().update()
        
        # Update stream positions
        for stream in self.streams:
            stream['y'] += stream['speed']
            
            # Reset stream if it goes off screen
            if stream['y'] > self.height + len(stream['chars']) * 20:
                stream['y'] = -len(stream['chars']) * 20
                stream['x'] = random.randint(0, self.width)
                
            # Update brightness
            for i in range(len(stream['brightness'])):
                if i == 0:
                    stream['brightness'][i] = 255
                else:
                    stream['brightness'][i] = max(50, stream['brightness'][i-1] - 30)
        
        # Randomly change some characters
        for stream in self.streams:
            if random.random() < 0.1:  # 10% chance to change a character
                idx = random.randint(0, len(stream['chars']) - 1)
                stream['chars'][idx] = random.choice(self.chars)
        
        return self.complete
    
    def draw(self):
        # Draw a semi-transparent black overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))
        
        # Draw the binary rain
        for stream in self.streams:
            for i, (char, brightness) in enumerate(zip(stream['chars'], stream['brightness'])):
                y_pos = stream['y'] + i * 20
                if 0 <= y_pos < self.height:
                    color = (0, min(255, brightness + 100), 0)
                    text = self.font.render(char, True, color)
                    self.screen.blit(text, (stream['x'], y_pos))
        
        # Draw progress bar
        bar_width = self.width - 100
        bar_height = 20
        bar_x = (self.width - bar_width) // 2
        bar_y = self.height - 50
        
        # Background
        pygame.draw.rect(self.screen, (0, 50, 0), (bar_x, bar_y, bar_width, bar_height))
        # Progress
        pygame.draw.rect(self.screen, (0, 255, 0), 
                        (bar_x, bar_y, int(bar_width * self.progress), bar_height))
        # Border
        pygame.draw.rect(self.screen, (0, 200, 0), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Status text
        status_text = "HACKING MAINFRAME..." if not self.complete else "ACCESS GRANTED"
        text = self.font.render(status_text, True, (0, 255, 0))
        text_rect = text.get_rect(centerx=self.width//2, bottom=bar_y - 10)
        self.screen.blit(text, text_rect)


class DownloadAnimation(LoadingAnimation):
    """File download progress animation"""
    def __init__(self, screen: pygame.Surface, width: int, height: int):
        super().__init__(screen, width, height)
        self.duration = 4000
        self.font = pygame.font.SysFont("Courier New", 20, bold=True)
        self.small_font = pygame.font.SysFont("Courier New", 14)
        self.files = [
            "root_access.sh",
            "firewall_bypass.exe",
            "data_packet_encryptor.dll",
            "security_override.ko",
            "crypto_keys.bin"
        ]
        self.current_file = 0
        self.file_progress = 0.0
        self.last_update = 0
    
    def update(self) -> bool:
        super().update()
        
        # Update current file progress
        now = pygame.time.get_ticks()
        if now - self.last_update > 100:  # Update every 100ms
            self.file_progress += random.uniform(0.05, 0.15)
            if self.file_progress >= 1.0:
                self.file_progress = 0.0
                self.current_file = min(self.current_file + 1, len(self.files) - 1)
            self.last_update = now
        
        return self.complete
    
    def draw(self):
        # Background
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 50, 220))  # Dark blue background
        self.screen.blit(overlay, (0, 0))
        
        # Title
        title = self.font.render("SECURE DOWNLOAD IN PROGRESS", True, (100, 200, 255))
        title_rect = title.get_rect(centerx=self.width//2, top=50)
        self.screen.blit(title, title_rect)
        
        # Draw file list
        for i, filename in enumerate(self.files):
            y = 120 + i * 40
            color = (0, 255, 0) if i < self.current_file else (100, 100, 100)
            
            # File name
            text = self.font.render(f"> {filename}", True, color)
            self.screen.blit(text, (100, y))
            
            # Progress indicator
            if i == self.current_file:
                bar_width = 300
                bar_height = 10
                bar_x = self.width - 100 - bar_width
                bar_y = y + 15
                
                # Background
                pygame.draw.rect(self.screen, (0, 50, 0), (bar_x, bar_y, bar_width, bar_height))
                # Progress
                progress_width = int(bar_width * self.file_progress)
                pygame.draw.rect(self.screen, (0, 200, 0), 
                               (bar_x, bar_y, progress_width, bar_height))
                # Border
                pygame.draw.rect(self.screen, (0, 255, 0), 
                               (bar_x, bar_y, bar_width, bar_height), 1)
                
                # Percentage
                percent = int(self.file_progress * 100)
                percent_text = self.small_font.render(f"{percent}%", True, (200, 200, 200))
                self.screen.blit(percent_text, (bar_x + bar_width + 10, bar_y - 3))
            elif i < self.current_file:
                # Show checkmark for completed files
                check = self.small_font.render("[COMPLETE]", True, (0, 255, 0))
                self.screen.blit(check, (self.width - 150, y))
        
        # Overall progress
        overall_text = f"Downloading files: {self.current_file + 1}/{len(self.files)}"
        overall_surf = self.font.render(overall_text, True, (200, 200, 255))
        overall_rect = overall_surf.get_rect(centerx=self.width//2, bottom=self.height - 50)
        self.screen.blit(overall_surf, overall_rect)


def get_animation_for_mission(mission_type: str, screen: pygame.Surface, width: int, height: int) -> LoadingAnimation:
    """Factory function to get the appropriate loading animation for a mission type"""
    animations = {
        'hack': HackingAnimation,
        'download': DownloadAnimation,
        # Add more animation types here
    }
    
    # Default to HackingAnimation if type not found
    animation_type = mission_type.lower() if mission_type.lower() in animations else 'hack'
    return animations[animation_type](screen, width, height)

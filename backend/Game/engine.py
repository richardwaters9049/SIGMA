import pygame
import sys
import random
from Database.mission_store import fetch_all_missions


class MatrixRain:
    """Creates matrix-style vertical rain animation."""

    def __init__(self, screen, width, height, font):
        self.screen = screen
        self.width = width
        self.height = height
        self.font = font

        self.font_width, self.font_height = self.font.size("A")
        self.columns = self.width // self.font_width
        self.drops = [random.randint(-20, 0) for _ in range(self.columns)]
        self.chars = ["0", "1"]

    def draw(self):
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(60)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        for i in range(self.columns):
            char = random.choice(self.chars)
            x = i * self.font_width
            y = self.drops[i] * self.font_height

            char_surface = self.font.render(char, True, (0, 255, 0))
            self.screen.blit(char_surface, (x, y))

            self.drops[i] += 1
            if (
                self.drops[i] * self.font_height > self.height
                and random.random() > 0.975
            ):
                self.drops[i] = random.randint(-20, 0)


class GameEngine:
    """Handles game loop, mission logic, UI rendering."""

    def __init__(self, width=800, height=600):
        pygame.init()
        pygame.font.init()

        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("SIGMA: AI Hacker Protocol")

        self.clock = pygame.time.Clock()
        self.running = True

        self.font = pygame.font.SysFont("Courier New", 20)
        self.big_font = pygame.font.SysFont("Courier New", 36)

        self.missions = fetch_all_missions()
        self.selected_index = 0

        self.state = "menu"  # 'menu', 'loading', 'gameplay', 'result'
        self.loading_counter = 0
        self.matrix_rain = MatrixRain(self.screen, self.width, self.height, self.font)

        self.mission_timer = 0
        self.mission_duration = 300  # 5 seconds (60 FPS)
        self.mission_outcome = None  # "success" or "failure"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == "menu":
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_UP:
                        self.selected_index = (self.selected_index - 1) % len(
                            self.missions
                        )
                    elif event.key == pygame.K_DOWN:
                        self.selected_index = (self.selected_index + 1) % len(
                            self.missions
                        )
                    elif event.key == pygame.K_RETURN:
                        self.state = "loading"
                        self.loading_counter = 0

                elif self.state == "result":
                    if event.key in [pygame.K_RETURN, pygame.K_ESCAPE]:
                        self.state = "menu"

    def update(self):
        if self.state == "loading":
            self.loading_counter += 1
            if self.loading_counter > 180:
                self.state = "gameplay"
                self.mission_timer = 0
                self.mission_outcome = None

        elif self.state == "gameplay":
            self.mission_timer += 1
            if self.mission_timer >= self.mission_duration:
                self.state = "result"
                self.mission_outcome = random.choice(["success", "failure"])

    def draw_menu(self):
        self.screen.fill((0, 0, 0))
        header = self.font.render(
            "Available Missions (Use ↑ ↓, Enter to load)", True, (0, 255, 0)
        )
        self.screen.blit(header, (20, 10))

        y = 60
        for i, mission in enumerate(self.missions):
            text = f"[{mission['difficulty'].upper()}] {mission['name']}"
            if i == self.selected_index:
                pygame.draw.rect(
                    self.screen, (0, 100, 100), pygame.Rect(15, y - 5, 770, 28)
                )
                color = (0, 255, 255)
            else:
                color = (0, 150, 150)
            text_surf = self.font.render(text, True, color)
            self.screen.blit(text_surf, (20, y))
            y += 30

    def draw_loading_screen(self):
        self.matrix_rain.draw()
        dots = (self.loading_counter // 15) % 4
        loading_text = "LOADING MISSION" + ("." * dots)
        text_surf = self.font.render(loading_text, True, (0, 255, 0))
        rect = text_surf.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text_surf, rect)

    def draw_gameplay_screen(self):
        self.screen.fill((0, 0, 0))
        title = self.big_font.render("HACKING IN PROGRESS...", True, (0, 255, 0))
        bar_width = int((self.mission_timer / self.mission_duration) * 600)
        bar_rect = pygame.Rect(100, 300, bar_width, 20)
        pygame.draw.rect(self.screen, (0, 255, 0), bar_rect)
        self.screen.blit(title, (200, 200))

    def draw_result_screen(self):
        self.screen.fill((0, 0, 0))
        result_text = (
            "MISSION SUCCESSFUL"
            if self.mission_outcome == "success"
            else "MISSION FAILED"
        )
        color = (0, 255, 0) if self.mission_outcome == "success" else (255, 0, 0)
        result_surface = self.big_font.render(result_text, True, color)
        self.screen.blit(
            result_surface,
            result_surface.get_rect(center=(self.width // 2, self.height // 2 - 20)),
        )

        prompt = self.font.render("Press ENTER to return to menu", True, (0, 150, 150))
        self.screen.blit(
            prompt, prompt.get_rect(center=(self.width // 2, self.height // 2 + 40))
        )

    def draw(self):
        if self.state == "menu":
            self.draw_menu()
        elif self.state == "loading":
            self.draw_loading_screen()
        elif self.state == "gameplay":
            self.draw_gameplay_screen()
        elif self.state == "result":
            self.draw_result_screen()

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()

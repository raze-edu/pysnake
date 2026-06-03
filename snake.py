import pygame
import random
import sys
import json
import os

# Initialize pygame
pygame.init()

# Game Constants
GRID_SIZE = 20
GRID_COUNT = 30
WINDOW_SIZE = GRID_SIZE * GRID_COUNT  # 600 x 600
FPS = 10

# Colors (Harmonious Cyberpunk / Neon Palette)
COLOR_BG = (15, 17, 26)       # Deep slate blue
COLOR_GRID = (25, 29, 45)     # Subtle grid lines
COLOR_SNAKE_HEAD = (0, 230, 118)  # Bright neon green
COLOR_SNAKE_BODY = (0, 176, 80)   # Darker neon green
COLOR_FOOD = (255, 23, 68)    # Neon pinkish-red
COLOR_TEXT = (236, 239, 241)  # Soft white
COLOR_ACCENT = (0, 176, 255)  # Neon blue (for titles/selection)
COLOR_PARTICLE = (255, 196, 0) # Gold particle glow

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)

# Set up screen
screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Cyber Snake 3000")
clock = pygame.time.Clock()

# Fonts
try:
    font_large = pygame.font.Font(None, 64)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)
except Exception:
    font_large = pygame.font.SysFont("Arial", 64)
    font_medium = pygame.font.SysFont("Arial", 36)
    font_small = pygame.font.SysFont("Arial", 24)

# High Score utility
HIGH_SCORE_FILE = "highscore.json"

def load_high_score():
    if os.path.exists(HIGH_SCORE_FILE):
        try:
            with open(HIGH_SCORE_FILE, "r") as f:
                return json.load(f).get("highscore", 0)
        except Exception:
            return 0
    return 0

def save_high_score(score):
    try:
        with open(HIGH_SCORE_FILE, "w") as f:
            json.dump({"highscore": score}, f)
    except Exception:
        pass

class Particle:
    def __init__(self, pos, color):
        self.x, self.y = pos
        # Random velocity
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.life = random.randint(10, 20)
        self.max_life = self.life
        self.color = color

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.life -= 1

    def draw(self, surface):
        alpha = int((self.life / self.max_life) * 255)
        # Create a tiny surface for transparency
        size = random.randint(2, 5)
        ps = pygame.Surface((size, size), pygame.SRCALPHA)
        ps.fill((*self.color, alpha))
        surface.blit(ps, (int(self.x), int(self.y)))

class Game:
    def __init__(self):
        self.high_score = load_high_score()
        self.reset_game()
        self.state = "START"  # START, PLAYING, PAUSED, GAME_OVER
        self.particles = []

    def reset_game(self):
        # Start in the middle moving right
        self.snake = [
            (GRID_COUNT // 2, GRID_COUNT // 2),
            (GRID_COUNT // 2 - 1, GRID_COUNT // 2),
            (GRID_COUNT // 2 - 2, GRID_COUNT // 2)
        ]
        self.direction = DIR_RIGHT
        self.next_direction = DIR_RIGHT
        self.score = 0
        self.spawn_food()

    def spawn_food(self):
        while True:
            self.food = (random.randint(0, GRID_COUNT - 1), random.randint(0, GRID_COUNT - 1))
            if self.food not in self.snake:
                break

    def spawn_particles(self, cell_pos, color):
        px = cell_pos[0] * GRID_SIZE + GRID_SIZE // 2
        py = cell_pos[1] * GRID_SIZE + GRID_SIZE // 2
        for _ in range(15):
            self.particles.append(Particle((px, py), color))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if self.state == "START":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.state = "PLAYING"
                
                elif self.state == "PLAYING":
                    if event.key in (pygame.K_UP, pygame.K_w) and self.direction != DIR_DOWN:
                        self.next_direction = DIR_UP
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and self.direction != DIR_UP:
                        self.next_direction = DIR_DOWN
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and self.direction != DIR_RIGHT:
                        self.next_direction = DIR_LEFT
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and self.direction != DIR_LEFT:
                        self.next_direction = DIR_RIGHT
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "PAUSED"
                
                elif self.state == "PAUSED":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "PLAYING"
                    elif event.key == pygame.K_q:
                        self.state = "START"
                        self.reset_game()

                elif self.state == "GAME_OVER":
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_SPACE):
                        self.reset_game()
                        self.state = "PLAYING"
                    elif event.key == pygame.K_ESCAPE:
                        self.state = "START"
                        self.reset_game()

    def update(self):
        # Update particles
        for p in self.particles[:]:
            p.update()
            if p.life <= 0:
                self.particles.remove(p)

        if self.state != "PLAYING":
            return

        self.direction = self.next_direction
        head_x, head_y = self.snake[0]
        dir_x, dir_y = self.direction
        new_head = (head_x + dir_x, head_y + dir_y)

        # Check wall collision
        if new_head[0] < 0 or new_head[0] >= GRID_COUNT or new_head[1] < 0 or new_head[1] >= GRID_COUNT:
            self.game_over()
            return

        # Check self collision
        if new_head in self.snake:
            self.game_over()
            return

        # Insert new head
        self.snake.insert(0, new_head)

        # Check food collision
        if new_head == self.food:
            self.score += 10
            self.spawn_particles(self.food, COLOR_FOOD)
            self.spawn_food()
        else:
            # Pop tail
            self.snake.pop()

    def game_over(self):
        self.state = "GAME_OVER"
        self.spawn_particles(self.snake[0], COLOR_SNAKE_HEAD)
        if self.score > self.high_score:
            self.high_score = self.score
            save_high_score(self.high_score)

    def draw_grid(self):
        for x in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, WINDOW_SIZE))
        for y in range(0, WINDOW_SIZE, GRID_SIZE):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (WINDOW_SIZE, y))

    def draw(self):
        screen.fill(COLOR_BG)
        self.draw_grid()

        # Draw Snake
        for index, segment in enumerate(self.snake):
            rect = pygame.Rect(segment[0] * GRID_SIZE + 1, segment[1] * GRID_SIZE + 1, GRID_SIZE - 2, GRID_SIZE - 2)
            color = COLOR_SNAKE_HEAD if index == 0 else COLOR_SNAKE_BODY
            pygame.draw.rect(screen, color, rect, border_radius=4)
            # Add small eyes/detail to snake head
            if index == 0:
                eye_size = 3
                if self.direction in (DIR_RIGHT, DIR_LEFT):
                    pygame.draw.circle(screen, COLOR_BG, (rect.centerx, rect.top + 5), eye_size)
                    pygame.draw.circle(screen, COLOR_BG, (rect.centerx, rect.bottom - 5), eye_size)
                else:
                    pygame.draw.circle(screen, COLOR_BG, (rect.left + 5, rect.centery), eye_size)
                    pygame.draw.circle(screen, COLOR_BG, (rect.right - 5, rect.centery), eye_size)

        # Draw Food
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE + 2, self.food[1] * GRID_SIZE + 2, GRID_SIZE - 4, GRID_SIZE - 4)
        pygame.draw.rect(screen, COLOR_FOOD, food_rect, border_radius=8)

        # Draw Particles
        for p in self.particles:
            p.draw(screen)

        # UI overlays
        if self.state == "START":
            self.draw_overlay("CYBER SNAKE", "Press ENTER or SPACE to start", f"High Score: {self.high_score}")
        elif self.state == "PLAYING":
            # Simple HUD
            score_text = font_medium.render(f"Score: {self.score}", True, COLOR_TEXT)
            hi_text = font_small.render(f"High: {self.high_score}", True, COLOR_ACCENT)
            screen.blit(score_text, (20, 20))
            screen.blit(hi_text, (20, 55))
        elif self.state == "PAUSED":
            self.draw_overlay("PAUSED", "Press ESC to resume", "Press Q to exit to main menu")
        elif self.state == "GAME_OVER":
            self.draw_overlay("GAME OVER", f"Your Score: {self.score}", "Press ENTER to retry, ESC for Menu")

        pygame.display.flip()

    def draw_overlay(self, title, subtitle1, subtitle2):
        # Semi-transparent overlay background
        overlay = pygame.Surface((WINDOW_SIZE, WINDOW_SIZE), pygame.SRCALPHA)
        overlay.fill((10, 12, 20, 220)) # Translucent dark overlay
        screen.blit(overlay, (0, 0))

        # Render Text
        t_surface = font_large.render(title, True, COLOR_ACCENT)
        s1_surface = font_medium.render(subtitle1, True, COLOR_TEXT)
        s2_surface = font_small.render(subtitle2, True, COLOR_TEXT)

        # Center alignments
        screen.blit(t_surface, (WINDOW_SIZE // 2 - t_surface.get_width() // 2, WINDOW_SIZE // 2 - 80))
        screen.blit(s1_surface, (WINDOW_SIZE // 2 - s1_surface.get_width() // 2, WINDOW_SIZE // 2 + 10))
        screen.blit(s2_surface, (WINDOW_SIZE // 2 - s2_surface.get_width() // 2, WINDOW_SIZE // 2 + 50))

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()

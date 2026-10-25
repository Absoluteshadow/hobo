import pygame
import sys

# Initialize Pygame
pygame.init()

# Screen Dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Hobo Simulator - 2D Prototype")

# Clock & FPS
clock = pygame.time.Clock()
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 50)
GREEN = (46, 204, 113)
BLUE = (52, 152, 219)
RED = (231, 76, 60)
YELLOW = (241, 196, 15)

# Physics Constant (Gravity = 10)
GRAVITY = 10

# Fonts
font = pygame.font.SysFont(None, 24)
large_font = pygame.font.SysFont(None, 32)


class Player:
    """Player class handling movement, gravity, and floor collision."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.color = BLUE
        self.vel_x = 0
        self.vel_y = 0
        self.speed = 5
        self.on_ground = False

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.vel_x = -self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:  # Fixed to uppercase K_RIGHT
            self.vel_x = self.speed

    def update(self, floor_y):
        # Apply gravity (scaled down slightly for smooth frame-rate integration)
        self.vel_y += GRAVITY * 0.1
        
        # Update positions
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Floor collision check
        if self.rect.bottom >= floor_y:
            self.rect.bottom = floor_y
            self.vel_y = 0
            self.on_ground = True
        else:
            self.on_ground = False

        # Screen boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Dumpster:
    """Interactable object class that triggers text menus."""
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 60, 50)
        self.color = DARK_GRAY
        self.interact_radius = 40

    def is_in_range(self, player_rect):
        expanded_rect = self.rect.inflate(self.interact_radius, self.interact_radius)
        return expanded_rect.colliderect(player_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        # Draw lid detail
        pygame.draw.rect(surface, GRAY, (self.rect.x - 5, self.rect.y - 8, self.rect.width + 10, 8))


class NPC:
    """NPC class for dialogues and basic trade/interactions."""
    def __init__(self, x, y, name):
        self.rect = pygame.Rect(x, y, 30, 50)
        self.color = RED
        self.name = name
        self.interact_radius = 40

    def is_in_range(self, player_rect):
        expanded_rect = self.rect.inflate(self.interact_radius, self.interact_radius)
        return expanded_rect.colliderect(player_rect)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)


class Game:
    """Main game class managing states, UI, and event loops."""
    def __init__(self):
        self.floor_y = SCREEN_HEIGHT - 100
        self.player = Player(100, self.floor_y - 50)
        self.dumpster = Dumpster(400, self.floor_y - 50)
        self.npc = NPC(600, self.floor_y - 50, "Passing Citizen")

        # Game State Variables
        self.money = 5
        self.reputation = 50
        
        # Menu States: None, "DUMPSTER_MENU", "NPC_MENU"
        self.active_menu = None

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.render()
            clock.tick(FPS)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                # Menu choices handling
                if self.active_menu == "DUMPSTER_MENU":
                    if event.key == pygame.K_1:
                        # Search action
                        self.money += 2
                        self.reputation -= 2
                        self.active_menu = None
                    elif event.key == pygame.K_2:
                        # Leave action
                        self.active_menu = None

                elif self.active_menu == "NPC_MENU":
                    if event.key == pygame.K_1:
                        # Beg for money
                        self.money += 1
                        self.reputation -= 5
                        self.active_menu = None
                    elif event.key == pygame.K_2:
                        # Chat peacefully
                        self.reputation += 2
                        self.active_menu = None
                    elif event.key == pygame.K_3:
                        # Leave action
                        self.active_menu = None

                else:
                    # Overworld actions
                    if event.key == pygame.K_e:
                        if self.dumpster.is_in_range(self.player.rect):
                            self.active_menu = "DUMPSTER_MENU"
                        elif self.npc.is_in_range(self.player.rect):
                            self.active_menu = "NPC_MENU"

    def update(self):
        if self.active_menu is None:
            self.player.handle_input()
            self.player.update(self.floor_y)

    def render(self):
        screen.fill(WHITE)

        # Draw Floor
        pygame.draw.rect(screen, GRAY, (0, self.floor_y, SCREEN_WIDTH, SCREEN_HEIGHT - self.floor_y))

        # Draw Entities
        self.dumpster.draw(screen)
        self.npc.draw(screen)
        self.player.draw(screen)

        # Draw HUD (Money & Reputation)
        money_text = font.render(f"Money: ${self.money}", True, BLACK)
        rep_text = font.render(f"Reputation: {self.reputation}", True, BLACK)
        screen.blit(money_text, (20, 20))
        screen.blit(rep_text, (20, 50))

        # Draw Interaction Prompts (Overworld)
        if self.active_menu is None:
            if self.dumpster.is_in_range(self.player.rect):
                prompt = font.render("Press 'E' to search Dumpster", True, BLACK)
                screen.blit(prompt, (self.dumpster.rect.x - 40, self.dumpster.rect.y - 30))
            elif self.npc.is_in_range(self.player.rect):
                prompt = font.render(f"Press 'E' to talk to {self.npc.name}", True, BLACK)
                screen.blit(prompt, (self.npc.rect.x - 40, self.npc.rect.y - 30))

        # Draw Interactive Menus (UI Overlay)
        if self.active_menu == "DUMPSTER_MENU":
            self.draw_menu_box("Dumpster Diving", ["[1] Search through trash (+$2, -2 Rep)", "[2] Leave"])
        elif self.active_menu == "NPC_MENU":
            self.draw_menu_box("Interaction", ["[1] Beg for spare change (+$1, -5 Rep)", "[2] Friendly conversation (+2 Rep)", "[3] Walk away"])

        pygame.display.flip()

    def draw_menu_box(self, title, options):
        # Semi-transparent menu box overlay background
        box_rect = pygame.Rect(200, 150, 400, 300)
        pygame.draw.rect(screen, BLACK, box_rect)
        pygame.draw.rect(screen, WHITE, box_rect, 3)

        # Title
        title_surface = large_font.render(title, True, YELLOW)
        screen.blit(title_surface, (box_rect.x + 20, box_rect.y + 20))

        # Options
        for i, option in enumerate(options):
            opt_surface = font.render(option, True, WHITE)
            screen.blit(opt_surface, (box_rect.x + 20, box_rect.y + 80 + (i * 40)))


if __name__ == "__main__":
    game = Game()
    game.run()
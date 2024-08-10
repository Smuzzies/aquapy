import random
import pygame
import sys
import os
import requests
from io import BytesIO

# Initialize Pygame
pygame.init()

# Define aquarium dimensions
WIDTH = 1280
HEIGHT = 768

# Enable Windows-level draggable window
if os.name == 'nt':
    import ctypes
    ctypes.windll.user32.SetProcessDPIAware()

# Define colors
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
DARK_GRAY = (20, 20, 20)  # Very dark gray for background
LIGHT_GRAY = (40, 40, 40)  # Light gray for the title bar
PALETTES = {
    'ocean': [(0, 119, 190), (0, 180, 216), (144, 224, 239), (202, 240, 248)],
    'coral': [(255, 190, 152), (255, 166, 158), (255, 138, 138), (255, 102, 99)],
    'tropical': [(255, 209, 102), (255, 140, 102), (255, 98, 98), (255, 69, 69)],
    'deep_sea': [(4, 41, 58), (6, 70, 99), (8, 100, 139), (11, 131, 180)],
    'pastel': [(255, 179, 186), (255, 223, 186), (255, 255, 186), (186, 255, 201)],
    'neon': [(255, 16, 240), (0, 255, 255), (0, 255, 0), (255, 255, 0)],
    'autumn': [(165, 42, 42), (204, 85, 0), (255, 140, 0), (255, 215, 0)],
    'spring': [(0, 255, 127), (50, 205, 50), (154, 205, 50), (255, 215, 0)],
    'monochrome': [(255, 255, 255), (200, 200, 200), (150, 150, 150), (100, 100, 100)],
    'vibrant': [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)],
    # New palettes with pinks and purples
    'berry': [(142, 68, 173), (155, 89, 182), (200, 102, 204), (231, 60, 192)],
    'sunset': [(255, 107, 107), (255, 159, 67), (255, 205, 86), (250, 177, 160)],
    'lavender': [(230, 230, 250), (216, 191, 216), (221, 160, 221), (238, 130, 238)],
    'neon_nights': [(255, 0, 255), (0, 255, 255), (255, 0, 128), (128, 0, 255)],
    'cotton_candy': [(255, 183, 213), (255, 219, 255), (189, 224, 254), (162, 210, 255)]
}

SEAWEED_COLORS = [
    (0, 100, 0),    # Dark Green
    (0, 128, 0),    # Green
    (34, 139, 34),  # Forest Green
    (0, 255, 0),    # Lime Green
    (50, 205, 50),  # Lime
    (144, 238, 144) # Light Green
]

# Define ASCII characters for different elements
FISH_RIGHT = ['><>', '><))>', '><)))°)', '>##°)', '>=°>', '>-=°>', '>|||°>', '><(((*>']
FISH_LEFT = ['<><', '<))><', '(°(((><', '(°##<', '<°=<', '<°=-<', '<°|||<', '<*)))><']
BUBBLES = ['o', 'O', '°', '.']
SEAWEED = ['((', '))', '&', '@']
CASTLE = [
    '                                  i~~~',
    '                                 / \\',
    '                                /   \\',
    '        ASCII Aquarium         <_____>',
    '    inspired by @oric_rax    _ _|_o_|_ _',
    '                             ]=I=I=I=I=[',
    '       Y Y Y Y Y Y Y Y        \\-|-|-|-/',
    '       ]=I=I=I=I=I=I=[   |  <===========>  Y Y Y Y Y Y Y',
    '        \\-\\--|-|--/-/    |  || []   [] |   ]=I=I=I=I=I=[',
    '         | ~    #  | _ _ |_ ||_ _ _ _ _|_ _ \\--|-|-|--/',
    '         |    -    |=I=I=I=I=I=I=I=I=I=I=I=I=|       |',
    '         |         |-=-=-=-=-=-=-=-=-=-=-=-=-| #   []|',
    '         |  #   [] |          ___            |       |',
    '         |         |    #    /   \\  #   #    |   #   |',
    '         |    #  - |  #    #|  ^  |    #     |  -  # |',
    '       _/|         |\\_   #  |     |      # _/|       |\\_'
]

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.NOFRAME)
pygame.display.set_caption("ASCII Aquarium")

# Set up the font
font = pygame.font.SysFont('consolas', 18)

try:
    pygame.mixer.music.load('aqua.mp3')
    pygame.mixer.music.play(-1)  # -1 means loop indefinitely
except pygame.error:
    print("Could not load or play the background music.")

# Variables for dragging
dragging = False
offset_x, offset_y = 0, 0

class AquariumObject:
    def __init__(self, x, y, char):
        self.x = x
        self.y = y
        self.char = char

    def move(self):
        pass

    def draw(self, surface, offset_x, offset_y):
        text = font.render(self.char, True, WHITE)
        surface.blit(text, ((self.x + offset_x) * 20, (self.y + offset_y) * 20))

class Fish(AquariumObject):
    def __init__(self, x, y):
        self.direction = random.choice([-1, 1])
        char = random.choice(FISH_RIGHT if self.direction == 1 else FISH_LEFT)
        super().__init__(x, y, char)
        self.color_mode = random.choice(['static', 'gradient', 'multi'])
        self.palette = random.choice(list(PALETTES.values()))
        self.colors = self.generate_colors()
        self.speed = random.uniform(0.01, 0.1)  # Random speed for each fish

    def generate_colors(self):
        if self.color_mode == 'static':
            return [random.choice(self.palette)] * len(self.char)
        elif self.color_mode == 'gradient':
            return [self.palette[i % len(self.palette)] for i in range(len(self.char))]
        else:  # multi
            return [random.choice(self.palette) for _ in range(len(self.char))]

    def move(self):
        self.x += self.direction * self.speed
        if self.x <= 0 or self.x >= WIDTH // 20 - len(self.char):
            self.direction *= -1
            char = random.choice(FISH_RIGHT if self.direction == 1 else FISH_LEFT)
            self.char = char
            self.colors = self.generate_colors()  # Regenerate colors when changing direction
            self.x = max(0, min(self.x, WIDTH // 20 - len(self.char)))

    def draw(self, surface, offset_x, offset_y):
        x_pos = int((self.x + offset_x) * 20)
        y_pos = int((self.y + offset_y) * 20)
        for char, color in zip(self.char, self.colors):
            text = font.render(char, True, color)
            surface.blit(text, (x_pos, y_pos))
            x_pos += text.get_width()

class Bubble(AquariumObject):
    def __init__(self, x, y):
        super().__init__(x, y, random.choice(BUBBLES))
        self.speed = random.uniform(0.025, 0.1)  # Varying speeds for bubbles

    def move(self):
        self.y -= self.speed
        if self.y < -1:
            self.y = HEIGHT // 20  # Reset to bottom when it reaches the top
            self.x = random.randint(0, WIDTH // 20 - 1)  # Random horizontal position

class Seaweed(AquariumObject):
    def __init__(self, x):
        super().__init__(x, HEIGHT // 20 - 1, random.choice(SEAWEED))
        self.height = random.randint(3, 20)  # Increased height range
        self.sway_offset = 0
        self.sway_direction = random.choice([-1, 1])
        self.color = random.choice(SEAWEED_COLORS)  # Randomly choose a green shade

    def move(self):
        self.sway_offset += 0.01 * self.sway_direction  # Slower swaying
        if abs(self.sway_offset) > 1:
            self.sway_direction *= -1

    def draw(self, surface, offset_x, offset_y):
        for i in range(self.height):
            text = font.render(self.char, True, self.color)
            x_pos = ((self.x + offset_x) * 20) + (self.sway_offset * i)
            y_pos = ((self.y - i) + offset_y) * 20
            surface.blit(text, (x_pos, y_pos))

class CloseButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 30, 0, 30, 30)
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        close_text = self.font.render('x', True, WHITE)
        surface.blit(close_text, (self.rect.x + 10, self.rect.y + 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                pygame.quit()
                sys.exit()

class Aquarium:
    def __init__(self):
        self.objects = []
        self.add_fish(25)
        self.add_bubbles(180)
        self.add_seaweed(40)  # Increased number of seaweed
        self.add_castle()
        self.aquarium_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        self.background = self.load_background("https://images.unsplash.com/photo-1465634836201-1d5651b9b6d6?q=80&w=2148&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", 0.2)

    def load_background(self, url, opacity):
        try:
            response = requests.get(url)
            image = pygame.image.load(BytesIO(response.content))
            image = pygame.transform.scale(image, (WIDTH, HEIGHT))
            image.set_alpha(int(255 * opacity))
            return image
        except:
            print("Failed to load background image.")
            return None

    def add_fish(self, count):
        for _ in range(count):
            self.objects.append(Fish(random.randint(0, WIDTH // 20 - 1), random.randint(0, HEIGHT // 20 - 1)))

    def add_bubbles(self, count):
        for _ in range(count):
            self.objects.append(Bubble(random.randint(0, WIDTH // 20 - 1), random.randint(0, HEIGHT // 20 - 1)))

    def add_seaweed(self, count):
        for _ in range(count):
            self.objects.append(Seaweed(random.randint(0, WIDTH // 20 - 1)))

    def add_castle(self):
        castle_width = max(len(line) for line in CASTLE)
        castle_height = len(CASTLE)
        
        castle_x = (WIDTH // 20) - castle_width
        castle_y = (HEIGHT // 20) - castle_height

        for i, line in enumerate(CASTLE):
            self.objects.append(AquariumObject(castle_x, castle_y + i, line))

    def update(self):
        for obj in self.objects:
            obj.move()

    def draw(self, surface, offset_x, offset_y):
        if self.background:
            surface.blit(self.background, (0, 0))
        else:
            surface.fill(DARK_GRAY)
        
        for obj in self.objects:
            obj.draw(surface, offset_x, offset_y)

def main():
    aquarium = Aquarium()
    close_button = CloseButton()
    clock = pygame.time.Clock()
    offset_x, offset_y = 0, 0
    dragging_aquarium = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    dragging_aquarium = True
                    mouse_x, mouse_y = event.pos
                    drag_start_x, drag_start_y = offset_x, offset_y
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    dragging_aquarium = False
            elif event.type == pygame.MOUSEMOTION:
                if dragging_aquarium:
                    mouse_x, mouse_y = event.pos
                    offset_x = drag_start_x + (mouse_x - event.pos[0]) // 20
                    offset_y = drag_start_y + (mouse_y - event.pos[1]) // 20
            
            close_button.handle_event(event)

        aquarium.update()
        screen.fill(DARK_GRAY)
        aquarium.draw(screen, offset_x, offset_y)
        close_button.draw(screen)
        pygame.display.flip()
        clock.tick(60)  # 30 FPS for smooth animation

if __name__ == "__main__":
    main()

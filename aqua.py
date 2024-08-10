import random
import pygame
import sys
import os

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
FISH_COLORS = [(255, 0, 0), (255, 255, 0), (0, 0, 255), (255, 0, 255), (0, 255, 255)]
DARK_GRAY = (20, 20, 20)  # Very dark gray for background
LIGHT_GRAY = (100, 100, 100)  # Light gray for the title bar

# Define ASCII characters for different elements
FISH_RIGHT = ['><>', '><))>', '><)))o', '>=~~~)', '>==>', '>-=>', '>|||>', '><(((*>']
FISH_LEFT = ['<><', '<))><', 'o(((><', '(~~~=<', '<==<', '<=-<', '<|||<', '<*)))><']
BUBBLES = ['o', 'O', '°', '.']
SEAWEED = ['((', '))', '~']
CASTLE = [
    '                                  i~~~',
    '                                 / \\',
    '                                /   \\',
    '        ASCII Aquarium         <_____>',
    '    inspired by @oric_rax    _ _|_o_|_ _',
    '                             ]=I=I=I=I=[',
    '       Y Y Y Y Y Y Y Y        \\-|-|-|-/',
    '       ]=I=I=I=I=I=I=[   |  <===========> Y Y Y Y Y Y Y',
    '        \\-\\--|-|--/-/  |  || []   [] |  ]=I=I=I=I=I=[',
    '         | ~    #  | _ _ |_ ||_ _ _ _ _|_ _\\--|-|-|--/',
    '         |    -    |=I=I=I=I=I=I=I=I=I=I=I=I=|       |',
    '         |         |-=-=-=-=-=-=-=-=-=-=-=-=-| #   []|',
    '         |  #   [] |          ___            |       |',
    '         |         |    #   /   \\  #   #    |   #   |',
    '         |    #  - |  #    #|  ^  |    #     |  -  # |',
    '       _/|         |\\_  #  |     |      # _/|       |\\_'
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
        self.color = self.random_bright_color()

    def random_bright_color(self):
        # Generate a random bright color
        h = random.random()  # Random hue
        s = 0.8 + random.random() * 0.2  # High saturation
        v = 0.8 + random.random() * 0.2  # High value (brightness)
        r, g, b = self.hsv_to_rgb(h, s, v)
        return (int(r * 255), int(g * 255), int(b * 255))

    def hsv_to_rgb(self, h, s, v):
        if s == 0.0:
            return v, v, v
        i = int(h * 6.0)
        f = (h * 6.0) - i
        p = v * (1.0 - s)
        q = v * (1.0 - s * f)
        t = v * (1.0 - s * (1.0 - f))
        i = i % 6
        if i == 0:
            return v, t, p
        if i == 1:
            return q, v, p
        if i == 2:
            return p, v, t
        if i == 3:
            return p, q, v
        if i == 4:
            return t, p, v
        if i == 5:
            return v, p, q

    def move(self):
        self.x += self.direction * 0.2  # Even slower movement
        if self.x <= 0 or self.x >= WIDTH // 20 - len(self.char):
            self.direction *= -1
            self.char = random.choice(FISH_RIGHT if self.direction == 1 else FISH_LEFT)
            # Adjust position to prevent sticking at the edge
            self.x = max(0, min(self.x, WIDTH // 20 - len(self.char)))

    def draw(self, surface, offset_x, offset_y):
        text = font.render(self.char, True, self.color)
        surface.blit(text, ((self.x + offset_x) * 20, (self.y + offset_y) * 20))

class Bubble(AquariumObject):
    def __init__(self, x, y):
        super().__init__(x, y, random.choice(BUBBLES))
        self.speed = random.uniform(0.1, 0.3)  # Varying speeds for bubbles

    def move(self):
        self.y -= self.speed
        if self.y < -1:
            self.y = HEIGHT // 20  # Reset to bottom when it reaches the top
            self.x = random.randint(0, WIDTH // 20 - 1)  # Random horizontal position

class Seaweed(AquariumObject):
    def __init__(self, x):
        super().__init__(x, HEIGHT // 20 - 1, random.choice(SEAWEED))
        self.height = random.randint(5, 17)  # Increased height range
        self.sway_offset = 0
        self.sway_direction = random.choice([-1, 1])

    def move(self):
        self.sway_offset += 0.05 * self.sway_direction  # Slower swaying
        if abs(self.sway_offset) > 1:
            self.sway_direction *= -1

    def draw(self, surface, offset_x, offset_y):
        for i in range(self.height):
            text = font.render(self.char, True, GREEN)
            # Reverse the sway effect: multiply by i instead of (self.height - i)
            x_pos = ((self.x + offset_x) * 20) + (self.sway_offset * i)
            y_pos = ((self.y - i) + offset_y) * 20
            surface.blit(text, (x_pos, y_pos))

class CloseButton:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH - 30, 0, 30, 30)
        self.font = pygame.font.Font(None, 24)
        
    def draw(self, surface):
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect)
        close_text = self.font.render('X', True, WHITE)
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
        self.add_bubbles(80)
        self.add_seaweed(20)  # Increased number of seaweed
        self.add_castle()
        self.aquarium_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)

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
        self.aquarium_surface.fill(DARK_GRAY)
        
        for obj in self.objects:
            obj.draw(self.aquarium_surface, offset_x, offset_y)
        
        surface.blit(self.aquarium_surface, (0, 0))

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
        clock.tick(30)  # 30 FPS for smooth animation

if __name__ == "__main__":
    main()

import pygame
import sys

# ---------- Configuration ----------
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
TOOLBAR_HEIGHT = 50
BUTTON_PADDING = 10
BUTTON_WIDTH = 80
BUTTON_HEIGHT = TOOLBAR_HEIGHT - 2 * BUTTON_PADDING
CANVAS_RECT = pygame.Rect(0, TOOLBAR_HEIGHT, WINDOW_WIDTH, WINDOW_HEIGHT - TOOLBAR_HEIGHT)

# Define some basic colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY  = (200, 200, 200)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)

# List of colors for color picker dropdown (simple cycle)
COLOR_LIST = [BLACK, RED, GREEN, BLUE]

# ---------- Button Class ----------
class Button:
    def __init__(self, x, y, w, h, text, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.action = action  # function to call when clicked
    def draw(self, surf, font):
        pygame.draw.rect(surf, GRAY, self.rect)
        label = font.render(self.text, True, BLACK)
        label_rect = label.get_rect(center=self.rect.center)
        surf.blit(label, label_rect)
    def click(self):
        self.action()

# ---------- Painter App ----------
class Painter:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simple Painter (GUI Tools)")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Canvas as a surface we can clear/redraw
        self.canvas = pygame.Surface(CANVAS_RECT.size)
        self.canvas.fill(WHITE)

        # Tool state
        self.current_tool = 'brush'
        self.brush_color = BLACK
        self.brush_size = 5

        # Build toolbar
        self.buttons = []
        self._create_buttons()

    def _create_buttons(self):
        x = BUTTON_PADDING
        # Brush
        self.buttons.append(Button(x, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT, 'Brush', self.use_brush))
        x += BUTTON_WIDTH + BUTTON_PADDING
        # Eraser
        self.buttons.append(Button(x, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT, 'Eraser', self.use_eraser))
        x += BUTTON_WIDTH + BUTTON_PADDING
        # Color
        self.buttons.append(Button(x, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT, 'Color', self.change_color))
        x += BUTTON_WIDTH + BUTTON_PADDING
        # Clear
        self.buttons.append(Button(x, BUTTON_PADDING, BUTTON_WIDTH, BUTTON_HEIGHT, 'Clear', self.clear_canvas))

    # Tool actions
    def use_brush(self):
        self.current_tool = 'brush'
    def use_eraser(self):
        self.current_tool = 'eraser'
    def change_color(self):
        # cycle through COLOR_LIST
        idx = COLOR_LIST.index(self.brush_color)
        self.brush_color = COLOR_LIST[(idx + 1) % len(COLOR_LIST)]
    def clear_canvas(self):
        self.canvas.fill(WHITE)

    def run(self):
        drawing = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.pos[1] < TOOLBAR_HEIGHT:
                        # Clicked in toolbar
                        for btn in self.buttons:
                            if btn.rect.collidepoint(event.pos):
                                btn.click()
                                break
                    else:
                        drawing = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    drawing = False

            if drawing:
                mx, my = pygame.mouse.get_pos()
                if CANVAS_RECT.collidepoint((mx, my)):
                    cx, cy = mx, my - TOOLBAR_HEIGHT
                    if self.current_tool == 'brush':
                        pygame.draw.circle(self.canvas, self.brush_color, (cx, cy), self.brush_size)
                    elif self.current_tool == 'eraser':
                        pygame.draw.circle(self.canvas, WHITE, (cx, cy), self.brush_size)

            # Draw everything
            self.screen.fill(WHITE)
            # Toolbar background
            pygame.draw.rect(self.screen, (230,230,230), (0, 0, WINDOW_WIDTH, TOOLBAR_HEIGHT))
            # Buttons
            for btn in self.buttons:
                btn.draw(self.screen, self.font)

            # Show current color and size
            info = self.font.render(f"Tool: {self.current_tool} | Color: {self.brush_color} | Size: {self.brush_size}", True, BLACK)
            self.screen.blit(info, (WINDOW_WIDTH - 300, 15))

            # Blit canvas
            self.screen.blit(self.canvas, (0, TOOLBAR_HEIGHT))

            pygame.display.flip()
            self.clock.tick(60)

if __name__ == '__main__':
    app = Painter()
    app.run()
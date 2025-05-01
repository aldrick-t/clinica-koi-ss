import pygame
import sys
import threading

# ---------- Configuration ----------
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
CANVAS_BG = (255, 255, 255)

# ---------- Painter Class ----------
class Painter:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Simple Painter (Console-Controlled)")
        self.canvas = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.canvas.fill(CANVAS_BG)
        self.clock = pygame.time.Clock()

        # Default tool settings
        self.brush_color = (0, 0, 0)
        self.brush_size = 5
        self.tool = 'brush'  # can also be 'eraser'

    def draw_loop(self):
        drawing = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    drawing = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    drawing = False

            if drawing:
                x, y = pygame.mouse.get_pos()
                if self.tool == 'brush':
                    pygame.draw.circle(self.canvas, self.brush_color, (x, y), self.brush_size)
                elif self.tool == 'eraser':
                    pygame.draw.circle(self.canvas, CANVAS_BG, (x, y), self.brush_size)

            # Display canvas
            self.screen.blit(self.canvas, (0, 0))
            pygame.display.flip()
            self.clock.tick(60)

    def repl(self):
        banner = (
            "\nConsole commands:\n"
            "  p.tool = 'brush' or 'eraser'\n"
            "  p.brush_color = (R,G,B)\n"
            "  p.brush_size = int\n"
            "  p.canvas.fill((R,G,B))  # to clear/change bg\n"
            "  help()  # show this message\n"
        )
        print(banner)
        local_vars = {'p': self, 'help': lambda: print(banner)}
        while True:
            try:
                cmd = input(">>> ")
                if cmd.strip() == '':
                    continue
                # Execute in the REPL namespace
                exec(cmd, {}, local_vars)
            except Exception as e:
                print(f"Error: {e}")

if __name__ == '__main__':
    p = Painter()
    # Start the console thread
    t = threading.Thread(target=p.repl, daemon=True)
    t.start()
    # Run the drawing loop (main thread)
    p.draw_loop()
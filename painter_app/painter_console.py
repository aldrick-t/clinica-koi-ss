import pygame
import sys
import threading

# ---------- Configuración ----------
ANCHO_VENTANA, ALTO_VENTANA = 800, 600
FONDO_LIENZO = (255, 255, 255)

# ---------- Painter Class ----------
class Pintor:
    def __init__(self):
        pygame.init()
        self.pantalla = pygame.display.set_mode((ANCHO_VENTANA, ALTO_VENTANA))
        pygame.display.set_caption("Pintor Simple (Control por Consola)")
        self.lienzo = pygame.Surface((ANCHO_VENTANA, ALTO_VENTANA))
        self.lienzo.fill(FONDO_LIENZO)
        self.reloj = pygame.time.Clock()

        # Ajustes de herramienta predeterminados
        self.color_pincel = (0, 0, 0)
        self.tamano_pincel = 5
        self.herramienta = 'pincel'  # puede ser también 'borrador'

    def bucle_dibujo(self):
        dibujando = False
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    dibujando = True
                elif event.type == pygame.MOUSEBUTTONUP:
                    dibujando = False

            if dibujando:
                x, y = pygame.mouse.get_pos()
                if self.herramienta == 'pincel':
                    pygame.draw.circle(self.lienzo, self.color_pincel, (x, y), self.tamano_pincel)
                elif self.herramienta == 'borrador':
                    pygame.draw.circle(self.lienzo, FONDO_LIENZO, (x, y), self.tamano_pincel)

            # Display canvas
            self.pantalla.blit(self.lienzo, (0, 0))
            pygame.display.flip()
            self.reloj.tick(60)

    def consola(self):
        banner = (
            "\nComandos de consola:\n"
            "  p.herramienta = 'pincel' o 'borrador'\n"
            "  p.color_pincel = (R,G,B)\n"
            "  p.tamano_pincel = int\n"
            "  p.lienzo.fill((R,G,B))  # para limpiar/cambiar fondo\n"
            "  help()  # muestra este mensaje\n"
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
    p = Pintor()
    # Start the console thread
    t = threading.Thread(target=p.consola, daemon=True)
    t.start()
    # Run the drawing loop (main thread)
    p.bucle_dibujo()
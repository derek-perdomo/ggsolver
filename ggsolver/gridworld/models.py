import pygame
from typing import Union
from ggsolver.graph import *
from dataclasses import dataclass
from ggsolver.util import ColoredMsg


@dataclass
class LineStyle:
    """
    :param line_width: (int) Line width of borders.
    :param line_color: (int) (3-tuple of int) (R, G, B), each value between [0, 255]
    :param line_style: (str) Line style of borders.
        Currently, only "solid" is supported. Later, we will support "dashed".
    """
    line_width: int = 1
    line_style: str = "solid"
    line_color: tuple = (0, 0, 0)


class SM:
    def __init__(self, graph: Graph):
        self._graph = graph
        self._curr_state = None
        self._states_history = []
        self._action_history = []
        self._curr_step = 0
        self._len_history = float("inf")

    # TODO. Add methods for initialize, delta etc.
    #  Unclear whether inputs should be nodes or states?


DEFAULT_CELL_SIZE = (50, 50)
DEFAULT_BG_COLOR = (255, 255, 255)
DEFAULT_LINE_STYLE = LineStyle(line_width=3, line_style="solid", line_color=(0, 0, 0))
MOUSE_HOVER_ANIM_COLOR = (255, 222, 173)


class GWSim:
    def __init__(self, dim, sm,
                 window_size: Union[str, tuple[int, int]] = "auto",
                 cell_size: Union[str, tuple[int, int]] = "auto",
                 bg_color=DEFAULT_BG_COLOR,
                 mouse_hover_anim_color=MOUSE_HOVER_ANIM_COLOR,
                 grid_line_style=DEFAULT_LINE_STYLE,
                 mode=None,
                 fps=2,
                 show_help=True,
                 show_msg_box=False,
                 show_grid_lines=True,
                 show_mouse_hover_animation=True,
                 enable_sound=False,
                 caption="Gridworld demo"):
        """
        mode: ("manual", "auto", "hybrid")
        dim: (int > 0, int > 0)
        cell_size: (int >= 50, int >= 50)
        cell_size: (int >= 50 * max_x, int >= 50 * max_y)
        """

        # Instance variables
        self._dim = dim
        self._sm = sm
        self._mode = mode
        self._fps = fps
        self._show_help = show_help
        self._show_msg_box = show_msg_box
        self._show_grid_lines = show_grid_lines
        self._enable_sound = enable_sound
        self._bg_color = bg_color
        self._grid_line_style = grid_line_style
        self._window_caption = caption
        self._running = False
        self._paused = False

        # Initialize pygame window
        pygame.init()

        # Determine window and cell size
        self._window_size, self._cell_size = self._determine_window_cell_size(window_size, cell_size)

        # Set up pygame window
        pygame.display.set_caption(self._window_caption)
        self._screen = pygame.display.set_mode([self._window_size[0], self._window_size[1]])
        self._grid = pygame.Surface((self._cell_size[0] * self._dim[0], self._cell_size[1] * self._dim[1]))

        # Pygame events
        self._animate_mouse_hover = show_mouse_hover_animation
        self._mouse_hover_anim_color = mouse_hover_anim_color

        # Game objects
        self._game_objects = pygame.sprite.Group()
        self._bg_sprites = pygame.sprite.Group()

        # Initialization functions
        self._generate_bg_sprites()

    def toggle_grid_lines(self):
        self._show_grid_lines = not self._show_grid_lines
        for sprite in self._bg_sprites.sprites():
            sprite.toggle_grid_lines()

    def cell_size(self):
        return self._cell_size

    def run(self):
        clock = pygame.time.Clock()
        self._running = True
        while self._running:
            for event in pygame.event.get():
                self.event_handler(event)
            # self.update()
            # self.render(self._sm.curr_state)
            self.render(None)        # FIXME: FOR DEBUG

            # Set FPS
            clock.tick(self._fps)

    def event_handler(self, event):
        if event.type == pygame.QUIT:
            self._running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_t:
                self.toggle_grid_lines()

    def update(self):
        # if self._show_grid_lines:
        #     self._bg_sprites.update(show_grid_lines=True)
        pass

    def render(self, state):
        # Screen background is black.
        self._screen.fill((0, 0, 0))

        # Determine position of grid in window.
        grid_left = (self._screen.get_size()[0] - self._grid.get_size()[0]) // 2
        grid_top = (self._screen.get_size()[1] - self._grid.get_size()[1]) // 2
        self._screen.blit(self._grid, (grid_left, grid_top))

        # Update background sprites
        self._bg_sprites.update()
        self._bg_sprites.draw(self._grid)

        # Handle mouse_hover event.
        self.mouse_hover()



        pygame.display.flip()

    def get_mouse_hover_animation_color(self):
        return self._mouse_hover_anim_color

    def mouse_hover(self):
        if self._animate_mouse_hover:
            mouse_pos = pygame.mouse.get_pos()
            for sprite in self._bg_sprites.sprites():
                sprite.mouse_hover(mouse_pos)

    def _generate_bg_sprites(self):
        x_max, y_max = self._dim
        for x in range(x_max):
            for y in range(y_max):
                cell_xy = BGSprite(parent=self, x=x, y=y, bg_color=self._bg_color,
                                   line_color=self._grid_line_style.line_color,
                                   line_width=self._grid_line_style.line_width,
                                   show_grid_lines=self._show_grid_lines)
                self._bg_sprites.add(cell_xy)
                self._game_objects.add(cell_xy)

    def _auto_window_size(self):
        # Given gridworld dimensions, try 100 x 100 pix cells.
        # The window dimensions should not exceed screen size - 150 pix.
        # If not try 75 x 75 pix cells.
        # If not, raise error.
        # Fix window and cell sizes.
        # Handle given cell and/or window sizes.
        pass

    def _determine_window_cell_size(self, window_size, cell_size):
        display = pygame.display.Info()
        screen_size = [display.current_w - 100, display.current_h - 100]

        if window_size != "auto" and cell_size != "auto":
            # FIXME (hard coded): Grid should fit leaving at least 10 pixels border on all 4 sides of window.
            assert window_size[0] <= screen_size[0], \
                f"window width doesn't fit within screen width (available={screen_size[0]})."
            assert window_size[1] <= screen_size[1], \
                f"window width doesn't fit within screen width (available={screen_size[1]})."
            assert cell_size[0] >= 75 and cell_size[1] >= 75, "cell_size must be >= 75 x 75 pixels."
            assert cell_size[0] * self._dim[0] <= window_size[0] - 20, "cell_width * num_cols <= window_width"
            assert cell_size[1] * self._dim[1] <= window_size[1] - 20, "cell_height * num_rows <= window_height"

            print(ColoredMsg.ok(f"Setting user specified window_size: {window_size}, cell_size: {cell_size}"))
            return window_size, cell_size

        elif window_size != "auto" and cell_size == "auto":
            assert window_size[0] <= screen_size[0], \
                f"window width doesn't fit within screen width (available={screen_size[0]})."
            assert window_size[1] <= screen_size[1], \
                f"window width doesn't fit within screen width (available={screen_size[1]})."

            # Try cell size 100 px.
            if 100 * self._dim[0] <= window_size[0] - 20 and 100 * self._dim[1] <= window_size[1] - 20:
                print(ColoredMsg.ok(f"Setting user specified window_size: {window_size}, determined cell_size: {100}"))
                return window_size, (100, 100)

            # Try cell size 75 px.
            elif 75 * self._dim[0] <= window_size[0] - 20 and 75 * self._dim[1] <= window_size[1] - 20:
                print(ColoredMsg.ok(f"Setting user specified window_size: {window_size}, determined cell_size: {75}"))
                return window_size, (75, 75)

            # Currently, we will try only two cell sizes. Else give error.
            else:
                raise AssertionError("Neither 100 x 100 nor 75 x 75 cells could fit within given window size.")

        elif window_size == "auto" and cell_size != "auto":
            assert cell_size >= 75, "cell_size must be >= 75 x 75 pixels."
            assert cell_size[0] * self._dim[0] <= screen_size[0] - 20, "cell_width * num_cols <= screen_width"
            assert cell_size[1] * self._dim[1] <= screen_size[1] - 20, "cell_height * num_rows <= screen_height"

            window_width = cell_size[0] * self._dim[0] + 20
            window_height = cell_size[1] * self._dim[1] + 20

            print(ColoredMsg.ok(f"Setting determined window_size: {window_size}, user given cell_size: {cell_size}"))
            return (window_width, window_height), cell_size

        else:  # window_size == "auto" and cell_size == "auto":
            # Try cell size 100 px.
            #   Ensure window should leave 100 px border on screen, 20 px border between grid and window
            if 100 * self._dim[0] <= screen_size[0] - 120 and 100 * self._dim[1] <= screen_size[1] - 120:
                print(
                    ColoredMsg.ok(
                        f"Setting determined window_size: {(100 * self._dim[0] + 20, 100 * self._dim[1] + 20)}, "
                        f"cell_size: {100}"
                    )
                )
                return (100 * self._dim[0] + 20, 100 * self._dim[1] + 20), (100, 100)

            # Try cell size 75 px.
            elif 75 * self._dim[0] <= screen_size[0] - 120 and 75 * self._dim[1] <= screen_size[1] - 120:
                print(
                    ColoredMsg.ok(
                        f"Setting determined window_size: {(75 * self._dim[0] + 20, 75 * self._dim[1] + 20)}, "
                        f"cell_size: {75}"
                    )
                )
                return (75 * self._dim[0] + 20, 75 * self._dim[1] + 20), (75, 75)

            # Currently, we will try only two cell sizes. Else give error.
            else:
                raise AssertionError("Neither 100 x 100 nor 75 x 75 cells could fit within given window size.")


class GameObject(pygame.sprite.Sprite):
    def __init__(self, parent, x, y):
        """
        :param parent: (Player object)
        :param x: (int) X-coordinate.
        :param y: (int) Y-coordinate.
        """
        super(GameObject, self).__init__()
        self._parent = parent
        self.image = pygame.Surface(self._parent.cell_size())
        self.rect = self.image.get_rect()
        cell_width, cell_height = self._parent.cell_size()
        self._pos = [x * cell_width, y * cell_height]
        self.rect.topleft = self._pos


class BGSprite(GameObject):
    def __init__(self, parent, x, y, bg_color=(255, 255, 255),
                 line_width=3, line_color=(0, 0, 0), show_grid_lines=True):
        """
        :param parent: (Player object)
        :param x: (int) X-coordinate.
        :param y: (int) Y-coordinate.
        :param bg_color: (3-tuple of int) (R, G, B), each value between [0, 255]
        :param line_width: (int) Line width of borders.
        :param line_color: (tuple[int, int, int]) Line color of borders.
        :param show_grid_lines: (bool) Show/hide grid line.
        """
        super(BGSprite, self).__init__(parent, x, y)
        self._bg_color = bg_color
        self._line_width = line_width
        self._line_color = line_color
        self._show_grid_lines = show_grid_lines
        self.image.fill(self._bg_color)

    def update(self):
        if self._show_grid_lines:
            pygame.draw.rect(
                self.image,
                self._line_color,
                pygame.Rect(0, 0, self.rect.width, self.rect.height),
                self._line_width
            )
        else:
            pygame.draw.rect(
                self.image,
                self._bg_color,
                pygame.Rect(0, 0, self.rect.width, self.rect.height),
                self._line_width
            )

    def toggle_grid_lines(self):
        self._show_grid_lines = not self._show_grid_lines

    def mouse_hover(self, mouse_pos):
        if self.rect.collidepoint(mouse_pos):
            self.image.fill(self._parent.get_mouse_hover_animation_color())
        else:
            self.image.fill(self._bg_color)


if __name__ == '__main__':
    sim = GWSim(
        dim=(5, 5),
        sm=None,
        # window_size=(700, 700),
        # cell_size=(75, 75),
        show_grid_lines=True,
        fps=60,
        grid_line_style=LineStyle(1, "solid", (0, 0, 0))
    )
    # for spr in sim._bg_sprites.sprites():
    #     print(spr, spr.rect)
    sim.run()

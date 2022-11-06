import pygame
from typing import Union
from ggsolver.graph import *
from dataclasses import dataclass


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


class GWSim:
    def __init__(self, dim, sm,
                 window_size: Union[str, tuple[int, int]] = "auto",
                 cell_size: Union[str, tuple[int, int]] = "auto",
                 bg_color=DEFAULT_BG_COLOR,
                 grid_line_style=DEFAULT_LINE_STYLE,
                 mode=None,
                 fps=2,
                 show_help=True,
                 show_msg_box=False,
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
        self._enable_sound = enable_sound
        self._bg_color = bg_color
        self._grid_line_style = grid_line_style
        self._window_caption = caption
        self._running = False
        self._paused = False

        if window_size == "auto":
            self._window_size = self._auto_window_size()
        else:
            self._window_size = window_size

        if cell_size == "auto":
            self._cell_size = self._auto_cell_size()
        else:
            self._cell_size = cell_size

        # Initialize pygame window
        pygame.init()
        pygame.display.set_caption(self._window_caption)
        self._screen = pygame.display.set_mode(self._window_size)

        # Game objects
        self._game_objects = pygame.sprite.Group()
        self._bg_sprites = pygame.sprite.Group()

        # Initialization functions
        self._generate_bg_sprites()

    def cell_size(self):
        return self._cell_size

    def run(self):
        clock = pygame.time.Clock()
        self._running = True
        self._screen.fill((200, 100, 0))
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

    def update(self):
        pass

    def render(self, state):
        self._bg_sprites.update()
        self._bg_sprites.draw(self._screen)
        pygame.display.flip()

    def _generate_bg_sprites(self):
        x_max, y_max = self._dim
        x_size, y_size = self._cell_size
        for x in range(x_max):
            for y in range(y_max):
                cell_xy = BGSprite(parent=self, x=x*x_size, y=y*y_size, bg_color=self._bg_color, border_style=self._grid_line_style)
                self._bg_sprites.add(cell_xy)
                self._game_objects.add(cell_xy)


class GameObject(pygame.sprite.Sprite):
    def __init__(self, parent, x, y):
        """
        :param parent: (Player object)
        :param x: (int) X-coordinate.
        :param y: (int) Y-coordinate.
        """
        super(GameObject, self).__init__()
        self._parent = parent
        self._pos = [x, y]
        self.image = pygame.Surface(self._parent.cell_size())
        self.rect = self.image.get_rect()
        self.rect.topleft = [x, y]


class BGSprite(GameObject):
    def __init__(self, parent, x, y, bg_color=(255, 255, 255), border_style=DEFAULT_LINE_STYLE):
        """
        :param parent: (Player object)
        :param x: (int) X-coordinate.
        :param y: (int) Y-coordinate.
        :param bg_color: (3-tuple of int) (R, G, B), each value between [0, 255]
        :param border_style: (LineStyle) Line width of borders.
        """
        super(BGSprite, self).__init__(parent, x, y)
        self._bg_color = bg_color
        self._line_width = border_style.line_width
        self._line_color = border_style.line_color
        self._line_style = border_style.line_style

        # self.image = pygame.Surface()
        self.image.fill(self._bg_color)
        # self.image.set_colorkey(self._bg_color)
        pygame.draw.rect(
            self.image,
            self._line_color,
            pygame.Rect(0, 0, self.rect.width, self.rect.height),
            self._line_width
        )


if __name__ == '__main__':
    sim = GWSim(
        dim=(2, 2),
        sm=None,
        window_size=(400, 400),
        cell_size=(200, 200)
    )
    for spr in sim._bg_sprites.sprites():
        print(spr, spr.rect)
    sim.run()

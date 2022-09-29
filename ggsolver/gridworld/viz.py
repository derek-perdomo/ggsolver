import pygame
from pygame._sdl2 import Window, Texture, Image, Renderer, get_drivers, messagebox


class GWSim:
    STANDALONE = "standalone"
    SERVER = "server"

    LAYOUT_CLASSIC = "classic"

    def __init__(self,
                 mode=STANDALONE,
                 graph=None,
                 server=None,
                 show_msg_window=False):
        """
        mode: (str) decides whether to connect to a server or to load a game graph.
        graph: (Graph or None). The graph used to run the simulation.
        server: (str) IP address of the server with port (e.g., `0.0.0.0:8080`).
        """
        # Mode
        self._mode = mode
        self._graph = None
        self._server = None

        # Players and Game objects
        self._players = dict()
        self._game_objects = pygame.sprite.Group()      # (Sprite group containing all sprites)

        # Pygame window(s)
        self._windows = dict()
        self._layout = self.LAYOUT_CLASSIC
        self._show_msg_window = show_msg_window

        # Status flags
        self._is_initialized = False

        # Initialize the simulation
        if mode == self.STANDALONE:
            self.init_with_graph(graph)
        elif mode == self.SERVER:
            self.init_with_server(server)
        else:
            raise ValueError(f"Input mode must be either {self.STANDALONE} or {self.SERVER}.")

        # Initialize base windows
        self.init_base_windows()

    def add_player(self, name, player):
        assert isinstance(player, Player)
        self._players[name] = player
        for obj in player.game_objects():
            self._game_objects.add(obj)
        if player.perspective():
            self._windows[name] = player.perspective()

    def rem_player(self, name):
        if name in self._players:
            for obj in self._players[name].game_objects():
                self._game_objects.remove(obj)
            if name in self._windows:
                self._windows.pop(name)
        self._players.pop(name)

    def init_base_windows(self):
        base_window = Perspective()

    def init_with_graph(self, graph):
        # TODO. Check important graph properties required for simulation.
        self._graph = graph

    def init_with_server(self, server):
        # TODO. Initialize connection to server.
        pass

    def set_layout(self, layout):
        self._layout = layout

    def is_initialized(self):
        return self._is_initialized

    def mode(self):
        return self._mode

    def windows(self):
        return self._windows


class Player:
    def game_objects(self):
        # TODO. Implement.
        return []

    def perspective(self):
        return None


class GameObject(pygame.sprite.Sprite):
    pass


class Perspective(Window):
    """ Windowed approach """
    pass

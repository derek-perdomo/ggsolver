import random
import sys

import pygame
import util
from multiprocessing import Process


class SM:
    def __init__(self):
        self._state = None
        self._states_history = []
        self._action_history = []
        self._curr_step = 0
        self._len_history = float("inf")


class GWSim:
    STANDALONE = "standalone"
    SERVER = "server"

    LAYOUT_CLASSIC = "classic"

    def __init__(self,
                 mode=STANDALONE,
                 graph=None,
                 server=None):
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
        self._players = {
            "god": None,
            "p1": None,
            "p2": None,
            "env": None,
        }
        self._game_objects = pygame.sprite.Group()      # (Sprite group containing all sprites)

        # Plugins (e.g., message windows etc.)
        self._plugins = dict()

        # Pygame window(s)
        self._windows = dict()
        self._layout = self.LAYOUT_CLASSIC

        # Status flags
        self._is_initialized = False

        # Initialize the simulation
        if mode == self.STANDALONE:
            self.init_with_graph(graph)
        elif mode == self.SERVER:
            self.init_with_server(server)
        else:
            raise ValueError(f"Input mode must be either {self.STANDALONE} or {self.SERVER}.")

    def set_player(self, name, player):
        assert isinstance(player, Player)
        assert name in self._players, "Input name should be one of {god, p1, p2, env}."
        self._players[name] = player
        for obj in player.game_objects():
            self._game_objects.add(obj)
        player.set_parent(self)

    def rem_player(self, name):
        if name in self._players:
            for obj in self._players[name].game_objects():
                self._game_objects.remove(obj)
        self._players.pop(name)

    def init_windows(self):
        pass

    def init_with_graph(self, graph):
        # TODO. Check important graph properties required for simulation.
        self._graph = graph

    def init_with_server(self, server):
        # TODO. Initialize connection to server.
        pass

    def init_plugins(self):
        pass

    def set_layout(self, layout=LAYOUT_CLASSIC):
        self._layout = layout

    def is_initialized(self):
        return self._is_initialized

    def mode(self):
        return self._mode

    def windows(self):
        return self._windows

    def run(self):
        self.init_windows()
        self.init_plugins()
        self.set_layout(self._layout)

        if len(self.windows()) == 0:
            print("[ERROR] No windows configured. Running in NOVIS mode.")

        pygame_processes = dict()
        for p_name, player in self._players.items():
            if player is not None:
                process = Process(target=player.run)
                process.daemon = True
                pygame_processes[p_name] = process

        for p_name, process in pygame_processes.items():
            process.start()
            print(f"[INFO] Started process for {p_name}.")

        while True:
            print({p_name: process.is_alive() for p_name, process in pygame_processes.items()}, end="\r")
            if not any(process.is_alive() for p_name, process in pygame_processes.items()):
                break

        print()
        print("Exited.")

class Player(SM):
    def __init__(self,
                 name,
                 perceptual_graph):

        # Initialize player state machine
        super(Player, self).__init__()

        # Player's game
        self._graph = perceptual_graph      # Perceptual game graph

        # Thought bubble visualization
        self._parent = None                 # GWSim instance.
        self._window = None                 # Pygame window
        self._tb_visible = False            # Thought bubble window visibility.

        self.size = (200, 200)
        self.screen = None
        self.bgcolor = (random.randint(0, 255), 0, 0)
        self.name = name

    def set_tb_visibility(self, value):
        self._tb_visible = value
        self._parent.set_layout()

    def set_parent(self, value):
        assert isinstance(value, GWSim)
        self._parent = value

    def game_objects(self):
        # TODO. Implement.
        return []

    def perspective(self):
        return None

    def run(self):
        self.screen = pygame.display.set_mode(self.size)
        self.screen.fill(self.bgcolor)
        while True:
            events = pygame.event.get()
            for e in events:
                if e.type == pygame.QUIT:
                    sys.exit(0)
                if e.type == pygame.KEYDOWN:
                    if e.key == pygame.K_ESCAPE:
                        sys.exit(0)  # close this specific process

            pygame.display.update()



class GameObject(pygame.sprite.Sprite):
    pass


if __name__ == '__main__':

    sim = GWSim()
    p1 = Player("player 1", None)
    p2 = Player("player 2", None)
    sim.set_player("p1", p1)
    sim.set_player("p2", p2)

    sim.run()

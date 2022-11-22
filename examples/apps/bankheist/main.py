"""
Programmer's notes:


"""
import json

import numpy as np
import pygame
import os
import pathlib
import itertools

import ggsolver.mdp as mdp
import ggsolver.gridworld as gw
import ggsolver.gridworld.util as gw_utils
from collections import namedtuple

curr_file_path = pathlib.Path(__file__).parent.resolve()


class BankHeistWindow(gw.Window):
    def __init__(self, name, size, game_config, **kwargs):
        super(BankHeistWindow, self).__init__(name, size, **kwargs)
        with open(game_config, "r") as file:
            self._game_config = json.load(file)

        if self._game_config["game"] != "Bank Heist":
            raise ValueError("The game is not Bank Heist.")

        # Construct grid
        self._terrain = np.array(self._game_config["terrain"])
        grid_size = tuple(reversed(self._terrain.shape))
        self.grid = gw.Grid(
            name="grid1",
            parent=self,
            position=(0, 0),
            size=size,
            grid_size=grid_size,
            backcolor=gw.COLOR_BEIGE,
            dockstyle=gw.DockStyle.TOP_LEFT,
            on_cell_leave=self.on_cell_leave,
            on_cell_enter=self.on_cell_enter,
        )

        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                if self._terrain[y, x] == 0:
                    self.grid[x, y].backcolor = gw.COLOR_GRAY51

        # Create character
        self._robber = Character(
            name="robber",
            parent=self.grid[0, 7],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["p1"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            init_sprite="N",
        )

        # Police cars
        # PATCH: Hard coded to two for now.
        self._police1 = Character(
            name="police1",
            parent=self.grid[3, 1],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["p2"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            # visible=False,
            init_sprite="N",
        )
        self._police2 = Character(
            name="police2",
            parent=self.grid[4, 1],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["p2"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            # visible=False,
            init_sprite="N",
        )

        # Banks
        bank1_pos = self._game_config["banks"]["banks.1"]
        bank2_pos = self._game_config["banks"]["banks.2"]
        self._bank1 = Character(
            name="bank1",
            parent=self.grid[bank1_pos[0], bank1_pos[1]],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["banks"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            visible=True,
            init_sprite="front",
        )
        self._bank2 = Character(
            name="bank2",
            parent=self.grid[bank2_pos[0], bank2_pos[1]],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["banks"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            visible=True,
            init_sprite="front",
        )

        # Gas station
        gas1_pos = self._game_config["gas"]["gas.1"]
        self._gas = Character(
            name="gas",
            parent=self.grid[gas1_pos[0], gas1_pos[1]],
            position=(0, 0),
            size=(0.75 * self.grid[0, 0].width, 0.75 * self.grid[0, 0].height),
            dockstyle=gw.DockStyle.CENTER,
            sprites=self._game_config["gas"]["sprites"],
            backcolor=gw.COLOR_TRANSPARENT,
            visible=True,
            init_sprite="front",
        )

    def sm_update(self, sender, event_args):
        print(f"sm_update: {event_args}")

    def on_cell_leave(self, sender, event_args):
        # print(f"on_cell_leave: {sender.name=}, {event_args=}")
        if sender.name == event_args.trigger.name:
            self.arrange_controls_in_cell(event_args.trigger)

    def on_cell_enter(self, sender, event_args):
        # print(f"on_cell_enter: {sender.name=}, {event_args=}")
        if sender.name == event_args.trigger.name:
            self.arrange_controls_in_cell(event_args.trigger)

    def arrange_controls_in_cell(self, cell):
        if len(cell.controls) == 0:
            pass

        elif len(cell.controls) == 1:
            print(f"arrange_controls_in_cell: {cell.name}, {len(cell.controls)=}")
            control = list(cell.controls.values())[0]
            control.width = 0.75 * cell.width
            control.height = 0.75 * cell.height
            control.dock = gw.DockStyle.CENTER

        elif len(cell.controls) == 2:
            print(f"arrange_controls_in_cell: {cell.name}, {len(cell.controls)=}")

            control0 = list(cell.controls.values())[0]
            control0.dock = gw.DockStyle.TOP_LEFT
            control0.width = 0.5 * cell.width
            control0.height = 0.5 * cell.height

            control1 = list(cell.controls.values())[1]
            control1.dock = gw.DockStyle.BOTTOM_RIGHT
            control1.width = 0.5 * cell.width
            control1.height = 0.5 * cell.height
        else:
            print(f"Not supported")


class Character(gw.Control):
    def __init__(self, name, parent, position, size, **kwargs):
        """
        Additional kwargs:
        * sprites: (Dict[str, PathLike]) Mapping of sprite name to sprite image.
        * init_sprite: (str) Name of initial sprite to use.
        """
        super(Character, self).__init__(name, parent, position, size, on_key_down=self.on_key_down, **kwargs)

        self._sprite_files = kwargs["sprites"] if "sprites" in kwargs else dict()
        self._sprites = {name: None for name, file in self._sprite_files.items()}
        # self._curr_sprite = None
        # PATCH
        self._curr_sprite = kwargs["init_sprite"] if "init_sprite" in kwargs else None

        self.add_event_handler(pygame.MOUSEBUTTONDOWN, self._on_select_changed)

    def __repr__(self):
        return f"<{self.__class__.__name__} at {self.parent.name}>"

    def _on_select_changed(self, sender, event_args):
        self._is_selected = not self._is_selected
    
    def update(self):
        super(Character, self).update()

        if self._curr_sprite is not None:
            if self._sprites[self._curr_sprite] is None:
                self._sprites[self._curr_sprite] = pygame.image.load(os.path.join(curr_file_path, pathlib.Path(self._sprite_files[self._curr_sprite])))
                self._sprites[self._curr_sprite] = pygame.transform.scale(self._sprites[self._curr_sprite], (50, 50))
            self._backimage = self._sprites[self._curr_sprite]

    def on_key_down(self, sender, event_args):
        if self.name == "robber":
            if event_args.key == pygame.K_RIGHT:
                self._curr_sprite = "E"
                (x, y) = self.parent.name
                if (x + 1, y) in self.parent.parent.controls:
                    self.parent = self.parent.parent[x + 1, y]

            if event_args.key == pygame.K_LEFT:
                self._curr_sprite = "W"
                (x, y) = self.parent.name
                if (x - 1, y) in self.parent.parent.controls:
                    self.parent = self.parent.parent[x - 1, y]

            if event_args.key == pygame.K_UP:
                self._curr_sprite = "N"
                (x, y) = self.parent.name
                if (x, y + 1) in self.parent.parent.controls:
                    self.parent = self.parent.parent[x, y + 1]

            if event_args.key == pygame.K_DOWN:
                self._curr_sprite = "S"
                (x, y) = self.parent.name
                if (x, y - 1) in self.parent.parent.controls:
                    self.parent = self.parent.parent[x, y - 1]

        if event_args.key == pygame.K_h:
            self.visible = not self.visible


class BankHeistMDP(mdp.QualitativeMDP):
    def __init__(self, game_config):
        super(BankHeistMDP, self).__init__()
        with open(game_config, "r") as file:
            self._game_config = json.load(file)

        self._terrain = np.array(self._game_config["terrain"])
        self._p2_1_accessible = np.array(self._game_config["p2"]["p2.1"]["accessible region"])
        self._p2_2_accessible = np.array(self._game_config["p2"]["p2.2"]["accessible region"])
        self._grid_size = tuple(reversed(self._terrain.shape))

    def states(self):
        """
        State representation: (p1.cell, p2.1.cell, p2.2.cell, p1.gas)
        :return:
        """
        x_max, y_max = self._grid_size
        p1_walkable_cells = [(x, y) for x in range(x_max) for y in range(y_max) if self._terrain[y, x] == 1]
        p1_gas = self._game_config["p1"]["gas capacity"]
        p2_1_walkable_cells = [(x, y) for x in range(x_max) for y in range(y_max) if self._p2_1_accessible[y, x] == 1]
        p2_2_walkable_cells = [(x, y) for x in range(x_max) for y in range(y_max) if self._p2_2_accessible[y, x] == 1]

        return list(itertools.product(p1_walkable_cells, p2_1_walkable_cells, p2_2_walkable_cells, range(p1_gas)))

    def actions(self):
        return [
            gw_utils.GW_ACT_N,
            gw_utils.GW_ACT_S,
            gw_utils.GW_ACT_E,
            gw_utils.GW_ACT_W,
        ]

    def delta(self, state, act):
        pass


if __name__ == '__main__':
    conf = os.path.join(curr_file_path, "saved_games", "game_2022_11_22_16_24.conf")
    game = BankHeistMDP(game_config=conf)
    print(len(game.states()))

    # window = BankHeistWindow(name="Bank Heist", size=(660, 480), game_config=conf)
    # window.run()

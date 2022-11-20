import numpy as np
import ggsolver.mdp as mdp
import ggsolver.gridworld as gw
from collections import namedtuple


GAME_CONFIG = {
    "maze": np.random.randint(low=0, high=2, dtype=int, size=(15, 15))
}


class BankHeistWindow(gw.Window):
    def __init__(self, name, size, game_config, **kwargs):
        super(BankHeistWindow, self).__init__(name, size, **kwargs)
        self._game_config = game_config

        # Construct grid
        grid_size = self._game_config["maze"].shape
        self.grid = gw.Grid(
            name="grid1",
            parent=self,
            position=(0, 0),
            size=size,
            grid_size=grid_size,
            backcolor=gw.COLOR_BEIGE,
            anchor=gw.AnchorStyle.TOP_LEFT,
        )

        for x in range(grid_size[0]):
            for y in range(grid_size[1]):
                if self._game_config["maze"][x, y] == 0:
                    self.grid[x, y].backcolor = gw.COLOR_BLACK

    def sm_update(self, event_args):
        print(f"sm_update: {event_args}")


if __name__ == '__main__':
    window = BankHeistWindow(name="Bank Heist", size=(600, 600), game_config=GAME_CONFIG)
    window.run()

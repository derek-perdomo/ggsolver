from ggsolver.gridworld.models import *


class SubGrid(Grid):
    def on_key_down(self, event_args):
        # print("Call: Subgrid.on_key_down")
        if event_args.key == pygame.K_RIGHT:
            self._position[0] += 5


if __name__ == '__main__':
    window = Window(name="window1", size=(600, 600), backcolor=(245, 245, 220))
    # control = Control(name="control1", parent=window, position=(100, 100), size=(50, 10))

    grid = Grid(name="grid", parent=window, position=(0, 0), size=(600, 600), grid_size=(2, 2))
    window.add_control(grid)

    sub_grid = SubGrid(name="sub-grid", parent=grid, position=(0, 0), size=(50, 50), grid_size=(2, 1))
    grid.add_control(sub_grid)

    window.run()

from ggsolver.gridworld.models import *


if __name__ == '__main__':
    window = Window(name="main", size=(600, 600), backcolor=(245, 245, 220), frame_rate=5, title="Primary")
    window2 = Window(name="secondary", size=(600, 600), backcolor=(245, 245, 220), frame_rate=5, title="Secondary")
    sim = GWSim(None, [window, window2])
    sim.run()

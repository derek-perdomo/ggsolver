# GGSolver

`ggsolver` is a python library containing set-based solvers for synthesis of winning strategies in two-player games on graphs. 

Version 1.0, Copyright (c) 2021, BSD 3 LICENSE
It is developed and maintained by Abhishek N. Kulkarni, University of Florida (http://akulkarni.me).


## Structure of library

`ggsolver/`
* `docker/` - Contains docker configuration file containing dependencies to run solvers.

* `docs/` - Auto generated documentation (also available on http://akulkarni.me/ggsolver/). 

* `examples/` - Illustrative examples on ggsolver features and demos from research papers.

* `ggsolver/` - python package containing various game on graph models and solvers. Each model and its corresponding solvers are placed in independent folder.

    * `dtptb/` - Deterministic two-player turn-based game.
    * `stptb/` - Stochastic two-player turn-based game.
    * `mdp/` - Game on MDP. 
    * `actiondeception/` - Action deception [IJCAI'20]
    * `sensorattack/` - Sensor attacks [CDC'21]
    * `staticpref/` - Synthesis with preference logic
    * `ds.py` - Common data structures used in ggsolver.
    * `utils.py` - Common utilities used in ggsolver.

* `parsers/` - parsers for various logics.

* `CHANGELOG.md` - Tracks important changes between versions.


## Jupyter Notebook Usage Instructions

1. Pull the latest version of `ggsolver` from `https://github.com/abhibp1993/ggsolver.git`.

2. Pull the latest version of `cirl-assignments` from `https://github.com/abhibp1993/cirl-assignments.git`.

3. Pull the latest version of docker image `abhibp1993/ggsolver` using `docker pull abhibp1993/ggsolver`.

4. Run `docker run -it -p 8888:8888 -v <path to ggsolver>:/home/ggsolver
   -v <path to cirl-assignments>:/home/cirl-assignments abhibp1993/ggsolver`

5. Run `cd /home/cirl-assignments/`

6. Run `jupyter notebook --allow-root --ip 0.0.0.0`

7. Use the link with `127.0.0.1/...` to open jupyter notebook on browser.
FROM debian:bullseye


# Install base utilities
RUN apt-get update && \
    apt-get install -y build-essential  && \
    apt-get install -y wget && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install miniconda
ENV CONDA_DIR /opt/conda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
     /bin/bash ~/miniconda.sh -b -p /opt/conda

# Put conda in path so we can use conda activate
ENV PATH=$CONDA_DIR/bin:$PATH


# Install spot
RUN conda install -c conda-forge spot

# Install graph-tool
RUN conda install -c conda-forge graph-tool

# Install graphviz
RUN conda install -c anaconda graphviz
RUN conda install -c conda-forge pygraphviz
RUN conda install -c conda-forge pydot

# Install basic python packages
RUN conda install -c anaconda numpy
RUN conda install -c conda-forge matplotlib
RUN conda install -c conda-forge scipy
RUN conda install -c conda-forge pytest
RUN conda install -c conda-forge pyzmq
RUN conda install -c conda-forge networkx
RUN conda install -c conda-forge pyyaml
RUN conda install -c conda-forge lark
RUN #conda install -c conda-forge jupyterlab



## Install python packages
#RUN pip3 install numpy matplotlib pyzmq pydot networkx pygraphviz pytest
#RUN pip3 install scipy pygame pyyaml lark
#RUN pip3 install sortedcontainers
RUN pip3 install jupyterlab
RUN pip3 install sphinx
RUN pip3 install myst-parser
RUN pip3 install sphinx_rtd_theme recommonmark
RUN pip3 install dd
RUN pip3 install nbsphinx

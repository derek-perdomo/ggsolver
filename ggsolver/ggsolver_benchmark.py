import ggsolver as gg
import random
import time
import tracemalloc
import logging

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s %(levelname)s %(name)s %(message)s",
                    # datefmt='%m-%d %H:%M',
                    filename="ggsolver_benchmark.log"
                    )
                    

def profile(tag):
    graph = gg.TGraph()

    num_nodes = int(1e5)
    num_edges = int(1e6)
    num_queries = int(1e5)

    tracemalloc.start()
    # Add a 10K nodes, 100K edges at random.
    start0 = time.time_ns()
    graph.add_nodes_from(num_nodes)
    end0 = time.time_ns()
    logging.debug(f"{tag}: {num_nodes} node addition: {10 ** -6 * (end0 - start0)} ms.")

    start1 = time.time_ns()
    graph.add_edges_from([(random.randint(0, num_nodes-1), random.randint(0, num_nodes -1 )) for _ in range(num_edges)])
    end1 = time.time_ns()
    logging.debug(f"{tag}: {num_edges} edge addition: {10 ** -6 * (end1 - start1)} ms.")
    
    # # Run a 100K successor and predecessor queries.
    start2 = time.time_ns()
    for _ in range(num_queries):
        n = random.randint(0, num_nodes - 1)
        graph.successors(n)

    end2 = time.time_ns()
    logging.debug(f"{tag}: {num_queries} succcessor queries: {10 ** -6 * (end2 - start2)} ms.")

    for _ in range(num_queries):
        n = random.randint(0, num_nodes - 1)
        graph.predecessors(n)

    end3 = time.time_ns()
    logging.debug(f"{tag}: {num_queries} predecessor queries: {10 ** -6 * (end3 - end2)} ms.")
    _, peak = tracemalloc.get_traced_memory()
    logging.debug(f"Peak was {peak / 10 ** 6} MB")
    tracemalloc.stop()


if __name__ == '__main__':
    # Run profiler
    logging.debug("START-----------------------\n\n")
    for _ in range(10):
        logging.debug("---------------------------------\n")
        profile(tag="ggsolver")

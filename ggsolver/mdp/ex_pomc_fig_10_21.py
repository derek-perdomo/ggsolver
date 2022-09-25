"""
Example from Principles of Model Checking, Fig. 10.21.
"""
from ggsolver.mdp.models import QualitativeMDP


if __name__ == '__main__':
    mdp = QualitativeMDP(
        states=[f"s{i}" for i in range(8)],
        actions=['alpha', 'beta'],
        trans_dict={
            "s0": {'alpha': ["s1"], 'beta': ["s2", "s4"]},
            "s1": {'alpha': ["s1", "s2", "s3"], 'beta': ["sink"]},
            "s2": {'alpha': ["s2"], 'beta': ["sink"]},
            "s3": {'alpha': ["s3"], 'beta': ["sink"]},
            "s4": {'alpha': ["s5", "s6"], 'beta': ["sink"]},
            "s5": {'alpha': ["s6"], 'beta': ["s2", "s7"]},
            "s6": {'alpha': ["s5", "s6"], 'beta': ["sink"]},
            "s7": {'alpha': ["s2", "s3"], 'beta': ["sink"]},
            "sink": {'alpha': ["sink"], 'beta': ["sink"]},
        },
        init_state="s0",
        final=["s2", "s3"]
    )
    mdp_graph = mdp.graphify()

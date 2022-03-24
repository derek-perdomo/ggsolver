#include "Snap.h"

int main(int argc, char* argv[]) {
    PNGraph Graph = TNGraph::New();
    Graph->AddNode(1);
    Graph->AddNode(5);
    Graph->AddNode(32);
    Graph->AddEdge(1, 5);
    Graph->AddEdge(5, 1);
    Graph->AddEdge(5, 32);
}


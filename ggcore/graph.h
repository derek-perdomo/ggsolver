//
// Created by Abhishek on 24-Mar-22.
//

#ifndef GGCORE_GRAPH_H
#define GGCORE_GRAPH_H

#include <memory>
#include <utility>
#include <Snap.h>
#include "entity.h"
#include "types.h"
#include "version.h"

using namespace std;

namespace ggsolver {

    class TNode;
    class TEdge;
    class TGraph;

    typedef std::shared_ptr<TNode> PNode;
    typedef std::shared_ptr<TEdge> PEdge;
    typedef std::shared_ptr<TGraph> PGraph;

    using TEdgeIdTriple = std::tuple<unsigned long, unsigned long, PAttrMap>;
    using TEdgeNodeTriple = std::tuple<PNode, PNode, PAttrMap>;


    class TNode : public TEntity {
    private:
        unsigned long m_SnapId;

    public:
        explicit TNode(unsigned long id) : m_SnapId(id) {}
        TNode(unsigned long id, PAttrMap attrMap) : TEntity(attrMap), m_SnapId(id) {}
        unsigned long GetNId();
    };

    class TEdge : public TEntity {
    private:
        unsigned long m_SnapId;
        unsigned long m_UId;
        unsigned long m_VId;
        unsigned long m_Key;
        PAttrMap m_AttrMap;
    public:
        TEdge(unsigned long eid, unsigned long uid, unsigned long vid) : m_SnapId(eid), m_UId(uid), m_VId(vid) {}
        TEdge(unsigned long eid, unsigned long uid, unsigned long vid, PAttrMap attrMap) :
            m_SnapId(eid), m_UId(uid), m_VId(vid)  {
            m_AttrMap = std::move(attrMap);
        }
        unsigned long GetEId();
        unsigned long GetUId();
        unsigned long GetVId();
        unsigned long GetKey();
    };

    class TGraph : public TEntity {
    private:    // Representation
        PNEGraph m_Graph;
        std::unordered_map<unsigned long, PNode> m_Nodes;
        std::unordered_map<unsigned long, PEdge> m_Edges;

    public:
        TGraph() {
            m_Graph = TNEGraph::New();
        }

        PNode AddNode() {}
        PNode AddNode(const PAttrMap& attrMap) {}

        std::vector<PNode> AddNodesFrom(unsigned long k) {}
        std::vector<PNode> AddNodesFrom(const std::vector<PAttrMap>& attrMaps) {}
        std::vector<PNode> AddNodesFrom(const std::pair<json, PAttrMap>& nodes) {}

        PEdge AddEdge(const unsigned long& uid, const unsigned long& v) {}
        PEdge AddEdge(const unsigned long& u, const unsigned long& v, const PAttrMap& attrMap) {}
        PEdge AddEdge(const PNode& u, const PNode& v) {}
        PEdge AddEdge(const PNode& u, const PNode& v, const PAttrMap& attrMap) {}

        std::vector<PEdge> AddEdgesFrom(std::vector<std::pair<unsigned long, unsigned long>> edges) {}
        std::vector<PEdge> AddEdgesFrom(std::vector<std::pair<PNode, PNode>> edges) {}
        std::vector<PEdge> AddEdgesFrom(std::vector<TEdgeIdTriple> edges) {}
        std::vector<PEdge> AddEdgesFrom(std::vector<TEdgeNodeTriple> edges) {}

        void RemNode(const unsigned long& id) {}
        void RemNode(const PNode& node) {}
        void RemNodesFrom(std::vector<unsigned long> nodes) {}
        void RemNodesFrom(std::vector<PNode> nodes) {}

        void RemEdge(const unsigned long& eid) {}
        void RemEdge(const PEdge& edge) {}
        void RemEdgesFrom(std::vector<unsigned long> edges) {}
        void RemEdgesFrom(std::vector<PEdge> edges) {}

        bool HasNode(const unsigned long& nid) {}
        bool HasNode(const PNode& node) {}
        bool HasEdge(const unsigned long& eid) {}
        bool HasEdge(const PEdge& edge) {}

        void Clear() {}
        void Reserve(unsigned long num_nodes) {}
        void Reserve(unsigned long num_nodes, unsigned long num_edges) {}


        std::vector<PEdge> Edges() {}
        std::vector<PEdge> InEdges(const unsigned long& vid) {}
        std::vector<PEdge> InEdges(const PNode& v) {}
        std::vector<PEdge> OutEdges(const unsigned long& uid) {}
        std::vector<PEdge> OutEdges(const PNode& u) {}

        std::vector<PNode> Successors(const unsigned long& u) {}
        std::vector<PNode> Successors(const PNode& u) {}
        std::vector<PNode> Predecessors(const unsigned long& u) {}
        std::vector<PNode> Predecessors(const PNode& u) {}

        unsigned long NumberOfNodes() {}
        unsigned long NumberOfEdges() {}
        unsigned long Size() {}

    };

}

#endif //GGCORE_GRAPH_H

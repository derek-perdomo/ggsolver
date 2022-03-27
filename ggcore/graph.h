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
        const std::vector<std::string> m_special_attr_names {"nid"};
        unsigned long m_snap_id;

    public:
        explicit TNode() : m_snap_id(-1) {}    // default (-1) will store the maximum value of long due to `unsigned`.
        TNode(json attrMap) : TEntity(attrMap), m_snap_id(-1) {}
        unsigned long get_node_id() {
            return m_snap_id;
        }
        template <typename T = json>
        void set_attr(const std::string& key, const T& value) {
            // If key is not special attribute
            if (!is_special_attr(key)) {
                // Update key and value in json attr_map. Use try-catch to protect un-jsonifiable values.
                m_attr_map[key] = value;
            }
            else {
                throw std::invalid_argument("Use specialized TNode.set_<attr> "
                                            "functions to update specialized attributes.");
            }
        }

        template <typename T = json>
        T get_attr(const std::string& key){
            if (!is_special_attr(key)) {
                return m_attr_map[key].get<T>();
            }
            else {
                if (key == "nid") {
                    return get_node_id();
                }
            }
        }

    private:
        friend class TGraph;
        void set_node_id(unsigned long nid) {
            m_snap_id = nid;
        }
    };

    class TEdge : public TEntity {
    private:
        const std::vector<std::string> m_special_attr_names {"uid", "vid", "eid"};
        unsigned long m_snap_id;
        unsigned long m_uid;
        unsigned long m_vid;

    public:
        TEdge(unsigned long eid, unsigned long uid, unsigned long vid) : m_snap_id(eid), m_uid(uid), m_vid(vid) {}
        TEdge(unsigned long eid, unsigned long uid, unsigned long vid, json attr_map) : TEntity(attr_map),
            m_snap_id(eid), m_uid(uid), m_vid(vid)  {}
        unsigned long get_eid() {
            return m_snap_id;
        }
        unsigned long get_uid() {
            return m_uid;
        }
        unsigned long get_vid() {
            return m_vid;
        }

    private:
        friend class TGraph;
        void set_edge_id(unsigned long eid, unsigned long uid, unsigned long vid){
            m_snap_id = eid;
            m_uid = uid;
            m_vid = vid;
        }
    };

//    class TGraph : public TEntity {
//    private:    // Representation
//        PNEGraph m_Graph;
//        std::unordered_map<unsigned long, PNode> m_Nodes;
//        std::unordered_map<unsigned long, PEdge> m_Edges;
//
//    public:
//        TGraph() {
//            m_Graph = TNEGraph::New();
//        }
//
//        PNode AddNode() {}
//        PNode AddNode(const PAttrMap& attrMap) {}
//
//        std::vector<PNode> AddNodesFrom(unsigned long k) {}
//        std::vector<PNode> AddNodesFrom(const std::vector<PAttrMap>& attrMaps) {}
//        std::vector<PNode> AddNodesFrom(const std::pair<json, PAttrMap>& nodes) {}
//
//        PEdge AddEdge(const unsigned long& uid, const unsigned long& v) {}
//        PEdge AddEdge(const unsigned long& u, const unsigned long& v, const PAttrMap& attrMap) {}
//        PEdge AddEdge(const PNode& u, const PNode& v) {}
//        PEdge AddEdge(const PNode& u, const PNode& v, const PAttrMap& attrMap) {}
//
//        std::vector<PEdge> AddEdgesFrom(std::vector<std::pair<unsigned long, unsigned long>> edges) {}
//        std::vector<PEdge> AddEdgesFrom(std::vector<std::pair<PNode, PNode>> edges) {}
//        std::vector<PEdge> AddEdgesFrom(std::vector<TEdgeIdTriple> edges) {}
//        std::vector<PEdge> AddEdgesFrom(std::vector<TEdgeNodeTriple> edges) {}
//
//        void RemNode(const unsigned long& id) {}
//        void RemNode(const PNode& node) {}
//        void RemNodesFrom(std::vector<unsigned long> nodes) {}
//        void RemNodesFrom(std::vector<PNode> nodes) {}
//
//        void RemEdge(const unsigned long& eid) {}
//        void RemEdge(const PEdge& edge) {}
//        void RemEdgesFrom(std::vector<unsigned long> edges) {}
//        void RemEdgesFrom(std::vector<PEdge> edges) {}
//
//        bool HasNode(const unsigned long& nid) {}
//        bool HasNode(const PNode& node) {}
//        bool HasEdge(const unsigned long& eid) {}
//        bool HasEdge(const PEdge& edge) {}
//
//        void Clear() {}
//        void Reserve(unsigned long num_nodes) {}
//        void Reserve(unsigned long num_nodes, unsigned long num_edges) {}
//
//
//        std::vector<PEdge> Edges() {}
//        std::vector<PEdge> InEdges(const unsigned long& vid) {}
//        std::vector<PEdge> InEdges(const PNode& v) {}
//        std::vector<PEdge> OutEdges(const unsigned long& uid) {}
//        std::vector<PEdge> OutEdges(const PNode& u) {}
//
//        std::vector<PNode> Successors(const unsigned long& u) {}
//        std::vector<PNode> Successors(const PNode& u) {}
//        std::vector<PNode> Predecessors(const unsigned long& u) {}
//        std::vector<PNode> Predecessors(const PNode& u) {}
//
//        unsigned long NumberOfNodes() {}
//        unsigned long NumberOfEdges() {}
//        unsigned long Size() {}
//
//    };

}

#endif //GGCORE_GRAPH_H

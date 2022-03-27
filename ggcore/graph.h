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
        TEdge() : m_snap_id(-1), m_uid(-1), m_vid(-1) {}
        unsigned long get_edge_id() {
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


    class TGraph : public TEntity {
    private:    // Representation
        PNEGraph m_graph;
        std::unordered_map<unsigned long, PNode> m_nodes;
        std::unordered_map<unsigned long, PEdge> m_edges;

    public:
        TGraph() {
            m_graph = TNEGraph::New();
        }

        /// Nodes are identified by their IDs. For an application, if node is identified by some other object,
        ///  user is expected to maintain the map {id: object} separately.
        PNode add_node() {
            // Add node to snap graph
            auto nid = m_graph->AddNode();
            // Create a new node
            auto node = std::make_shared<TNode>();
            // Set its node id
            node->set_node_id(nid);
            // Update nodes id:object map
            m_nodes[nid] = node;
            // Return node object
            return node;
        }
        PNode add_node(const json& attr_map) {
            // Add node to snap graph
            auto nid = m_graph->AddNode();
            // Create a new node
            auto node = std::make_shared<TNode>(attr_map);
            // Set its node id
            node->set_node_id(nid);
            // Update nodes id:object map
            m_nodes[nid] = node;
            // Return node object
            return node;
        }

        std::vector<PNode> add_nodes_from(const unsigned long& k) {
            std::vector<PNode> nodes;
            for(int i = 0; i < k; i++) {
                nodes.push_back(add_node());
            }
            return nodes;
        }
        std::vector<PNode> add_nodes_from(const std::vector<json>& attr_maps) {
            std::vector<PNode> nodes;
            for(const auto& item : attr_maps) {
                nodes.push_back(add_node(item));
            }
            return nodes;
        }

//        PEdge add_edge(const unsigned long& uid, const unsigned long& v) {}
//        PEdge add_edge(const unsigned long& u, const unsigned long& v, const json& attr_map) {}
//        PEdge add_edge(const PNode& u, const PNode& v) {}
//        PEdge add_edge(const PNode& u, const PNode& v, const json& attr_map) {}
//
//        std::vector<PEdge> add_edges_from(std::vector<std::pair<unsigned long, unsigned long>> edges) {}
//        std::vector<PEdge> add_edges_from(std::vector<std::pair<PNode, PNode>> edges) {}
//        std::vector<PEdge> add_edges_from(std::vector<std::tuple<unsigned long, unsigned long, json>> edges) {}
//        std::vector<PEdge> add_edges_from(std::vector<std::tuple<PNode, PNode, json>> edges) {}
//
//        void rem_node(const unsigned long& id) {}
//        void rem_node(const PNode& node) {}
//        void rem_nodes_from(std::vector<unsigned long> nodes) {}
//        void rem_nodes_from(std::vector<PNode> nodes) {}
//
//        void rem_edge(const unsigned long& eid) {}
//        void rem_edge(const PEdge& edge) {}
//        void rem_edges_from(std::vector<unsigned long> edges) {}
//        void rem_edges_from(std::vector<PEdge> edges) {}
//
        bool has_node(const unsigned long& nid) {
            if (m_nodes.find(nid) != m_nodes.end()){
                return true;
            }
            return false;
        }
        bool has_node(const PNode& node) {
            return has_node(node->get_node_id());
        }
//        bool has_edge(const unsigned long& eid) {}
//        bool has_edge(const PEdge& edge) {}
//
//        void clear() {}
//        void reserve(unsigned long num_nodes) {}
//        void reserve(unsigned long num_nodes, unsigned long num_edges) {}
//
//
//        std::vector<PEdge> edges() {}
//        std::vector<PEdge> in_edges(const unsigned long& vid) {}
//        std::vector<PEdge> in_edges(const PNode& v) {}
//        std::vector<PEdge> out_edges(const unsigned long& uid) {}
//        std::vector<PEdge> out_edges(const PNode& u) {}
//
//        std::vector<PNode> successors(const unsigned long& u) {}
//        std::vector<PNode> successors(const PNode& u) {}
//        std::vector<PNode> predecessors(const unsigned long& u) {}
//        std::vector<PNode> predecessors(const PNode& u) {}
//
//        unsigned long number_of_nodes() {}
//        unsigned long number_of_edges() {}
//        unsigned long size() {}

    };

}

#endif //GGCORE_GRAPH_H

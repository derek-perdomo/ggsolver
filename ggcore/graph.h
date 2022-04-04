//
// Created by Abhishek on 24-Mar-22.
//

#ifndef GGCORE_GRAPH_H
#define GGCORE_GRAPH_H

#include <memory>
#include <utility>
#include <tuple>
#include <Snap.h>
#include "entity.h"
#include "types.h"
#include "version.h"

#define HEADER_NODE_ID "nid"
#define HEADER_EDGE_ID "eid"
#define HEADER_EDGE_SRC_ID "uid"
#define HEADER_EDGE_DST_ID "vid"

using namespace std;

namespace ggsolver {

    class TNode;
    class TEdge;
    class TGraph;

    typedef std::shared_ptr<TNode> PNode;
    typedef std::shared_ptr<TEdge> PEdge;
    typedef std::shared_ptr<TGraph> PGraph;

    using TEdgeIdTriple = std::tuple<unsigned long, unsigned long, TAttrMap>;
    using TEdgeNodeTriple = std::tuple<PNode, PNode, TAttrMap>;


    class TNode : public TEntity {
    private:
        const std::vector<std::string> m_reserved_attr {HEADER_NODE_ID};
        const std::string m_class_name = "TNode";

    public:
        explicit TNode() {
            set_attr(HEADER_NODE_ID, std::make_shared<TValue>((long)-1));
        }
        TNode(const TAttrMap& attr_map) : TNode() {
            for (const auto& item : attr_map) {
                set_attr(item.first, item.second);
            }
        }
        TNode(const py::handle& attr_map) : TNode() {
            auto dict = attr_map.cast<py::dict>();
            for (const auto& item : dict) {
                set_attr(item.first.cast<std::string>(), item.second);
            }
        }
        unsigned long get_nid() {
            return get_attr(HEADER_NODE_ID)->get_int();
        }

    private:
        friend class TGraph;
        void set_nid(const long& nid) {
            set_attr(HEADER_NODE_ID, std::make_shared<TValue>(nid));
        }
    };

    class TEdge : public TEntity {
    private:
        const std::vector<std::string> m_reserved_attr {"uid", "vid", "eid"};
        const std::string m_class_name = "TEdge";

    public:
        TEdge() {
            set_attr(HEADER_EDGE_ID, std::make_shared<TValue>((long)-1));
            set_attr(HEADER_EDGE_SRC_ID, std::make_shared<TValue>((long)-1));
            set_attr(HEADER_EDGE_DST_ID, std::make_shared<TValue>((long)-1));
        }
        TEdge(const TAttrMap& attr_map) : TEdge() {
            for (const auto& item : attr_map) {
                set_attr(item.first, item.second);
            }
        }
        TEdge(const py::handle& attr_map) : TEdge() {
            auto dict = attr_map.cast<py::dict>();
            for (const auto& item : dict) {
                set_attr(item.first.cast<std::string>(), item.second);
            }
        }

        long get_eid() {
            return get_attr(HEADER_EDGE_ID)->get_int();
        }
        long get_uid() {
            return get_attr(HEADER_EDGE_SRC_ID)->get_int();
        }
        long get_vid() {
            return get_attr(HEADER_EDGE_DST_ID)->get_int();
        }

    private:
        friend class TGraph;
        void set_edge_id(const long& eid, const long& uid, const long& vid){
            set_attr(HEADER_EDGE_ID, std::make_shared<TValue>(eid));
            set_attr(HEADER_EDGE_SRC_ID, std::make_shared<TValue>(uid));
            set_attr(HEADER_EDGE_DST_ID, std::make_shared<TValue>(vid));
        }
    };


    class TGraph : public TEntity {
    private:    // Representation
        PNEGraph m_graph;
        std::unordered_map<unsigned long, PNode> m_nodes;
        std::unordered_map<unsigned long, PEdge> m_edges;
        const std::vector<std::string> m_reserved_attr {"nodes", "edges", "graph"};
        const std::string m_class_name = "TGraph";

    public:
        TGraph() : TEntity() {
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
            node->set_nid(nid);
            // Update nodes id:object map
            m_nodes[nid] = node;
            // Return node object
            return node;
        }
        PNode add_node(const TAttrMap& attr_map) {
            // Add node to snap graph
            auto nid = m_graph->AddNode();
            // Create a new node
            auto node = std::make_shared<TNode>(attr_map);
            // Set its node id
            node->set_nid(nid);
            // Update nodes id:object map
            m_nodes[nid] = node;
            // Return node object
            return node;
        }
        PNode add_node(const py::handle& attr_map) {
            // Add node to snap graph
            auto nid = m_graph->AddNode();
            // Create a new node
            auto node = std::make_shared<TNode>(attr_map);
            // Set its node id
            node->set_nid(nid);
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
        std::vector<PNode> add_nodes_from(const std::vector<TAttrMap>& attr_maps) {
            std::vector<PNode> nodes;
            for(const auto& item : attr_maps) {
                nodes.push_back(add_node(item));
            }
            return nodes;
        }
        std::vector<PNode> add_nodes_from(const std::vector<py::handle>& attr_maps) {
            std::vector<PNode> nodes;
            for(const auto& item : attr_maps) {
                nodes.push_back(add_node(item));
            }
            return nodes;
        }

        PEdge add_edge(const unsigned long& uid, const unsigned long& vid) {
            if (has_node(uid) && has_node(vid)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(uid, vid);
                // Create a new edge
                auto edge = std::make_shared<TEdge>();
                // Set its edge id
                edge->set_edge_id(eid, uid, vid);
                // Update edges {id:object} map
                m_edges[eid] = edge;
                // Return edge object
                return edge;
            }
            throw std::invalid_argument("TGraph.add_edge: uid and/or vid are not in graph.");
        }
        PEdge add_edge(const unsigned long& uid, const unsigned long& vid, const TAttrMap& attr_map) {
            if (has_node(uid) && has_node(vid)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(uid, vid);
                // Create a new edge
                auto edge = std::make_shared<TEdge>(attr_map);
                // Set its edge id
                edge->set_edge_id(eid, uid, vid);
                // Update edges {id:object} map
                m_edges[eid] = edge;
                // Return edge object
                return edge;
            }
            throw std::invalid_argument("TGraph.add_edge: uid and/or vid are not in graph.");
        }
        PEdge add_edge(const unsigned long& uid, const unsigned long& vid, const py::handle& attr_map) {
            if (has_node(uid) && has_node(vid)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(uid, vid);
                // Create a new edge
                auto edge = std::make_shared<TEdge>(attr_map);
                // Set its edge id
                edge->set_edge_id(eid, uid, vid);
                // Update edges {id:object} map
                m_edges[eid] = edge;
                // Return edge object
                return edge;
            }
            throw std::invalid_argument("TGraph.add_edge: uid and/or vid are not in graph.");
        }
        PEdge add_edge(const PNode& u, const PNode& v) {
            return add_edge(u->get_nid(), v->get_nid());
        }
        PEdge add_edge(const PNode& u, const PNode& v, const TAttrMap& attr_map) {
            return add_edge(u->get_nid(), v->get_nid(), attr_map);
        }
        PEdge add_edge(const PNode& u, const PNode& v, const py::handle& attr_map) {
            if (has_node(u) && has_node(v)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(u->get_nid(), v->get_nid());
                // Create a new edge
                auto edge = std::make_shared<TEdge>(attr_map);
                // Set its edge id
                edge->set_edge_id(eid, u->get_nid(), v->get_nid());
                // Update edges {id:object} map
                m_edges[eid] = edge;
                // Return edge object
                return edge;
            }
            throw std::invalid_argument("TGraph.add_edge: uid and/or vid are not in graph.");
        }

        std::vector<PEdge> add_edges_from(std::vector<std::pair<unsigned long, unsigned long>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(item.first, item.second));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::pair<PNode, PNode>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(item.first, item.second));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<unsigned long, unsigned long, TAttrMap>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(std::get<0>(item), std::get<1>(item), std::get<2>(item)));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<unsigned long, unsigned long, py::handle>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(std::get<0>(item), std::get<1>(item), std::get<2>(item)));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<PNode, PNode, TAttrMap>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(std::get<0>(item), std::get<1>(item), std::get<2>(item)));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<PNode, PNode, py::handle>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(std::get<0>(item), std::get<1>(item), std::get<2>(item)));
            }
            return edge_objects;
        }

        void rem_node(const unsigned long& id) {
            // Remove only if node exists
            if (has_node(id)){
                // remove from snap graph
                m_graph->DelNode(id);
                // remove from {id: node} map.
                m_nodes.erase(id);
            }
        }
        void rem_node(const PNode& node) {
            rem_node(node->get_nid());
        }
        void rem_nodes_from(std::vector<unsigned long> nodes) {
            for (const auto& nid : nodes){
                rem_node(nid);
            }
        }
        void rem_nodes_from(std::vector<PNode> nodes) {
            for (const auto& node : nodes){
                rem_node(node);
            }
        }

        void rem_edge(const unsigned long& eid) {
            // Remove only if edge exists
            if (has_edge(eid)){
                // remove edge from snap graph
                m_graph->DelEdge(eid);
                // remove from {id: edge} map.
                m_edges.erase(eid);
            }
        }
        void rem_edge(const PEdge& edge) {
            rem_edge(edge->get_eid());
        }
        void rem_edges_from(std::vector<unsigned long> edges) {
            for (const auto& eid : edges){
                rem_edge(eid);
            }
        }
        void rem_edges_from(std::vector<PEdge> edges) {
            for (const auto& edge : edges){
                rem_edge(edge);
            }
        }

        bool has_node(const unsigned long& nid) {
            if (m_nodes.find(nid) != m_nodes.end()){
                return true;
            }
            return false;
        }
        bool has_node(const PNode& node) {
            return has_node(node->get_nid());
        }
        bool has_edge(const unsigned long& eid) {
            if (m_edges.find(eid) != m_edges.end()){
                return true;
            }
            return false;
        }
        bool has_edge(const PEdge& edge) {
            return has_edge(edge->get_eid());
        }

        void clear() {
            m_graph->Clr();
            m_nodes.clear();
            m_edges.clear();
        }
        void reserve(unsigned long num_nodes, unsigned long num_edges) {
            m_graph->Reserve(num_nodes, num_edges);
            m_nodes.reserve(num_nodes);
            m_edges.reserve(num_edges);
        }


        std::vector<PEdge> edges() {
            std::vector<PEdge> ret_edges;
            for (const auto& key : m_edges){
                ret_edges.push_back(key.second);
            }
            return ret_edges;
        }
        std::vector<PEdge> in_edges(const unsigned long& vid) {
            // Initialize empty in edges vector
            std::vector<PEdge> ret_in_edges;

            // Get in-degree of given node from SNAP's graph
            auto in_degree = m_graph->GetNI(vid).GetInDeg();

            // Iteratively query SNAP for in neighbors and extract corresponding iglpy node
            int eid;
            for (int i = 0; i < in_degree; i++) {
                eid = m_graph->GetNI(vid).GetInEId(i);
                ret_in_edges.push_back(m_edges[eid]);
            }

            // Return in edges
            return ret_in_edges;
        }
        std::vector<PEdge> in_edges(const PNode& v) {
            return in_edges(v->get_nid());
        }
        std::vector<PEdge> out_edges(const unsigned long& uid) {
            // Initialize empty in edges vector
            std::vector<PEdge> ret_out_edges;

            // Get out-degree of given node from SNAP's graph
            auto out_degree = m_graph->GetNI(uid).GetOutDeg();

            // Iteratively query SNAP for out edges
            int eid;
            for (int i = 0; i < out_degree; i++) {
                eid = m_graph->GetNI(uid).GetOutEId(i);
                ret_out_edges.push_back(m_edges[eid]);
            }

            // Return in edges
            return ret_out_edges;
        }
        std::vector<PEdge> out_edges(const PNode& u) {
            return out_edges(u->get_nid());
        }

        std::vector<PNode> successors(const unsigned long& uid) {
            auto ret_out_edges = out_edges(uid);
            std::vector<PNode> ret_successors;
            unsigned long vid;
            for (const auto& edge : ret_out_edges) {
                vid = edge->get_vid();
                ret_successors.push_back(m_nodes[vid]);
            }
            return ret_successors;
        }
        std::vector<PNode> successors(const PNode& u) {
            return successors(u->get_nid());
        }
        std::vector<PNode> predecessors(const unsigned long& vid) {
            auto ret_in_edges = in_edges(vid);
            std::vector<PNode> ret_successors;
            unsigned long uid;
            for (const auto& edge : ret_in_edges) {
                uid = edge->get_uid();
                ret_successors.push_back(m_nodes[uid]);
            }
            return ret_successors;
        }
        std::vector<PNode> predecessors(const PNode& u) {
            return predecessors(u->get_nid());
        }

        unsigned long number_of_nodes() {
            return m_graph->GetNodes();
        }
        unsigned long number_of_edges() {
            return m_graph->GetEdges();
        }
        unsigned long size() {
            // FIXME: Will this have overflow issue?
            return number_of_nodes() + number_of_edges();
        }

        inline std::unordered_map<unsigned long, PNode> get_nodes_dict(){
            return m_nodes;
        }
        inline std::unordered_map<unsigned long, PEdge> get_edges_dict(){
            return m_edges;
        }
    };
}

#endif //GGCORE_GRAPH_H

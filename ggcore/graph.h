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
        TNode(const PAttrMap& attr_map) : TEntity(attr_map), m_snap_id(-1) {}
        TNode(const py::handle& attr_map) : TEntity(attr_map), m_snap_id(-1) {}
        TNode(const std::unordered_map<std::string, PValue>& attr_map) : TEntity(attr_map), m_snap_id(-1) {}

        unsigned long get_node_id() {
            return m_snap_id;
        }
        PValue get_attr(const std::string& key){
            if (!is_special_attr(key)) {
                return TEntity::get_attr(key);
            }

            if (key == "nid") {
                return std::make_shared<TValue>(get_node_id());
            }

            throw "attribute " + key + " is not in Node.";
        }

        // TODO
//        template <typename T>
//        void set_attr(const std::string& key, const T& value) {
//            // If key is not special attribute
//            if (!is_special_attr(key)) {
//                TEntity::set_attr<T>(key, value);
//            }
//            else {
//                throw std::invalid_argument("Use specialized TNode.set_<attr> "
//                                            "functions to update specialized attributes.");
//            }
//        }

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
        TEdge(const PAttrMap& attr_map) : TEntity(attr_map), m_snap_id(-1), m_uid(-1), m_vid(-1) {}
        TEdge(const py::handle& attr_map) : TEntity(attr_map), m_snap_id(-1), m_uid(-1), m_vid(-1) {}
        TEdge(const std::unordered_map<std::string, PValue>& attr_map) : TEntity(attr_map), m_snap_id(-1), m_uid(-1), m_vid(-1) {}

        unsigned long get_edge_id() {
            return m_snap_id;
        }
        unsigned long get_uid() {
            return m_uid;
        }
        unsigned long get_vid() {
            return m_vid;
        }

        PValue get_attr(const std::string& key){
            if (!is_special_attr(key)) {
                return TEntity::get_attr(key);
            }

            if (key == "eid") {
                return std::make_shared<TValue>(get_edge_id());
            }
            else if (key == "uid") {
                return std::make_shared<TValue>(get_uid());
            }
            else if (key == "vid") {
                return std::make_shared<TValue>(get_vid());
            }
            else {
                throw "attribute " + key + " is not in Node.";
            }
        }

        // TODO
//        template <typename T>
//        void set_attr(const std::string& key, const T& value) {
//            // If key is not special attribute
//            if (!is_special_attr(key)) {
//                TEntity::set_attr<T>(key, value);
//            }
//            else {
//                throw std::invalid_argument("Use specialized TNode.set_<attr> "
//                                            "functions to update specialized attributes.");
//            }
//        }

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
        const std::vector<std::string> m_special_attr_names {"nodes", "edges", "graph"};

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
        PNode add_node(const PAttrMap& attr_map) {
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
        PNode add_node(const py::handle& attr_map) {
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
        PNode add_node(const std::unordered_map<std::string, PValue>& attr_map) {
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
        std::vector<PNode> add_nodes_from(const std::vector<PAttrMap>& attr_maps) {
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
        std::vector<PNode> add_nodes_from(const std::vector<std::unordered_map<std::string, PValue>>& attr_maps) {
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
        PEdge add_edge(const unsigned long& uid, const unsigned long& vid, const PAttrMap& attr_map) {
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
        PEdge add_edge(const unsigned long& uid, const unsigned long& vid, const std::unordered_map<std::string, PValue>& attr_map) {
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
            return add_edge(u->get_node_id(), v->get_node_id());
        }
        PEdge add_edge(const PNode& u, const PNode& v, const PAttrMap& attr_map) {
            return add_edge(u->get_node_id(), v->get_node_id(), attr_map);
        }
        PEdge add_edge(const PNode& u, const PNode& v, const py::handle& attr_map) {
            if (has_node(u) && has_node(v)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(u->get_node_id(), v->get_node_id());
                // Create a new edge
                auto edge = std::make_shared<TEdge>(attr_map);
                // Set its edge id
                edge->set_edge_id(eid, u->get_node_id(), v->get_node_id());
                // Update edges {id:object} map
                m_edges[eid] = edge;
                // Return edge object
                return edge;
            }
            throw std::invalid_argument("TGraph.add_edge: uid and/or vid are not in graph.");
        }
        PEdge add_edge(const PNode& u, const PNode& v, const std::unordered_map<std::string, PValue>& attr_map) {
            if (has_node(u) && has_node(v)) {
                // Add edge to snap graph
                auto eid = m_graph->AddEdge(u->get_node_id(), v->get_node_id());
                // Create a new edge
                auto edge = std::make_shared<TEdge>(attr_map);
                // Set its edge id
                edge->set_edge_id(eid, u->get_node_id(), v->get_node_id());
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
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<unsigned long, unsigned long, PAttrMap>> edges) {
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
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<unsigned long, unsigned long, std::unordered_map<std::string, PValue>>> edges) {
            std::vector<PEdge> edge_objects;
            for (const auto& item : edges){
                edge_objects.push_back(add_edge(std::get<0>(item), std::get<1>(item), std::get<2>(item)));
            }
            return edge_objects;
        }
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<PNode, PNode, PAttrMap>> edges) {
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
        std::vector<PEdge> add_edges_from(std::vector<std::tuple<PNode, PNode, std::unordered_map<std::string, PValue>>> edges) {
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
            rem_node(node->get_node_id());
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
            rem_edge(edge->get_edge_id());
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
            return has_node(node->get_node_id());
        }
        bool has_edge(const unsigned long& eid) {
            if (m_edges.find(eid) != m_edges.end()){
                return true;
            }
            return false;
        }
        bool has_edge(const PEdge& edge) {
            return has_edge(edge->get_edge_id());
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
            return in_edges(v->get_node_id());
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
            return out_edges(u->get_node_id());
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
            return successors(u->get_node_id());
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
            return predecessors(u->get_node_id());
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

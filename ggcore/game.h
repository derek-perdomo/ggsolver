//
// Created by Abhishek on 24-Mar-22.
//

#ifndef GGCORE_GAME_H
#define GGCORE_GAME_H

#include <functional>
#include <memory>
#include "entity.h"
#include "graph.h"
#include "types.h"
#include "version.h"
#include <nlohmann/json.hpp>


using json = nlohmann::json;


namespace ggsolver {
    class TGame;
    typedef std::shared_ptr<TGame> PGame;

    class TGame : public TEntity {
    protected:
        PGraph m_Graph;
        std::function<std::vector<PNode>(const PNode&, const std::string&)> m_cb_Delta;
        std::function<std::vector<PEdge>(const PNode&)> m_cb_Predecessor;
        std::function<std::vector<PEdge>(const PNode&)> m_cb_Successor;
        std::function<std::vector<std::string>(const PNode&)> m_cb_Label;

    public:
        TGame(std::string name) {
            SetAttr("name", name);
            SetAttr("actions", json());
            SetAttr("init_state", json());
            SetAttr("atoms", json());
            SetAttr("mode", json());
            SetAttr("is_constructed", json());
            SetAttr("is_labeled", json());

            m_cb_Delta = DefaultCBDelta;
            m_cb_Predecessor = DefaultCBPredecessor;
            m_cb_Successor = DefaultCBSuccessor;
            m_cb_Label = DefaultCBLabel;
        }

        bool IsConstructed() {}
        bool IsLabeled() {}
        bool IsComplete() {}
        bool IsValid() {}
        std::string GetMode() {}

        std::vector<PNode> Delta(const PNode& state, const std::string& action) {}
        std::vector<PEdge> Predecessor(const PNode& state, const std::string& action) {}
        std::vector<PEdge> Successor(const PNode& state, const std::string& action) {}

        void MakeComplete() {}
        void MakeLabeled(std::vector<std::string> atoms,
                         std::function<std::vector<std::string>(const PNode&)> cb_label) {}

        void ConstructFromGraph(PGraph graph) {}
        void ConstructFromCallbacks(
                std::vector<PNode> nodes,
                std::function<std::vector<PNode>(const PNode&, const std::string&)> cb_delta,
                std::function<std::vector<PEdge>(const PNode&)> cb_predecessor,
                std::function<std::vector<PEdge>(const PNode&)> cb_successor
                ) {}

    private:  // default callbacks
        static std::vector<PNode> DefaultCBDelta(const PNode& state, const std::string& action) {}
        static std::vector<PEdge> DefaultCBPredecessor(const PNode& state) {}
        static std::vector<PEdge> DefaultCBSuccessor(const PNode& state) {}
        static std::vector<std::string> DefaultCBLabel(const PNode& state) {}
    };

}


#endif //GGCORE_GAME_H

//
// Created by Abhishek on 24-Mar-22.
//

#ifndef GGSOLVER_DTPTB_H
#define GGSOLVER_DTPTB_H


#include "game.h"


namespace ggsolver {
    namespace dtptb {

        /// Class declaration
        class TDTPTBGame;         // (Deterministic) Two Player Game on Graph
        class TSWReach;
        class TASWReach;
        class TPWReach;

        /// Type definitions for shared_ptr.
        typedef std::shared_ptr<TDTPTBGame> PDTPTBGame;
        typedef std::shared_ptr<TSWReach> PSWReach;
        typedef std::shared_ptr<TASWReach> PASWReach;
        typedef std::shared_ptr<TPWReach> PPWReach;

        /// Class definition: One player game
        class TDTPTBGame : public TGame {
        public:
            TDTPTBGame(std::string name) : TGame(name) {
                m_cb_Delta = DefaultCBDelta;
                m_cb_Predecessor = DefaultCBPredecessor;
                m_cb_Successor = DefaultCBSuccessor;
                m_cb_Label = DefaultCBLabel;
            }

            void ConstructFromGraph(PGraph graph) {}

            void ConstructFromCallbacks(
                    std::vector <PNode> nodes,
                    std::function<std::vector<PNode>(const PNode &, const std::string &)> cb_delta,
                    std::function<std::vector<PEdge>(const PNode &)> cb_predecessor,
                    std::function<std::vector<PEdge>(const PNode &)> cb_successor
            ) {}

        private:
            static std::vector <PNode> DefaultCBDelta(const PNode &state, const std::string &action) {}
            static std::vector <PEdge> DefaultCBPredecessor(const PNode &state) {}
            static std::vector <PEdge> DefaultCBSuccessor(const PNode &state) {}
            static std::vector <std::string> DefaultCBLabel(const PNode &state) {}
        };
        /// Class definition: Sure winning
        class TSWReach {

        };

        /// Class definition: Almost-sure winning
        class TASWReach {

        };

        /// Class definition: Positive Winning
        class TPWReach {

        };

    }
}


#endif //GGSOLVER_DTPTB_H

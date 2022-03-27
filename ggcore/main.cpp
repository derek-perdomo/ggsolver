//
// Created by Abhishek on 24-Mar-22.
//

#include "types.h"
#include "version.h"
#include "entity.h"
#include "graph.h"
//#include "game.h"
//#include "oneplayer.h"
//#include "mdp.h"
//#include "dtptb.h"
//#include "stptb.h"

using namespace ggsolver;


void test_entity() {
    TEntity ent0;
    ent0.set_attr<std::nullptr_t>("nullptr", std::nullptr_t());
    ent0.set_attr<bool>("bool", true);
    ent0.set_attr<std::string>("string", "entity");
    ent0.set_attr<json>("json", {{"ele1", 10}, {"ele2", "string"}});
}


void test_node() {
    TNode n1;
    n1.set_attr<>("name", std::string("test"));
    std::cout << n1.get_attr<std::string>("name") << std::endl;
}


int main(){

    test_entity();
    test_node();
    return 0;
}
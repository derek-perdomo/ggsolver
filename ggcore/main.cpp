//
// Created by Abhishek on 24-Mar-22.
//

#include "types.h"
#include "version.h"
#include "entity.h"
//#include "graph.h"
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

int main(){

    test_entity();
    return 0;
}
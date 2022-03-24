
#include <nlohmann/json.hpp>
#include <gtest/gtest.h>
#include "../ggcore/entity.h"
//#include "../ggcore/json_ext.h"

#include <iostream>
#include <memory>
#include <vector>
#include <variant>

using json = nlohmann::json;
using namespace ggsolver::core;



namespace {

    class EntityTest : public testing::Test {
    protected:
        void SetUp() {
            TEntity newEntity(std::string("name"));
            m_Entity = newEntity;
        }

        TEntity m_Entity;
        std::shared_ptr<TEntity> p_Entity;
    };


    TEST_F(EntityTest, TestInstantiations) {

        // Default instantiation
        ASSERT_NO_THROW(TEntity());

        // Instantiation with name
        TEntity ent0 = TEntity(std::string("namedEntity"));
        ASSERT_TRUE(ent0.HasAttr("name"));
        ASSERT_EQ(ent0.GetAttr("name"), std::string("namedEntity"));

        //// Instantiation with name and identity attributes
        //// json idAttr = { {"planet", "earth"}, {"windows", 10}, {"entity", ent0} };
        json idAttr = { {"planet", "earth"}, {"windows", 10} };
        //TEntity ent1 = TEntity(std::string("namedEntity"), idAttr);
        //ASSERT_TRUE(ent1.HasAttr("name"));
        //ASSERT_TRUE(ent1.HasAttr("planet"));
        //ASSERT_TRUE(ent1.HasAttr("windows"));
        //ASSERT_TRUE(ent1.IsReadOnlyAttr("name"));
        //ASSERT_TRUE(ent1.IsReadOnlyAttr("planet"));
        //ASSERT_EQ(ent1.GetAttr("planet"), std::string("earth"));
        //ASSERT_EQ(ent1.GetAttr("windows"), 10);
        ////ASSERT_EQ(ent1.GetAttr("entity"), ent0);

        // Copy constructor
        TEntity ent2(ent0);
        ASSERT_TRUE(ent2.HasAttr("name"));
        ASSERT_TRUE(ent2.HasAttr("planet"));
        ASSERT_TRUE(ent2.HasAttr("windows"));
        ASSERT_TRUE(ent2.IsReadOnlyAttr("name"));
        ASSERT_TRUE(ent2.IsReadOnlyAttr("planet"));
        ASSERT_EQ(ent2.GetAttr("planet"), std::string("earth"));
        ASSERT_EQ(ent2.GetAttr("windows"), 10);
        //ASSERT_EQ(ent2.GetAttr("entity"), ent0);
        
        // Copy constructor using pointer
        std::shared_ptr<TEntity> ent3 = std::make_shared<TEntity>(ent2);
        ASSERT_TRUE(ent3->HasAttr("name"));
        ASSERT_TRUE(ent3->HasAttr("planet"));
        ASSERT_TRUE(ent3->HasAttr("windows"));
        ASSERT_TRUE(ent3->IsReadOnlyAttr("name"));
        ASSERT_TRUE(ent3->IsReadOnlyAttr("planet"));
        ASSERT_EQ(ent3->GetAttr("planet"), std::string("earth"));
        ASSERT_EQ(ent3->GetAttr("windows"), 10);
        //ASSERT_EQ(ent3->GetAttr("entity"), ent0);

        // Construction from jsonified id properties
        idAttr = { {"planet", "earth"}, {"windows", 10} };
        TEntity ent4(idAttr);
        ASSERT_FALSE(ent4.HasAttr("name"));
        ASSERT_TRUE(ent4.HasAttr("planet"));
        ASSERT_TRUE(ent4.HasAttr("windows"));
        ASSERT_FALSE(ent4.IsReadOnlyAttr("name"));
        ASSERT_TRUE(ent4.IsReadOnlyAttr("planet"));
        ASSERT_EQ(ent4.GetAttr("planet"), std::string("earth"));
        ASSERT_EQ(ent4.GetAttr("windows"), 10);
        //ASSERT_EQ(ent4.GetAttr("entity"), ent0);

        // Construction from jsonified TEntity object
        TEntity ent5(ent2.Serialize());
        ASSERT_TRUE(ent5.HasAttr("name"));
        ASSERT_TRUE(ent5.HasAttr("planet"));
        ASSERT_TRUE(ent5.HasAttr("windows"));
        ASSERT_TRUE(ent5.IsReadOnlyAttr("name"));
        ASSERT_TRUE(ent5.IsReadOnlyAttr("planet"));
        ASSERT_EQ(ent5.GetAttr("planet"), std::string("earth"));
        ASSERT_EQ(ent5.GetAttr("windows"), 10);
        //ASSERT_EQ(ent5.GetAttr("entity"), ent0);

    }

    TEST_F(EntityTest, TestGetAttr) {
        // TODO: After implementing exchange.h
    }

    TEST_F(EntityTest, TestSetAttr) {
        // TODO: After implementing exchange.h
    }

}
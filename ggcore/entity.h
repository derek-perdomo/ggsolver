//
// Created by Abhishek on 24-Mar-22.
//

#ifndef GGCORE_ENTITY_H
#define GGCORE_ENTITY_H

#include <string>
#include <memory>
#include "types.h"
#include "version.h"

namespace ggsolver {

    class TEntity;
    typedef std::shared_ptr<TEntity> PEntity;


    class TEntity {
    private:
        PAttrMap m_AttrMap;

    public:
        TEntity() {
            m_AttrMap = std::make_shared<TAttrMap>();
        }
        TEntity(PAttrMap attrMap) {
            m_AttrMap = std::move(attrMap);
        }
        bool HasAttr(const std::string& key);
        void SetAttr(const std::string& key, const json& value);
        void GetAttrType(const std::string& key);
        template <typename T>
        T GetAttr(std::string key);
    };
}
#endif //GGCORE_ENTITY_H

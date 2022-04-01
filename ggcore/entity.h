#ifndef GGCORE_ENTITY_H
#define GGCORE_ENTITY_H

#include <iostream>
#include <algorithm>
#include <string>
#include <memory>
#include <typeinfo>
#include "types.h"
#include "version.h"

namespace ggsolver {

    class TEntity;
    typedef std::shared_ptr<TEntity> PEntity;

    /// Let JSON object store whatever it can. Attributes of other types must be stored in derived class
    /// using specialized C++ types. All specialized class variable names must be stored in static variable
    /// `special_properties`. The `getattr` and `setattr` functions should also be updated accordingly.
//    class TEntity {
//    protected:
//        json m_attr_map;
//        const std::vector<std::string> m_special_attr_names {};
//
//    public:
//        TEntity() {};
//        TEntity(json attr_map) {
//            if (attr_map.is_object()){
//                m_attr_map.update(attr_map);
//            }
//        }
//        bool is_special_attr(const std::string& key) {
//            return std::find(m_special_attr_names.begin(), m_special_attr_names.end(), key) != m_special_attr_names.end();
//        }
//        bool has_attr(const std::string& key) {
//            auto has_key = m_attr_map.find(key) != m_attr_map.end();
//            auto is_special = is_special_attr(key);
//            return has_key || is_special;
//        }
//        std::string get_attr_type(const std::string& key) {
//            return m_attr_map[key].type_name();
//        }
//
//        template <typename T = json>
//        void set_attr(const std::string& key, const T& value) {
//            // If key is not special attribute
//            if (!is_special_attr(key)) {
//                // Update key and value in json attr_map. Use try-catch to protect un-jsonifiable values.
//                m_attr_map[key] = value;
//            }
//            else {
//                throw std::invalid_argument("TEntity.set_attr() expects a nlohmann::json supported `value` type." );
//            }
//        }
//
//        template <typename T = json>
//        T get_attr(const std::string& key){
//            if (!is_special_attr(key)) {
//                return m_attr_map[key].get<T>();
//            }
//            else {
//                throw std::invalid_argument("TEntity.get_attr() has no specialized attributed.");
//            }
//        }
//    };
}
#endif //GGCORE_ENTITY_H

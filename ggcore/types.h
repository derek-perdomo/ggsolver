#ifndef GGCORE_TYPES_H
#define GGCORE_TYPES_H

#include <iostream>
#include <algorithm>
#include <string>
#include <utility>
#include <exception>
#include <vector>
#include <variant>
#include <memory>
#include <cstdint>
#include <unordered_map>
#include <stdexcept>
#include <type_traits>
#include <pybind11/pybind11.h>
#include <nlohmann/json.hpp>
#include "version.h"

#define HEADER_GGSOLVER_VERSION "__ggsolver_version"

using json = nlohmann::json;
namespace py = pybind11;


namespace ggsolver {

    class TEntity;
    class TValue;
    class TAttrMap;
    typedef std::shared_ptr<TEntity> PEntity;
    typedef std::shared_ptr<TValue> PValue;
    typedef std::shared_ptr<TAttrMap> PAttrMap;


    /// We can't work with JSON because it does not distinguish between list, tuple and set + it can't store Entity.
    class TValue {
    public:
        enum class Type : uint8_t {
            py_none,
            py_bool,
            py_int,
            py_float,
            py_str,
            py_tuple,
            py_list,
            py_set,
            py_dict,
            py_function,
            py_object,
            gg_entity,
        };

        typedef std::variant<
            std::nullptr_t,
            bool,
            unsigned long,
            double,
            std::string,
            PEntity,
            py::function,
            std::vector<PValue>,
            std::unordered_set<PValue>,
            std::unordered_map<std::string, PValue>
            > Value;

    private:
        Type m_type;
        Value m_value;

    public:
        TValue() : m_type(Type::py_none), m_value(nullptr) {}
        explicit TValue(const bool& val) : m_type(Type::py_bool), m_value(val) {}
        explicit TValue(const unsigned long& val) : m_type(Type::py_int), m_value(val) {}
        explicit TValue(const double& val) : m_type(Type::py_float), m_value(val) {}
        explicit TValue(const std::string& val) : m_type(Type::py_float), m_value(val) {}
        explicit TValue(const PEntity& val) : m_type(Type::gg_entity), m_value(std::move(val)) {}
        explicit TValue(const std::vector<PValue>& val) : m_type(Type::py_list), m_value(val) {}
        explicit TValue(const std::unordered_set<PValue>& val) : m_type(Type::py_set), m_value(val) {}
        explicit TValue(const std::unordered_map<std::string, PValue>& val) : m_type(Type::py_float), m_value(val) {}
        explicit TValue(const py::handle& val) {
//            std::cout << "TValue.constructor - py::handle" << std::endl;
            set_object(val);
        }
        TValue (const TValue& obj) {
            m_type = obj.m_type;
            m_value = obj.m_value;
        }

        void set_none() {
            m_type = Type::py_none;
            m_value = nullptr;
        }
        void set_bool(const bool& val) {
            m_type = Type::py_bool;
            m_value = val;
        }
        void set_int(const unsigned long& val) {
            m_type = Type::py_int;
            m_value = val;
        }
        void set_double(const double& val) {
            m_type = Type::py_float;
            m_value = val;
        }
        void set_string(const std::string& val) {
            std::cout << "\tsetting type to string" << std::endl;
            m_type = Type::py_str;
            std::cout << "\tupdating variant value" << std::endl;
            m_value = std::string(val);
            std::cout << "\tupdated variant value" << std::endl;
        }
        void set_entity(const PEntity& val) {
            m_type = Type::gg_entity;
            m_value = val;
        }
        void set_vector(const std::vector<PValue>& val, Type type=Type::py_list) {
            m_type = type;
            m_value = val;
        }
        void set_set(const std::unordered_set<PValue>& val) {
            m_type = Type::py_set;
            m_value = val;
        }
        void set_map(const std::unordered_map<std::string, PValue>& val) {
            m_type = Type::py_dict;
            m_value = val;
        }
        void set_object(const py::handle& val) {
            std::cout << "TValue.set_object(): " << typeid(val).name() << std::endl;
            std::cout << "\tval.__class__: " << val.attr("__class__").attr("__name__").cast<std::string>() << std::endl;

            if (py::isinstance<nullptr_t>(val) || val.is_none()){
                std::cout << "\tProcessing none" << std::endl;
                set_none();
            }
            else if (py::isinstance<py::bool_>(val)) {
                std::cout << "\tProcessing bool" << std::endl;
                set_bool(val.cast<bool>());
            }
            else if (py::isinstance<py::int_>(val)) {
                std::cout << "\tProcessing int" << std::endl;
                set_int(val.cast<unsigned long>());
            }
            else if (py::isinstance<py::float_>(val)) {
                std::cout << "\tProcessing float" << std::endl;
                set_double(val.cast<double>());
            }
            else if (py::isinstance<py::str>(val)) {
                std::cout << "\tProcessing str" << std::endl;
                auto str = val.cast<std::string>();
                set_string(str);
                std::cout << "\tProcessing str complete..." << std::endl;
            }
            else if (py::isinstance<py::tuple>(val)) {
                std::cout << "\tProcessing tuple" << std::endl;
                std::vector<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.push_back(t_val);
                }

                set_vector(out, Type::py_tuple);
            }
            else if (py::isinstance<py::list>(val)) {
                std::cout << "\tProcessing list" << std::endl;
                std::vector<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.push_back(t_val);
                }

                set_vector(out, Type::py_list);
            }
            else if (py::isinstance<py::set>(val)) {
                std::cout << "\tProcessing set" << std::endl;
                std::unordered_set<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.insert(std::move(t_val));
                }

                set_set(out);
            }
            else if (py::isinstance<py::dict>(val)) {
                std::cout << "\tProcessing dict" << std::endl;
                // Is dictionary a serialized object?
                bool is_serialized = false;
                bool is_entity = false;

                // Extract map
                std::unordered_map<std::string, PValue> out;
                std::string str_key;
                PValue t_value;
                for (const py::handle& key : val) {
                    str_key = key.cast<std::string>();
                    t_value = std::make_shared<TValue>(val[key]);

                    if (str_key == std::string("__class")) {
                        is_serialized = true;
                    }

                    if (str_key == std::string("__entity")) {
                        is_entity = true;
                    }
                }

                // If yes, is it an entity or some other python object?
                if (is_entity) {
                    throw "Entity cannot be processed by set_object. Use set_entity function.";
                }
                else if (is_serialized) {
                    m_type = Type::py_object;
                    m_value = out;
                }
                else {
                    set_map(out);
                }
            }
            else if (py::isinstance<py::function>(val)) {
                std::cout << "\tProcessing function" << std::endl;
                m_type = Type::py_function;
                m_value = val.cast<py::function>();
            }
            else {
                std::cout << "\tProcessing non-standard py type. Identifying if val is Entity..." << std::endl;

                // Try constructing an entity from object.
                try {
                    auto ent = val.cast<PEntity>();
                    set_entity(ent);
//                    auto is_entity = py::hasattr(val, "__entity__");
//                    std::cout << "\tis_entity(val): " << is_entity << std::endl;
//                    if (is_entity) {
//                        auto ent = val.cast<PEntity>();
//                        set_entity(ent);
//                    }
//                    else {
//                        throw "Unexpected type.";
//                    }
                }
                catch (py::cast_error e) {
                    std::string err_str = "Casting failed from " +
                            val.attr("__class__").attr("__name__").cast<std::string>() +
                                    " to PEntity.";
                    throw std::runtime_error(err_str);
                }
                catch (std::exception e) {
                    std::string err_str = "TValue.set_object() cannot process py::handle of type " +
                            val.attr("__class__").attr("__name__").cast<std::string>();
                    throw std::runtime_error(err_str);
                }
            }

            std::cout << "TValue.set_object(): complete" << std::endl;
        }

        Type get_type() {
            return m_type;
        }
        std::nullptr_t get_none() {
            if (m_type == Type::py_none)
                return nullptr;
            throw "value is not none.";
        }
        bool get_bool() {
            if (m_type == Type::py_bool)
                return std::get<bool>(m_value);
            throw "value is not bool.";
        }
        unsigned long get_int() {
            if (m_type == Type::py_int)
                return std::get<unsigned long>(m_value);
            throw "value is not integer.";
        }
        double get_double() {
            if (m_type == Type::py_float)
                return std::get<double>(m_value);
            throw "value is not double.";
        }
        std::string get_string() {
            if(m_type == Type::py_str)
                return std::get<std::string>(m_value);
            throw "value is not string.";
        }
        std::vector<PValue> get_vector() {
            if (m_type == Type::py_tuple || m_type == Type::py_list)
                return std::get<std::vector<PValue>>(m_value);
            throw "value is not vector.";
        }
        std::unordered_set<PValue> get_set() {
            if (m_type == Type::py_tuple || m_type == Type::py_list)
                return std::get<std::unordered_set<PValue>>(m_value);
            throw "value is not vector.";
        }
        std::unordered_map<std::string, PValue> get_map() {
            if (m_type == Type::py_dict)
                return std::get<std::unordered_map<std::string, PValue>>(m_value);
            throw "value is not dict.";
        }
        py::handle get_object() {
            if (m_type == Type::py_none){
                return py::none();
            }
            else if (m_type == Type::py_bool) {
                return py::bool_(get_bool());
            }
            else if (m_type == Type::py_int) {
                return py::int_(get_int());
            }
            else if (m_type == Type::py_float) {
                return py::float_(get_double());
            }
            else if (m_type == Type::py_str) {
                return py::str(get_string());
            }
            else if (m_type == Type::py_function) {
                return get_function<py::function>();
            }
            else if (m_type == Type::py_tuple) {
                auto vec = get_vector();
                py::tuple tup;
                for (const auto& item : vec){
                    tup.operator+(item->get_object());
                }
                return tup;
            }
            else if (m_type == Type::py_list) {
                auto vec = get_vector();
                py::list list;
                for (const auto& item : vec){
                    list.append(item->get_object());
                }
                return list;
            }
            else if (m_type == Type::py_dict || m_type == Type::py_object) {
                auto map = get_map();
                py::dict dict;
                for (const auto& item : map){
                    dict[py::str(item.first)] = item.second->get_object();
                }
                return dict;
            }
            else {  // (m_type == Type::gg_entity)
                throw std::runtime_error("TValue.get_object(): cannot process entity. Use get_entity() instead.");
            }
        }

        template <typename T>
        std::shared_ptr<T> get_entity() {
            if (std::is_base_of<TEntity, T>::value && m_type == Type::gg_entity) {
                auto ent = std::get<PEntity>(m_value);
                return std::static_pointer_cast<T>(ent);
            }
            throw "value is not an entity.";
        }

        template <typename T>
        T get_function() {
            if (m_type == Type::py_function) {
                auto func = std::get<py::function>(m_value);
                return func.cast<T>();
            }
            throw "value is not an function.";
        }
    };


    class TAttrMap {
    private:
        std::unordered_map<std::string, PValue> m_dict {};

    public:
        TAttrMap() {}
        explicit TAttrMap(const std::unordered_map<std::string, PValue>& dict) : m_dict(dict) {}
        explicit TAttrMap(const py::handle& obj) {
            if (py::isinstance<py::dict>(obj)) {
                auto dict = obj.cast<py::dict>();
                for (const auto& item : dict) {
                    m_dict[item.first.cast<std::string>()] = std::make_shared<TValue>(item.second);
                }
            }
            else {
                throw "TAttrMap constructor expects py::dict.";
            }
        }

        PValue get_attr(const std::string& key){
            auto has_key = m_dict.find(key);
            if (has_key != m_dict.end()) {
                return m_dict[key];
            }
            else {
                throw "TAttrMap.get_attr: key not in dictionary.";
            }
        }

        void set_attr(const std::string& key, const PValue& value) {
            std::cout << "TAttrMap.set_attr(PValue): processing..." << std::endl;
            m_dict[key] = std::move(value);
            std::cout << "TAttrMap.set_attr(PValue): complete." << std::endl;
        }
        void set_attr(const std::string& key, const py::handle& value) {
            std::cout << "TAttrMap.set_attr(py::handle): processing..." << std::endl;
            auto p_value = std::make_shared<TValue>(value);
            m_dict[key] = p_value;
            std::cout << "TAttrMap.set_attr(py::handle): complete" << std::endl;
        }

        void update(const PAttrMap& dict) {

        }

        void update(const py::dict& dict) {

        }

        void update(const std::unordered_map<std::string, PValue>& dict) {

        }

        bool has_key(const std::string& key){
            return m_dict.find(key) != m_dict.end();
        }

        TValue::Type get_type(const std::string& key) {
            if (has_key(key)) {
                return m_dict[key]->get_type();
            }
        }
    };


    class TEntity {
    private:
        PAttrMap m_attr_map;
        const std::vector<std::string> m_special_attr_names {"__entity__"};

    public:
        TEntity() : m_attr_map(std::make_shared<TAttrMap>()) {
            m_attr_map->set_attr("__entity__", std::make_shared<TValue>("TEntity"));
        };
        TEntity(const PAttrMap& attr_map) : m_attr_map(std::make_shared<TAttrMap>()) {
            m_attr_map->set_attr("__entity__", std::make_shared<TValue>("TEntity"));
            m_attr_map->update(attr_map);
        }
        TEntity(const py::handle& attr_map) : m_attr_map(std::make_shared<TAttrMap>()) {
            m_attr_map->set_attr("__entity__", std::make_shared<TValue>("TEntity"));
            if (py::isinstance<py::dict>(attr_map)) {
                m_attr_map->update(attr_map.cast<py::dict>());
            }
        }
        TEntity(const std::unordered_map<std::string, PValue>& attr_map) : m_attr_map(std::make_shared<TAttrMap>()) {
            m_attr_map->set_attr("__entity__", std::make_shared<TValue>("TEntity"));
            m_attr_map->update(attr_map);
        }

        bool is_special_attr(const std::string& key) {
            return std::find(m_special_attr_names.begin(), m_special_attr_names.end(), key) != m_special_attr_names.end();
        }
        bool has_attr(const std::string& key) {
            return m_attr_map->has_key(key);
        }
        TValue::Type get_type(const std::string& key) {
            return m_attr_map->get_type(key);
        }

        void set_attr(const std::string& key, const PValue& value) {
            if (!is_special_attr(key)) {
                std::cout << "TEntity.set_attr(PValue): processing non-special attribute." << std::endl;
                m_attr_map->set_attr(key, value);
            }
            else {
                std::cout << "TEntity.set_attr(PValue): processing special attribute." << std::endl;
                throw std::invalid_argument("TEntity.set_attr() expects a nlohmann::json supported `value` type." );
            }
        }
        void set_attr(const std::string& key, const py::handle& value) {
            if (!is_special_attr(key)) {
                std::cout << "TEntity.set_attr(py::handle): processing non-special attribute." << std::endl;
                m_attr_map->set_attr(key, value);
            }
            else {
                std::cout << "TEntity.set_attr(py::handle): processing special attribute." << std::endl;
                throw std::invalid_argument("TEntity.set_attr() expects a nlohmann::json supported `value` type." );
            }
        }

        PValue get_attr(const std::string& key){
            if (!is_special_attr(key)) {
                return m_attr_map->get_attr(key);
            }
            else {
                throw std::invalid_argument("Attr " + key + " is specialized. Use specialized getter function.");
            }
        }
    };


} // end namespace ggsolver




#endif
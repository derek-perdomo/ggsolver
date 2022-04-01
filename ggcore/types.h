#ifndef GGCORE_TYPES_H
#define GGCORE_TYPES_H

#include <iostream>
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
#include <variant>
#include <memory>
#include <cstdint>
#include <stdexcept>
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
        enum class Type {
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
            set_object(val);
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
            m_type = Type::py_str;
            m_value = val;
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
            if (py::isinstance<nullptr_t>(val) || val.is_none()){
                set_none();
            }
            else if (py::isinstance<py::bool_>(val)) {
                set_bool(val.cast<bool>());
            }
            else if (py::isinstance<py::int_>(val)) {
                set_int(val.cast<unsigned long>());
            }
            else if (py::isinstance<py::float_>(val)) {
                set_double(val.cast<double>());
            }
            else if (py::isinstance<py::str>(val)) {
                set_string(val.cast<std::string>());
            }
            else if (py::isinstance<py::tuple>(val)) {
                std::vector<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.push_back(t_val);
                }

                set_vector(out, Type::py_tuple);
            }
            else if (py::isinstance<py::list>(val)) {
                std::vector<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.push_back(t_val);
                }

                set_vector(out, Type::py_list);
            }
            else if (py::isinstance<py::set>(val)) {
                std::unordered_set<PValue> out;
                for (const py::handle& item : val)
                {
                    PValue t_val = std::make_shared<TValue>(item);
                    out.insert(std::move(t_val));
                }

                set_set(out);
            }
            else if (py::isinstance<py::dict>(val)) {
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
                m_type = Type::py_function;
                m_value = val.cast<py::function>();
            }
            else {
                throw "TValue.set_object() cannot process py::handle. ";
            }
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
                throw "TValue.get_object(): cannot process entity. Use get_entity() instead.";
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

//    class TAttrMap {
//    private:    // representation
//        json m_Attr;                                                // key: value pairs where value is serializable.
//        std::unordered_map<std::string, py::function>  m_Callback;  // key: value pairs where value is py::function.
//
//    public:
//        TAttrMap() {
//            AddHeaders();
//        }
//        explicit TAttrMap(const json& val) {
//            AddHeaders();
//            m_Attr.update(val);
//        }
//        explicit TAttrMap(const py::dict& val) {
//            AddHeaders();
//            ParsePyDict(val);
//        }
//        void AddHeaders() {
//            m_Attr[HEADER_GGSOLVER_VERSION] = Version();
//        }
//        void ParsePyDict(const py::dict& val){
//            for (std::pair<py::handle, py::handle> item : val) {
//                auto key = item.first.cast<std::string>();
//
//                if (py::isinstance<py::function>(item.second)){
//                    m_Callback[key] = item.second.cast<py::function>();
//                }
//                else {
//                    try {
//                        auto value = ToJson(item.second.cast<py::object>());
//                        m_Attr[key] = value;
//                    }
//                    catch (const std::invalid_argument& err) {
//                        throw err;
//                    }
//                }
//            }
//        }
//        json ToJson(const py::object& obj) {
//            if (obj.ptr() == nullptr || obj.is_none()) {
//                return nullptr;
//            }
//            if (py::isinstance<py::bool_>(obj)) {
//                return obj.cast<bool>();
//            }
//            if (py::isinstance<py::int_>(obj)) {
//                return obj.cast<long>();
//            }
//            if (py::isinstance<py::float_>(obj)) {
//                return obj.cast<double>();
//            }
//            if (py::isinstance<py::str>(obj)) {
//                return obj.cast<std::string>();
//            }
//            if (py::isinstance<py::tuple>(obj) || py::isinstance<py::list>(obj) || py::isinstance<py::set>(obj)) {
//                auto array = json::array();
//                for (const py::handle& value : obj) {
//                    array.push_back(ToJson(py::cast<py::object>(value)));
//                }
//                return array;
//            }
//            if (py::isinstance<py::dict>(obj)) {
//                json out;
//                auto dict = py::cast<py::dict>(obj);
//                for (std::pair<py::handle, py::handle> item : dict) {
//                    auto key = item.first.cast<std::string>();
//                    auto value = ToJson(item.second.cast<py::object>());
//                    m_Attr[key] = value;
//                }
//            }
//            throw std::invalid_argument("ToJson received unsupported type for conversion.");
//        }
//        std::vector<std::string> GetKeys(){
//            std::vector<std::string> keys;
//            for (const auto& item : m_Attr.items()) {
//                keys.push_back(item.key());
//            }
//            for (const auto& item: m_Callback){
//                keys.push_back(item.first);
//            }
//            return keys;
//        }
//    };


} // end namespace ggsolver




#endif
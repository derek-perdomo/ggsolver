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

    class TValue;
    class TAttrMap;
    typedef std::shared_ptr<TValue> PValue;
    typedef std::shared_ptr<TAttrMap> PAttrMap;


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
            py_object
        };

        typedef std::variant<
            std::nullptr_t,
            bool,
            unsigned long,
            double,
            std::string,
            std::vector<PValue>,
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
        explicit TValue(const std::vector<PValue>& val) : m_type(Type::py_float), m_value(val) {}
        explicit TValue(const std::unordered_map<std::string, PValue>& val) : m_type(Type::py_float), m_value(val) {}
        explicit TValue(const py::object& val) {
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
        void set_vector(const std::vector<PValue>& val, Type type=Type::py_list) {
            m_type = type;
            m_value = val;
        }
        void set_map(const std::unordered_map<std::string, PValue>& val) {
            m_type = Type::py_dict;
            m_value = val;
        }
        void set_object(const std::unordered_map<std::string, PValue>& val) {

        }
        void set_object(const py::object& val) {

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
            if (m_type == Type::py_tuple || m_type == Type::py_list || m_type == Type::py_set)
                return std::get<std::vector<PValue>>(m_value);
            throw "value is not vector.";
        }
        std::unordered_map<std::string, PValue> get_map() {
            if (m_type == Type::py_dict)
                return std::get<std::unordered_map<std::string, PValue>>(m_value);
            throw "value is not dict.";
        }
        std::unordered_map<std::string, PValue> get_object() {

        }
    };

    class TAttrMap {
    private:    // representation
        json m_Attr;                                                // key: value pairs where value is serializable.
        std::unordered_map<std::string, py::function>  m_Callback;  // key: value pairs where value is py::function.

    public:
        TAttrMap() {
            AddHeaders();
        }
        explicit TAttrMap(const json& val) {
            AddHeaders();
            m_Attr.update(val);
        }
        explicit TAttrMap(const py::dict& val) {
            AddHeaders();
            ParsePyDict(val);
        }
        void AddHeaders() {
            m_Attr[HEADER_GGSOLVER_VERSION] = Version();
        }
        void ParsePyDict(const py::dict& val){
            for (std::pair<py::handle, py::handle> item : val) {
                auto key = item.first.cast<std::string>();

                if (py::isinstance<py::function>(item.second)){
                    m_Callback[key] = item.second.cast<py::function>();
                }
                else {
                    try {
                        auto value = ToJson(item.second.cast<py::object>());
                        m_Attr[key] = value;
                    }
                    catch (const std::invalid_argument& err) {
                        throw err;
                    }
                }
            }
        }
        json ToJson(const py::object& obj) {
            if (obj.ptr() == nullptr || obj.is_none()) {
                return nullptr;
            }
            if (py::isinstance<py::bool_>(obj)) {
                return obj.cast<bool>();
            }
            if (py::isinstance<py::int_>(obj)) {
                return obj.cast<long>();
            }
            if (py::isinstance<py::float_>(obj)) {
                return obj.cast<double>();
            }
            if (py::isinstance<py::str>(obj)) {
                return obj.cast<std::string>();
            }
            if (py::isinstance<py::tuple>(obj) || py::isinstance<py::list>(obj) || py::isinstance<py::set>(obj)) {
                auto array = json::array();
                for (const py::handle& value : obj) {
                    array.push_back(ToJson(py::cast<py::object>(value)));
                }
                return array;
            }
            if (py::isinstance<py::dict>(obj)) {
                json out;
                auto dict = py::cast<py::dict>(obj);
                for (std::pair<py::handle, py::handle> item : dict) {
                    auto key = item.first.cast<std::string>();
                    auto value = ToJson(item.second.cast<py::object>());
                    m_Attr[key] = value;
                }
            }
            throw std::invalid_argument("ToJson received unsupported type for conversion.");
        }
        std::vector<std::string> GetKeys(){
            std::vector<std::string> keys;
            for (const auto& item : m_Attr.items()) {
                keys.push_back(item.key());
            }
            for (const auto& item: m_Callback){
                keys.push_back(item.first);
            }
            return keys;
        }
    };


} // end namespace ggsolver




#endif
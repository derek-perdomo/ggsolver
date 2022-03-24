#ifndef GGCORE_TYPES_H
#define GGCORE_TYPES_H

#include <iostream>
#include <algorithm>
#include <string>
#include <utility>
#include <vector>
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

    class TAttrMap;
    typedef std::shared_ptr<TAttrMap> PAttrMap;


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
//
// Created by Abhishek on 31-Mar-22.
//

#include <iostream>
#include <variant>
#include <vector>
#include <unordered_set>
#include <unordered_map>
#include <memory>
#include <pybind11/pybind11.h>
#include <nlohmann/json.hpp>


using json = nlohmann::json;
namespace py = pybind11;


class TValueVariant;
class TValuePyObject;
typedef std::shared_ptr<TValueVariant> PValueVariant;


class TValueVariant {
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
            std::shared_ptr<std::string>,
            std::shared_ptr<std::vector<PValueVariant>>,
            std::shared_ptr<std::unordered_map<std::string, PValueVariant>>
    > Value;

private:
    Type m_type;
    Value m_value;

};


class TValuePyObject {
private:
    py::object m_obj;
};


class TValueJSON {
private:
    json m_obj;
};







int main() {
    TValueVariant variant_;
    TValuePyObject py_object_;
    TValuePyObject json_;

    std::cout << "variant " << sizeof(variant_) << " bytes" << std::endl;
    std::cout << "py_object " << sizeof(py_object_) << " bytes" << std::endl;
    std::cout << "json " << sizeof(json_) << " bytes" << std::endl;
}
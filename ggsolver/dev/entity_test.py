from ggsolver import TEntity

ent0 = TEntity()
print("ent0.is_special_attr('name'):", ent0.is_special_attr("name"))
print("ent0.is_special_attr('noname'):", ent0.is_special_attr("noname"))
ent0.set_attr("bool", True)
print("ent0.has_attr('bool'): ", ent0.has_attr('bool'))
print("ent0.get_attr('bool'): ", ent0.get_attr('bool'))
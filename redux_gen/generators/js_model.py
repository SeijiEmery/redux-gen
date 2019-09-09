
class JSEntity:
    pass


class JSTypeInfo(JSEntity):
    pass


class JSConcreteEntity(JSEntity):
    pass


class Stmt(JSConcreteEntity):
    pass


class Expr(Stmt):
    def __init__(self, value):
        self.value = value


def enforce_type(expr, type_):
    if type(expr) != type_ and not isinstance(expr, type_):
        raise Exception("invalid type: expected %s, got %s" % (
            type_, type(expr)))


def enforce_list_of(expr, type_):
    enforce_type(expr, list)
    for elem in expr:
        enforce_type(elem, type_)


class Type(JSTypeInfo):
    def __init__(self, name):
        self.name = name
        # enforce_type(name, str)


class Export(JSEntity):
    def __init__(self, item):
        self.item = item
        enforce_type(item, JSConcreteEntity)


class TypedParam(JSTypeInfo):
    def __init__(self, name, type_):
        self.name = name
        self.type = type_
        enforce_type(name, str)
        enforce_type(type_, Type)


class InterfaceDecl(JSTypeInfo):
    def __init__(self, name, members):
        self.name = name
        self.members = members
        enforce_type(name, str)
        enforce_list_of(members, TypedParam)


class EnumKey(JSConcreteEntity):
    def __init__(self, enum_decl, value):
        self.enum_decl = enum_decl
        self.value = value
        enforce_type(enum_decl, EnumDecl)
        enforce_type(value, str)


class EnumDecl(JSTypeInfo):
    def __init__(self, type_, members):
        self.type = type_
        self.members = members
        enforce_type(type_, Type)
        enforce_list_of(members, EnumKey)


class FunctionDefn(JSConcreteEntity):
    def __init__(self, name, params, return_type, body):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.body = body
        enforce_type(name, str)
        enforce_list_of(params, TypedParam)
        enforce_type(return_type, Type)
        enforce_type(body, Stmt)


class Return(Stmt):
    def __init__(self, expr):
        self.expr = expr
        enforce_type(expr, Expr)


class MatchStmt(Stmt):
    def __init__(self, enum, expr, cases):
        self.enum = enum
        self.expr = expr
        self.cases = cases
        enforce_type(enum, EnumDecl)
        enforce_type(expr, Expr)
        enforce_list_of(cases, MatchCase)


class MatchCase(Stmt):
    def __init__(self, case, expr):
        self.case = case
        self.expr = expr
        enforce_type(case, EnumKey)
        enforce_type(expr, Stmt)


class ObjectInitializer(Expr):
    def __init__(self, object_type, *key_only_fields, **kv_fields):
        self.object_type = object_type
        self.key_only_fields = key_only_fields
        self.kv_fields = kv_fields
        enforce_type(object_type, InterfaceDecl)
        # enforce_list_of(list(key_only_fields), str)
        # enforce_dict_of(kv_fields, Expr)


class PartialObjectInitializer(ObjectInitializer):
    def __init__(self, origin, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.origin = origin
        enforce_type(origin, str)


class ActionExpr(Expr):
    def __init__(self, name, expr):
        self.name = name
        self.expr = expr



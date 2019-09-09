from generators.renderer_hooks import renderer, create_target
from generators.js_model import *
from generators.javascript import Javascript

Typescript = create_target(derive_from=Javascript)
TypescriptEnums = create_target()


@renderer(Typescript, Type)
def render_typescript_type(t, context):
    def render_type(t):
        if type(t) == dict:
            return context.render_dict_type(', '.join([
                '%s: %s' % (k, render_type(v))
                for k, v in t.items()
            ]))
        if type(t) == list:
            return context.render_list_type(', '.join(
                map(render_type, t)))
        return context.render_basic_type(t)
    return render_type(t.name)


@renderer(Typescript, TypedParam)
def render_typescript_param(param, context):
    return '%s: %s' % (param.name, context.render(param.type))


@renderer(Typescript, InterfaceDecl)
def render_typescript_interface_decl(interface, context):
    return 'interface %s { %s }' % (
        interface.name, ''.join([
            '%s;' % context.render(param)
            for param in interface.members
        ]))


@renderer(Typescript, FunctionDefn)
def render_typescript_function_defn(fcn, context):
    return 'function %s (%s) -> %s { %s }' % (
        fcn.name, ', '.join([
            context.render(param)
            for param in fcn.params
        ]),
        context.render(fcn.return_type),
        context.render(fcn.body))

@renderer(Typescript, EnumDecl)
def render_typescript_enum_defn(enum, context):
    return 'type %s = %s;'%(
        context.render(enum.type),
        ' | '.join(context.render(enum.members)))

@renderer(TypescriptEnums, EnumKey)
def render_enum_key(key, context):
    return '%s.%s'%(
        str(context.render(key.enum_decl.type)),
        key.value)

@renderer(TypescriptEnums, EnumDecl)
def render_enum_decl(enum, context):
    return 'enum %s { %s }'%(
        context.render(enum.type),
        ', '.join([ item.value for item in enum.members ]))

@renderer(TypescriptEnums, EnumTypeOf)
def render_enum_typeof(enum, context):
    # bypass normal enum key rendering (ie. SomeType.ELEMENT)
    # to just render the type (ie. SomeType) in specific situations
    # (ie. object type defns)
    #
    # Exists b/c in the default mode (string enums), types are given
    # like this:
    # (default) { type: 'SOME_ELEMENT' }
    #
    # wrong:    { type: SomeType.ELEMENT }
    # correct:  { type: SomeType }
    return context.render(enum.enum_key.enum_decl.type)



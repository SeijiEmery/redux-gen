from generators.renderer_hooks import renderer, create_target
from generators.js_model import *
from generators.javascript import Javascript

Typescript = create_target(derive_from=Javascript)


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
    return 'export interface %s { %s }' % (
        interface.name, ''.join([
            '%s;' % context.render(param)
            for param in interface.members
        ]))


@renderer(Typescript, FunctionDefn)
def render_typescript_function_defn(fcn, context):
    return 'export function %s (%s) -> %s { %s }' % (
        fcn.name, ', '.join([
            context.render(param)
            for param in fcn.params
        ]),
        context.render(fcn.return_type),
        context.render(fcn.body))



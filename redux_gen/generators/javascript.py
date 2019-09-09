from generators.renderer_hooks import renderer, create_target
from generators.js_model import *

Javascript = create_target()


@renderer(Javascript, TypedParam)
def render_param(param, context):
    return param.name


@renderer(Javascript, EnumKey)
def render_enum_value(key, context):
    return "'%s'" % key.value


@renderer(Javascript, EnumTypeOf)
def render_enum_pass_through(key, context):
    return context.render(key.enum_key)


@renderer(Javascript, Export)
def render_export(export, context):
    return 'export %s' % context.render(export.item)


@renderer(Javascript, Expr)
def render_expr(expr, context):
    return str(expr.value)


@renderer(Javascript, FunctionDefn)
def render_function_defn(fcn, context):
    params = ', '.join(context.render(fcn.params))
    body = context.render(fcn.body)
    return 'function %s (%s) { %s }' % (fcn.name, params, body)


@renderer(Javascript, Return)
def render_return(stmt, context):
    return 'return %s;' % (context.render(stmt.expr))


@renderer(Javascript, MatchStmt)
def render_match_stmt(stmt, context):
    return 'switch(%s) { %s }' % (
        context.render(stmt.expr),
        ' '.join(context.render(stmt.cases)))


@renderer(Javascript, MatchCase)
def render_match_case(stmt, context):
    return 'case %s: %s' % (
        context.render(stmt.case),
        context.render(stmt.expr))


@renderer(Javascript, ObjectInitializer)
def render_object_initializer(stmt, context):
    return '{ %s }' % (
        ', '.join([str(context.render(v)) for v in stmt.key_only_fields] + [
            ('%s: %s') % (k, str(context.render(v)))
            for k, v in stmt.kv_fields.items()
        ]))

@renderer(Javascript, PartialObjectInitializer)
def render_partial_object_initializer(stmt, context):
    return '{ %s, %s... }' % (
        ', '.join([str(context.render(v)) for v in stmt.key_only_fields] + [
            ('%s: %s') % (k, str(context.render(v)))
            for k, v in stmt.kv_fields.items()
        ]), stmt.origin)


@renderer(Javascript, ActionExpr)
def render_typescript_action_expr(action, context):
    if type(action.expr) == dict:
        for k, expr in action.expr.items():
            return {
                'set': lambda: str(expr),
                'map': lambda: 'state.%s.map(%s)'%(action.name, expr),
                'filter': lambda: 'state.%s.filter(%s)'%(action.name, expr),
                'append': lambda: 'state.%s.concat(%s)'%(action.name, expr),
            }[k]()
    return str(action.expr)

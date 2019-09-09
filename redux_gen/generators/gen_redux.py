from generators.js_model import Expr, Type, TypedParam, Export, InterfaceDecl, \
    EnumDecl, EnumKey, FunctionDefn, Return, MatchStmt, MatchCase, \
    ObjectInitializer, PartialObjectInitializer, ActionExpr


def gen_redux_states_and_actions(renderer, file_name, state, actions, config):

    State = Type(config.names('State', file_name))
    Actions = Type(config.names('Actions', file_name))
    reducer = config.names('reducer', file_name)

    state = [TypedParam(config.names('var', k), Type(v))
             for k, v in state.items()]

    action_enum = EnumDecl(Actions, [])

    # print(actions)
    actions = {name: {
        'params': [TypedParam(config.names('var', k), Type(v)) for k, v in action['params'].items()],
        'reduce': {config.names('var', k): v for k, v in action['reduce'].items()},
        'param_type': Type(config.names('Action', name)),
        'fcn_name': config.names('action', name),
        'ENUM_ID': EnumKey(action_enum, config.names('ACTION', name)),
    } for name, action in actions.items()}

    state_type = InterfaceDecl(State.name, state)
    action_types = {
        name: InterfaceDecl(action['param_type'].name, action['params'])
        for name, action in actions.items()
    }
    action_enum.members = [
        action['ENUM_ID'] for action in actions.values()
    ]
    action_ctors = [
        FunctionDefn(
            name=action['fcn_name'],
            params=action['params'],
            return_type=action['param_type'],
            body=Return(ObjectInitializer(action_types[name], [
                param.type.name for param in action['params']
            ], type=action['ENUM_ID'])))
        for name, action in actions.items()
    ]
    reducer_fcn = FunctionDefn(
        name=reducer,
        params=[TypedParam('state', State), TypedParam('action', Actions)],
        return_type=State,
        body=MatchStmt(action_enum, Expr('state.type'), [
            MatchCase(
                action['ENUM_ID'],
                Return(PartialObjectInitializer('state', state_type, **{
                    k: ActionExpr(k, v)
                    for k, v in action['reduce'].items()
                })))
            for action in actions.values()
        ]))

    if config.target_single_file:
        renderer.write_file(config.out_path(),
                            state_type, action_types, action_enum, action_ctors, reducer_fcn)
    else:
        types = renderer.write_file(config.out_path(
            'types'), state_type, action_types, action_enum)
        actions = renderer.write_file(config.out_path(
            'actions'), action_ctors, imports=types)
        reducer = renderer.write_file(config.out_path(
            'reducer'), reducer_fcn, imports=types)
        index = renderer.write_file(config.out_path('index'), imports=[types, actions, reducer])




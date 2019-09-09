import yaml
import re
import os
from utils.name_utils import reformat


lower_camel_case = lambda name: reformat(name, 'camel')
upper_camel_case = lambda name: reformat(name, 'pascal')
lower_underscores = lambda name: reformat(name, 'lower')
upper_underscores = lambda name: reformat(name, 'upper')


def redux_gen(file, out_dir):
    with open(file) as f:
        spec = yaml.load(f.read())
    # print(spec)
    # validate(spec, validation_spec)

    file_name = os.path.split(file)[1].split('.')[0]

    file_name = upper_camel_case(file_name)
    file_name_plural = file_name if file_name.endswith(
        's') else file_name + 's'
    file_name_singular = file_name[:-
                                   1] if file_name.endswith('s') else file_name

    state_type_name = '{}State'.format(file_name_singular)
    actions_type_name = '{}Actions'.format(file_name_singular)

    def action_fcn_name(action): return lower_camel_case(action)

    def action_type_name(action): return '{}Action'.format(
        upper_camel_case(action))

    def action_string_type(action): return upper_underscores(action)
    reducer_fcn_name = spec['reducer_name'] if 'reducer_name' in spec else 'reduce' + file_name_plural

    def enforcement(exception=Exception):
        def enforce(cond, msg, *args, **kwargs):
            if not cond:
                raise exception(msg.format(*args, **kwargs))
        return enforce

    def make_type(obj):
        type_map = {'string': 'String', 'number': 'Number'}
        if type(obj) == str:
            if obj in type_map:
                return type_map[obj]
            return obj
        if type(obj) == list:
            return 'List<{}>'.format(', '.join(map(make_type, obj)))
        if type(obj) == dict:
            return '{ %s }' % (', '.join([
                '%s: %s' % (key, make_type(value))
                for key, value in obj.items()
            ]))
        return str(obj)

    def validate(spec):
        enforce = enforcement()
        enforce('state' in spec, "missing state defn")
        enforce(type(spec['state']) == dict, "invalid state defn")
        enforce(type(spec['actions']) == dict, "invalid actions defn")

    def gen_state_type(spec):
        return 'export interface {StateNameUpper} {{{content}\n}}'.format(
            StateNameUpper=state_type_name,
            content=''.join([
                '\n\t{key}: {type}'.format(
                    key=var_name, type=make_type(var_type))
                for var_name, var_type in spec['state'].items()
            ]))

    def gen_action_types(spec):
        return '\n'.join([
            'export interface {ActionNameUpper} {{{content}}}'.format(
                ActionNameUpper=action_type_name(action_name),
                content=''.join(
                    ['\n\ttype: %s' % (make_type('string'))] + [
                        '\n\t{key}: {type}'.format(
                            key=var_name, type=make_type(var_type))
                        for var_name, var_type in action_spec['params'].items()
                    ]) + '\n' if 'params' in action_spec else ''
            )
            for action_name, action_spec in spec['actions'].items()
        ]) + '\nexport type {ActionsNameUpper}\n\t= {types};\n'.format(
            ActionsNameUpper=actions_type_name,
            types='\n\t| '.join([
                '%sAction' % upper_camel_case(action_name)
                for action_name in spec['actions'].keys()
            ])
        )

    def gen_action_ctors(spec):
        return '\n'.join([
            'export function {actionName} ({params}) -> {ActionType} {{\n\t{body}\n}}'.format(
                actionName=action_fcn_name(action_name),
                ActionType=action_type_name(action_name),
                params=', '.join([
                    '{name}: {var}'.format(name=name, var=make_type(var_type))
                    for name, var_type in action_spec['params'].items()
                ]),
                body="return {{ type: '{STRING_TYPE}', {params} }};".format(
                    STRING_TYPE=action_string_type(action_name),
                    params=', '.join(action_spec['params'].keys())
                )
            )
            for action_name, action_spec in spec['actions'].items()
        ])

    def gen_action_reducer(spec):
        def gen_reducer_action(action_spec):
            def gen_action(state_var, action):
                if type(action) == dict:
                    if 'set' in action:
                        return action['set']
                    if 'append' in action:
                        return 'state.{name}.concat({expr})'.format(
                            name=state_var, expr=action['append'].strip())
                    if 'map' in action:
                        return 'state.{name}.map({expr})'.format(
                            name=state_var, expr=action['map'].strip())
                    if 'filter' in action:
                        return 'state.{name}.map({expr})'.format(
                            name=state_var, expr=action['map'].strip())
                return str(action)

            return ''.join([
                '\n\t\t\t{name}: {value}'.format(
                    name=name,
                    value=gen_action(name, action)
                )
                for name, action in action_spec.items()
            ])

        return '\n'.join([
            'export function {reducerName} (state: {StateType}, action: {ActionType}) -> {StateType} {{\n\t{body}\n}}'.format(
                reducerName=reducer_fcn_name,
                StateType=state_type_name,
                ActionType=actions_type_name,
                body='switch (state.type) {{\n\t\t{cases}\n\t}}'.format(
                    cases=''.join([
                        "case '{ACTION_TYPE}': return {{{elems}\n\t\t\tstate...\n\t\t}};\n\t\t".format(
                            ACTION_TYPE=action_string_type(action_name),
                            elems=gen_reducer_action(action_spec['reduce']))
                        for action_name, action_spec in spec['actions'].items()
                    ])
                )
            )
        ])

    validate(spec)
    print(gen_state_type(spec))
    print(gen_action_types(spec))
    print(gen_action_ctors(spec))
    print(gen_action_reducer(spec))


if __name__ == '__main__':
    redux_gen('../test/samples/todo.yaml', 'test/out/todo')

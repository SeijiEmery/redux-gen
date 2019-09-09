import yaml
import re
import os
from utils.name_utils import reformat
# from types import make_type
import yamale

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


def redux_gen(file, out_dir):
    with open(file) as f:
        spec = yaml.load(f.read())

    def validate(spec):
        schema = yamale.make_schema('../schema.yaml')
        schema.validate(spec, file, True)

    # make_type = type_converter('typescript')

    file_name = os.path.split(file)[1].split('.')[0]
    names = {
        'StateType': reformat(file_name, 'pascal', noun_form='singular', with_suffix='State'),
        'ActionEnumType': reformat(file_name, 'pascal', noun_form='plural', with_suffix='Actions'),
        'reducerFunction': spec['reducer_name'] if 'reducer_name' in spec else \
            reformat(file_name, 'camel', noun_form='singular', with_prefix='reduce'),
        'ActionType': lambda action: reformat(action, 'pascal', with_suffix='Action'),
        'actionFunctionName': lambda action: reformat(action, 'camel'),
        'ACTION_ENUM': lambda action: "'%s'"%reformat(action, 'upper'),
    }

    def enforcement(exception=Exception):
        def enforce(cond, msg, *args, **kwargs):
            if not cond:
                raise exception(msg.format(*args, **kwargs))
        return enforce

    def gen_state_type(spec):
        return 'export interface {StateNameUpper} {{{content}\n}}'.format(
            StateNameUpper=names['StateType'],
            content=''.join([
                '\n\t{key}: {type}'.format(
                    key=var_name, type=make_type(var_type))
                for var_name, var_type in spec['state'].items()
            ]))

    def gen_action_types(spec):
        return '\n'.join([
            'export interface {ActionNameUpper} {{{content}}}'.format(
                ActionNameUpper=names['ActionType'](action_name),
                content=''.join(
                    ['\n\ttype: %s' % (make_type('string'))] + [
                        '\n\t{key}: {type}'.format(
                            key=var_name, type=make_type(var_type))
                        for var_name, var_type in action_spec['params'].items()
                    ]) + '\n' if 'params' in action_spec else ''
            )
            for action_name, action_spec in spec['actions'].items()
        ]) + '\nexport type {ActionsNameUpper}\n\t= {types};\n'.format(
            ActionsNameUpper=names['ActionEnumType'],
            types='\n\t| '.join([
                names['ActionType'](action_name)
                for action_name in spec['actions'].keys()
            ])
        )

    def gen_action_ctors(spec):
        return '\n'.join([
            'export function {actionName} ({params}) -> {ActionType} {{\n\t{body}\n}}'.format(
                actionName=names['actionFunctionName'](action_name),
                ActionType=names['ActionType'](action_name),
                params=', '.join([
                    '{name}: {var}'.format(name=name, var=make_type(var_type))
                    for name, var_type in action_spec['params'].items()
                ]),
                body="return {{ type: {ACTION_ENUM}, {params} }};".format(
                    ACTION_ENUM=names['ACTION_ENUM'](action_name),
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
                reducerName=names['reducerFunction'],
                StateType=names['StateType'],
                ActionType=names['ActionEnumType'],
                body='switch (state.type) {{\n\t\t{cases}\n\t}}'.format(
                    cases=''.join([
                        "case {ACTION_ENUM}: return {{{elems}\n\t\t\tstate...\n\t\t}};\n\t\t".format(
                            ACTION_ENUM=names['ACTION_ENUM'](action_name),
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

import yaml
import yamale
import pprint
import jsbeautifier

pp = pprint.PrettyPrinter(indent=4)
def pretty_print(*args, **kwargs):
    pp.pprint(*args, **kwargs)


def update_recursive(target, src):
    for k, v in src.items():
        if type(v) == dict:
            if k not in target:
                target[k] = {}
            update_recursive(target[k], src[k])
        else:
            target[k] = v


def load_configs():
    with open('dialects/typescript.yaml') as f:
        configs = {}
        features = {}
        for config in yaml.load_all(f):
            for root in config.keys():
                if root.startswith('feature '):
                    features[' '.join(root.split(' ')[1:])] = config[root]
                else:
                    configs[root] = config[root]
    return configs, features

def load_config(lang, *features):
    features = set(features)
    configs, config_features = load_configs()

    def build_dep_order(lang):
        if lang not in configs:
            raise Exception("invalid language target '%s'"%lang)        
        config = configs[lang]
        deps = config['inheirit'] if 'inheirit' in config else []
        if type(deps) != list:
            deps = [deps]
        dep_order = []
        for dep in reversed(deps):
            dep_order += build_dep_order(dep)
        dep_order += [lang]
        return dep_order

    # build lang dependencies in order
    config = {}
    for dep in build_dep_order(lang):
        # print("Adding dep %s"%dep)
        update_recursive(config, configs[dep])
        # pretty_print(config)

    # add feature deps
    for feature in features:
        # print("adding feature %s"%feature)
        update_recursive(config, config_features[feature])
        # pretty_print(config)
    return config

def generate(config, names, state, actions):
    syntax = config['syntax']
    # print(list(config.keys()))
    type_conv = config['types']['decl']
    type_conv = { k: v.strip() for k, v in type_conv.items() }

    def format_type(t):
        if type(t) == dict:
            return type_conv['dict'].replace('...', ', '.join([
                '%s: %s'%(k, format_type(v))
                for k, v in t.items()
            ]))
        if type(t) == list:
            return type_conv['list'].replace('...', ', '.join(
                map(format_type, t)))
        if t in type_conv:
            return type_conv[t]
        return t

    def gen_interface(name, members):
        return (syntax['interface-decl'].strip()
            .replace('$name', name)
            .replace('$body', ' '.join([
                syntax['interface-elem'].strip()
                    .replace('$name', name)
                    .replace('$type', format_type(type))
                    for name, type in members.items()
                ])))

    def gen_enum(name, elements):
        return (syntax['enum']['decl'].strip()
            .replace('$type', name)
            .replace('$body', ' '.join([
                (syntax['enum']['decl_elem_0']
                if i == 0 else
                syntax['enum']['decl_elem'])
                    .strip()
                    .replace('$elem', elem)
                for i, elem in enumerate(elements)
            ])))

    def gen_fcn(name, params, return_type, body):
        return (syntax['fcn-signatures'].strip()
            .replace('$name', name)
            .replace('$params', ', '.join([
                syntax['type-signatures'].strip()
                    .replace('$var', name)
                    .replace('$type', format_type(type))
                for name, type in params.items()
            ]))
            .replace('$return-type', return_type)
            .replace('$body', body))

    def printjs(js):
        print(js)
        # print(jsbeautifier.beautify(js))

    printjs(gen_interface(names['StateType'], state))
    for name, action in actions.items():
        elem = 'ACTION_ELEM'
        params = { 'type': syntax['enum']['decl_type']
            .replace('$type', names['ActionEnumType'])
            .replace('$elem', elem)
        }
        params.update(action['params'])
        printjs(gen_interface(name, params))
    printjs(gen_enum(names['ActionEnumType'], [
        action for action in actions.keys()
    ]))
    for name, action in actions.items():
        printjs(gen_fcn(name, action['params'], name+'Action',
            syntax['action-ctor-body'].strip()
                .replace('$type', name+'Action')
                .replace('$elem', 'ACTION_ELEM')
                .replace('$params', ', '.join(action['params'].keys()))
            ))

    State, Actions = names['StateType'], names['ActionEnumType']

    def build_action(name, result):
        # print(name, result)
        if type(result) == dict:
            for key, expr in result.items():
                return (config['action-extensions'][key].strip()
                    .replace('$var', name)
                    .replace('$expr', expr))
        return str(result)

    State, Action = names['StateType'], names['ActionEnumType']
    printjs(gen_fcn('reducer', { 'state': State, 'action': Action }, State,
        syntax['enum']['match'].strip()
            .replace('$expr', 'state.type')
            .replace('$body', ' '.join([
                syntax['enum']['match-case'].strip()
                    .replace('$type', 'ActionType')
                    .replace('$elem', 'ACTION_ELEM')
                    .replace('$expr', syntax['reducer-state-return'].strip()
                        .replace('$cases', ''.join([
                            syntax['reducer-state-var'].strip()
                                .replace('$var', name)
                                .replace('$expr', build_action(name, result))
                            for name, result in action['reduce'].items()
                        ])))
                for action_name, action in actions.items()
            ])
        )))



if __name__ == '__main__':
    # load_config()
    for options in [
        [ 'typescript' ],
        [ 'typescript', 'typescript-enums' ],
        [ 'javascript' ], 
    ]:
        print()
        print(options)
        generate(load_config(*options),
            { 'StateType': 'FooState', 'ActionEnumType': 'FooActions' },
            { 'foo': 'string', 'bar': [{ 'a': 'number', 'b': 'string' }] },
            { 
                'add pillows': { 'params': { 'a': 'number' }, 'reduce': { 'foo': { 'append': 'fubar' } } },
                'add more pillows': { 'params': { 'a': 'number' }, 'reduce': { 'foo': '"fubar"' } },
            }
        )
    # pretty_print(load_config('typescript', 'string-enums'))

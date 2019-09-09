from generators.gen_redux import gen_redux_states_and_actions
from generators.javascript import Javascript
from utils.name_utils import reformat
import yaml
import yamale


def load_yaml(file):
    with open(file) as f:
        spec = yaml.load(f.read())
        schema = yamale.make_schema('../schema.yaml')
        schema.validate(spec, file, True)
        file_name = os.path.split(file)[1].split('.')[0]
        return file_name, spec


def from_keys(**kwargs):
    return kwargs


class Config:
    def __init__(self, target_single_file=True):
        self.name_config = from_keys(
            State=from_keys(fmt='pascal', with_suffix='State'),
            Actions=from_keys(fmt='pascal', with_suffix='Actions'),
            reducer=from_keys(fmt='camel', with_prefix='reduce'),
            var=from_keys(fmt='camel'),
            action=from_keys(fmt='camel'),
            Action=from_keys(fmt='pascal', with_suffix='Action'),
            ACTION=from_keys(fmt='upper'),
        )
        self.target_single_file = target_single_file

    def names(self, preset, name):
        if preset not in self.name_config:
            raise Exception("missing name preset '%s'", preset)
        return reformat(name, **self.name_config[preset])


if __name__ == '__main__':
    file, spec = load_yaml('../test/examples/todo.yaml')
    config = Config()
    renderer = Javascript
    gen_redux_states_and_actions(renderer, file, spec['state'], spec['actions'], config)


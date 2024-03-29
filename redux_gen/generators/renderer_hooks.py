import jsbeautifier
from generators.js_model import Export

def renderer(target, model):
    def renderer(fcn):
        target.add_renderer(model, fcn)
    return renderer


class Target():
    def __init__(self, derive_from=None):
        self.renderers = {}
        if derive_from is not None:
            if not isinstance(derive_from, Target):
                raise Exception("Attempting to derive from invalid type %s"%type(derive_from))
            self.renderers.update(derive_from.renderers)
        self.add_renderer(str, lambda value, _: value)
        self.add_renderer(dict, lambda values, ctx: {
            k: ctx.render(v) for k, v in values.items()
        })
        self.add_renderer(list, lambda values, ctx: [
            ctx.render(item) for item in values])

    def __and__(self, other):
        new_target = Target(derive_from=self)
        new_target.renderers.update(other.renderers)
        return new_target

    def render_dict_type(self, contents):
        return '{ %s }'%contents

    def render_list_type(self, contents):
        return 'Array<%s>'%contents

    def render_basic_type(self, type_):
        return str(type_)

    def add_renderer(self, model, fcn):
        self.renderers[str(model)] = fcn

    def render(self, obj):
        type_key = str(type(obj))
        if type_key in self.renderers:
            return self.renderers[type_key](obj, self)
        print("No renderer for %s, %s!"%(
            type_key, obj))

    def write_file(self, path, *objects, imports=None):
        def write(obj):
            print(jsbeautifier.beautify(str(self.render(Export(obj)))))

        def write_recursive(objects):
            for obj in objects:
                if type(obj) == list:
                    write_recursive(obj)
                elif type(obj) == dict:
                    write_recursive(obj.values())
                else:
                    write(obj)
        write_recursive(objects)




def create_target(*args, **kwargs):
    return Target(*args, **kwargs)

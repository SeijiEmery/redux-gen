import re


def reformat(name, fmt):
    return {
        'camel': lower_camel_case,
        'pascal': upper_camel_case,
        'lower': lower_underscores,
        'upper': upper_underscores,
        'space': lower_space_separated,
    }[fmt](name)


def upper_camel_case(name):
    """ Converts a name / identifier into UpperCamelCase (aka PascalCase). """
    return ''.join([
        component[0].upper() + component[1:].lower()
        for component in split_name(name)
    ])


def lower_camel_case(name):
    """ Converts a name / identifier into lowerCamelCase. """
    return ''.join([
        component.lower() if i == 0 else
        component[0].upper() + component[1:].lower()
        for i, component in enumerate(split_name(name))
    ])


def lower_underscores(name):
    """ Converts a name / identifier into lower_case_with_underscores. """
    return '_'.join([component.lower() for component in split_name(name)])


def upper_underscores(name):
    """ Converts a name / identifier into UPPER_CASE_WITH_UNDERSCORES. """
    return '_'.join([component.upper() for component in split_name(name)])


def lower_space_separated(name):
    """" Converts a name / identifier into 'lower case space separated'.

    Default case used for yaml keys (because it's pretty, and why not).
    Highly unlikely we will use this to generate anything, but it is an option.
    """
    return ' '.join([component.lower() for component in split_name(name)])


def split_name(name):
    """ Splits a PL name / identifier into its constituent words, using
    programming language conventions to handle pascal / camel case,
    upper / lower case with underscores, AND whitespace separated
    identifiers (ie. yaml key strings).

    Used to implement utilities that let us freely change the naming
    convention of programming identifiers used in yaml files for
    redux-gen.

    ie. "hello world" <=> "helloWorld" <=> "HELLO_WORLD"
        <=> "HelloWorld" <=> "hello_world" <=> [ "hello", "world" ]

    Specific edge cases that we are aware of and have worked around:

    Pascal single letter identifiers / acronyms

        "IFoo" => "I", "Foo"
        "UIPACFoo" => "IUPAC", "Foo"

    Mixed case reverse

        "uiFOO" => "ui", "FOO"

    The only case we do NOT handle correctly:

        "FOObar" => "FO", "Obar"

    (it's impossible to handle this and pascal correctly)
    """
    def split_camel_case(s):
        found_split = True
        while found_split and len(s) > 1:
            found_split = False
            if s[0].isupper() and s[1].islower():
                for i in range(1, len(s)):
                    if s[i].isupper():
                        yield s[:i]
                        s = s[i:]
                        found_split = True
                        break
            else:
                upper = s[0].isupper()
                for i in range(1, len(s)):
                    if s[i].isupper() != upper:
                        if upper:
                            word, s = s[:i - 1], s[i - 1:]
                        else:
                            word, s = s[:i], s[i:]
                        yield word
                        found_split = True
                        break
        if s:
            yield s

    def split_parts():
        for component in re.split(r'[\s_\-]+', name):
            for component in split_camel_case(component):
                yield component
    return list(split_parts())


if __name__ == '__main__':
    # Basic ad-hoc tests. Full unittests TBD
    for name in [
        'f', 'foo', 'fBar', 'fooBar',
        'foo-bar', 'foo_bar', 'FOO_BAR',
        'FOObar', 'FOOBar', 'fooBAR'
    ]:
        print('%s => %s => %s => %s, %s => %s, %s => %s, %s => %s' % (
            name, split_name(name),
            upper_camel_case(name), split_name(upper_camel_case(name)),
            lower_camel_case(name), split_name(lower_camel_case(name)),
            lower_underscores(name), split_name(lower_underscores(name)),
            upper_underscores(name), split_name(upper_underscores(name)),
        ))

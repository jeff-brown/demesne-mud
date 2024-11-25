class _Container(object):
    """
    Utility class to provide for __repl__ in config options.
    """

    def __repr__(self):
        type_name = type(self).__name__
        string_args = []
        dict_args = {}

        for arg in self._get_args():
            string_args.append(repr(arg))

        for key, value in self._get_kwargs():
            if key.isidentifier():
                string_args.append(f"{key}={value}")
            else:
                dict_args[key] = value

        if dict_args:
            string_args.append(f"**{repr(dict_args)}")

        return f"{type_name}({', '.join(string_args)})"

    def _get_kwargs(self):
        return sorted(self.__dict__.items())

    def _get_args(self):
        return []


class ConfigSection(_Container):
    """
    Object for storing configuration option group.
    """

    def __init__(self, **kwargs):
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def __eq__(self, other):
        if not isinstance(other, ConfigSection):
            return NotImplemented
        return vars(self) == vars(other)

    def __contains__(self, key):
        return key in self.__dict__
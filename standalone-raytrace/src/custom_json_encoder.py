import json

class CustomJsonEncoder(json.JSONEncoder):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.indent_str = ' ' * self.indent
        self.indent_const = self.indent

    def iterencode(self, o, _one_shot=False):
        if isinstance(o, list):
            yield '['
            if self.indent is not None:
                self.indent += self.indent_const
                self.indent_str = ' ' * self.indent
            for i, item in enumerate(o):
                if i > 0:
                    yield ', '
                yield from self.iterencode(item)
            if self.indent is not None:
                self.indent -= self.indent_const
                self.indent_str = ' ' * self.indent
            yield ']'
        elif isinstance(o, dict):
            yield '{'
            if self.indent is not None:
                self.indent += self.indent_const
                self.indent_str = ' ' * self.indent
            for i, (key, value) in enumerate(o.items()):
                if i > 0:
                    yield ','
                if self.indent is not None:
                    yield '\n' + self.indent_str
                yield from self.iterencode(key)
                if self.indent is not None:
                    yield ': '
                else:
                    yield ':'
                yield from self.iterencode(value)
            if self.indent is not None:
                self.indent -= self.indent_const
                self.indent_str = ' ' * self.indent
                yield '\n' + self.indent_str
            yield '}'
        else:
            yield from super().iterencode(o, _one_shot=_one_shot)

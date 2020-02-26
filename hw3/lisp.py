# lisp.py
# xvalent4


def CreateElement(components):
    if isinstance(components, list):
        return ElementCompound(components)
    else:  # atom
        if components == "#t" or components == "#f":
            return ElementBoolean(components)
        elif components.startswith('"') and components.endswith('"'):
            return ElementString(components)
        else:
            try:
                int(components)
                return ElementNumber(components)
            except ValueError:
                try:
                    float(components)
                    return ElementNumber(components)
                except ValueError:
                    return ElementIdentifier(components)


class Element:
    def initattributes(self):
        self.components     = []
        self.token          = ""
        self.compound       = False
        self.atom           = False
        self.boolean        = False
        self.literal        = False
        self.string         = False
        self.number         = False
        self.identifier     = False

    def __eq__(self, other):
        return self.token == other.token

    def is_compound(self):
        return self.compound

    def is_atom(self):
        return self.atom

    def is_boolean(self):
        return self.boolean

    def is_literal(self):
        return self.literal

    def is_string(self):
        return self.string

    def is_number(self):
        return self.number

    def is_identifier(self):
        return self.identifier

    def __str__(self):
        if self.is_compound():
            out = "("
            for component in self.components:
                out += str(component)
                out += " "
            out = out[:-1]
            out += ")"
            return out
        else:
            return self.token


class ElementBoolean(Element):
    def __init__(self, components):
        super(ElementBoolean, self).initattributes()
        self.atom = True
        self.literal = True
        self.boolean = True
        self.token = components
        if self.token == "#t":
            self.value = True
        else:
            self.value = False

    def __bool__(self):
        return self.value


class ElementCompound(Element):
    def __init__(self, components):
        super(ElementCompound, self).initattributes()
        self.compound = True
        self.components = components
        self.index = 0

    def __eq__(self, other):
        if type(other) is not ElementCompound:
            return False

        for i in range(len(self.components)):
            if not self.components[i] == other.components[i]:
                return False
        return True

    def __iter__(self):
        return self

    def __next__(self):
        try:
            component = self.components[self.index]
        except IndexError:
            raise StopIteration
        self.index += 1
        return component


class ElementString(Element):
    def __init__(self, components):
        super(ElementString, self).initattributes()
        self.atom = True
        self.literal = True
        self.string = True
        self.token = components


class ElementNumber(Element):
    def __init__(self, components):
        super(ElementNumber, self).initattributes()
        self.atom = True
        self.literal = True
        self.number = True
        self.token = components
        try:
            self.value = int(components)
            self.float = False
        except ValueError:
            self.value = float(components)
            self.float = True

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def _eval(self, other, op):
        if self.float is True:
            return op(self.value, float(other))
        elif isinstance(other, float):
            return op(self.value, other)
        elif isinstance(other, ElementNumber):
            if other.float is True:
                return op(self.value, float(other))

        return op(self.value, int(other))

    def __add__(self, other):
        return self._eval(other, lambda x, y: x + y)

    def __radd__(self, other):
        return self._eval(other, lambda x, y: y + x)

    def __sub__(self, other):
        return self._eval(other, lambda x, y: x - y)

    def __rsub__(self, other):
        return self._eval(other, lambda x, y: y - x)

    def __mul__(self, other):
        return self._eval(other, lambda x, y: x * y)

    def __rmul__(self, other):
        return self._eval(other, lambda x, y: y * x)

    def __truediv__(self, other):
        return self._eval(other, lambda x, y: x / y)

    def __rtruediv__(self, other):
        return self._eval(other, lambda x, y: y / x)

    def __floordiv__(self, other):
        return self._eval(other, lambda x, y: x // y)

    def __rfloordiv__(self, other):
        return self._eval(other, lambda x, y: y // x)

    def __lt__(self, other):
        return self._eval(other, lambda x, y: x < y)

    def __le__(self, other):
        return self._eval(other, lambda x, y: x <= y)

    def __eq__(self, other):
        return self._eval(other, lambda x, y: x == y)

    def __ne__(self, other):
        return self._eval(other, lambda x, y: x != y)

    def __ge__(self, other):
        return self._eval(other, lambda x, y: x >= y)

    def __gt__(self, other):
        return self._eval(other, lambda x, y: x > y)


class ElementIdentifier(Element):
    def __init__(self, components):
        super(ElementIdentifier, self).initattributes()
        self.atom = True
        self.identifier = True
        self.token = components
        if not IsValidIdenfier(self.token):
            raise SyntaxError(self.token)


def IsValidIdenfier(string):
    id_init = ['!', '$', '%', '&', '*', '/', ':', '<', '=', '>', '?', '^', '_', '~']
    id_special = ['+', '-', '.', '@']

    if len(string) == 1 and (string == "+" or string == "-"):
        return True

    for index, c in enumerate(string):
        if index == 0:  # init
            if not c.isalpha() and c not in id_init:
                return False
        if index > 0:
            if not c.isalnum() and c not in id_init and c not in id_special:
                return False
    return True


def tokenize(string):
    ret = []
    token = ""
    quote = False
    bracket = 0
    escaped = False

    for c in string:
        if quote:
            if escaped:
                escaped = False
                if c == '"':
                    token += c
                elif c == '\\':
                    token += c
                else:
                    raise SyntaxError
            else:
                if c == '"':
                    quote = False
                elif c == '\\':
                    escaped = True
                token += c
        else:
            if not c.isspace() and not (c in '()'):
                token += c
                if c == '"':
                    quote = True
            else:
                if c == '(':
                    bracket += 1
                if c == ')':
                    bracket -= 1

                if len(token) > 0:
                    ret.append(token)
                    token = ""
                if not c.isspace():
                    ret += c

    if len(token) > 0:
        ret.append(token)

    if bracket != 0 or quote or escaped:
        raise SyntaxError
    return ret


def parse(expr):
    tokens = tokenize(expr)
    return parsing(tokens)


def parsing(tokens):
    if tokens == []:  # list is empty
        raise SyntaxError

    token = tokens.pop(0)
    if token == "(":
        components = []
        while tokens[0] != ")":
            components.append(parsing(tokens))
        tokens.pop(0)
        return CreateElement(components)
    elif token == ")":
        raise SyntaxError
    else:
        return CreateElement(token)

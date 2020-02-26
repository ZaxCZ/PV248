# Parser from hw3.

import numpy as np


def CreateElement(components):
    if isinstance(components, list):
        if isinstance(components[0], Identifier):
            if components[0].token == "vector":
                return Vector(components)
            elif components[0].token == "matrix":
                if checkMatrix(components):
                    return Matrix(components)
                else:
                    return Error("matrix dimensions mismatch")
        return Compound(components)
    else:  # atom
        if components == "#t" or components == "#f":
            return Boolean(components)
        elif components.startswith('"') and components.endswith('"'):
            return String(components)
        else:
            try:
                int(components)
                return Number(components)
            except ValueError:
                try:
                    float(components)
                    return Real(components)
                except ValueError:
                    return Identifier(components)


class Element(object):
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
        self.real           = False
        self.vector         = False
        self.matrix         = False
        self.error          = False
        self.float          = False

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

    def is_real(self):
        return self.real

    def is_vector(self):
        return self.vector

    def is_matrix(self):
        return self.matrix

    def is_error(self):
        return self.error

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


class Boolean(Element):
    def __init__(self, components):
        super(Boolean, self).initattributes()
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


class Compound(Element):
    def __init__(self, components):
        super(Compound, self).initattributes()
        self.compound = True
        self.components = components
        self.index = 0

    def __eq__(self, other):
        if type(other) is not Compound:
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


class Vector(Compound):
    def __init__(self, components):
        super(Vector, self).__init__(components)
        self.index = 1   # there is an identifier on index 0
        self.vector = True

        for component in components[1:]:
            if not isinstance(component, Number):
                raise SyntaxError("This should not be in a vector: " + str(component))

        self.value = np.array([component.value for component in components[1:]])

    def _eval(self, other, op):
        if isinstance(other, Vector):
            if (self.value.shape == other.value.shape):
                return op(self.value, other.value)
            else:
                raise ValueError("Vector shape mismatch")
        else:
            raise TypeError("Stop trying vector operations on other types")

    def __add__(self, other):
        return self._eval(other, lambda x, y: np.add(x, y))

    def __radd__(self, other):
        return self._eval(other, lambda x, y: np.add(y, x))

    def dot(self, other):
        return self._eval(other, lambda x, y: np.inner(x, y))

    def dft(self):
        return np.absolute(np.fft.rfft(self.value))


def checkMatrix(components):
    size = 0

    for component in components[1:]:
        if not isinstance(component, Vector):
            raise SyntaxError("This should not be in a matrix: " + str(component))
        else:
            if size == 0:
                size = len(component.value)
            elif len(component.value) != size:
                return False
    return True


class Matrix(Compound):
    def __init__(self, components):
        super(Matrix, self).__init__(components)
        self.index = 1   # there is an identifier on index 0
        self.matrix = True

        self.value = np.array([component.value for component in components[1:]])

    def _eval(self, other, op):
        if isinstance(other, Matrix):
            if (self.value.shape == other.value.shape):
                return op(self.value, other.value)
            else:
                raise ValueError("Matrix shape mismatch")
        else:
            raise TypeError("Stop trying matrix operations on other types")

    def __add__(self, other):
        return self._eval(other, lambda x, y: np.add(x, y))

    def __radd__(self, other):
        return self._eval(other, lambda x, y: np.add(y, x))

    def __mul__(self, other):
        return self._eval(other, lambda x, y: np.dot(x, y))

    def __rmul__(self, other):
        return self._eval(other, lambda x, y: np.dot(y, x))

    def det(self):
        return np.linalg.det(self.value)

    def solve(self):
        if self.value.shape[0] != self.value.shape[1]:
            raise ValueError("Matrix shape is not square")
        return null(self.value).flatten()


class String(Element):
    def __init__(self, components):
        super(String, self).initattributes()
        self.atom = True
        self.literal = True
        self.string = True
        self.token = components


class Number(Element):
    def __init__(self, components):
        super(Number, self).initattributes()
        self.atom = True
        self.literal = True
        self.number = True
        self.token = components
        self.value = int(components)
        self.float = False
        self.real = True

    def __int__(self):
        return int(self.value)

    def __float__(self):
        return float(self.value)

    def _eval(self, other, op):
        if isinstance(other, float):
            return op(float(self.value), other)
        elif isinstance(other, Number):
            if other.float is True:
                return op(float(self.value), other)
            else:
                return op(self.value, int(other))
        else:
            raise TypeError("dont know what to do with this")

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


class Real(Number):
    def __init__(self, components):
        super(Real, self).initattributes()
        self.real = True
        self.atom = True
        self.literal = True
        self.float = True
        self.token = components
        self.value = float(components)


class Error(Element):
    def __init__(self, components):
        super(Error, self).initattributes()
        self.error = True
        self.token = components


class Identifier(Element):
    def __init__(self, components):
        super(Identifier, self).initattributes()
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


# https://stackoverflow.com/questions/5889142/python-numpy-scipy-finding-the-null-space-of-a-matrix
def null(A, eps=1e-15):
    u, s, vh = np.linalg.svd(A)
    null_mask = (s <= eps)
    null_space = np.compress(null_mask, vh, axis=0)
    res = np.transpose(null_space)
    if res.size == 0:
        return np.zeros(len(A))
    else:
        return res

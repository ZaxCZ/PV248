# This file should implement eval().

from lisp import parse, Element, Error
import numpy as np


def eval(str):
    x = parse(str)
    return evaluate(x)


def evaluate(element):
    if element.is_atom():
        return element
    elif element.is_compound():
        if element.is_vector():
            return element
        elif element.is_matrix():
            return element
        else:
            elements = list(evaluate(e) for e in element.components)
            return resolve(elements)
    elif element.is_error():
        return element
    else:
        raise SyntaxError("unexpected error")


def resolve(elements):
    if len(elements) != 2 and len(elements) != 3:
        return Error("too many/ too little operands")
    operator = str(elements[0])
    operands = elements[1:]

    if operator == "+":
        if len(operands) != 2:
            return Error("too many/ too little operands")
        try:
            result = operands[0] + operands[1]
        except:
            return Error("+ failed")

    elif operator == "*":
        if len(operands) != 2:
            return Error("too many/ too little operands")
        try:
            result = operands[0] * operands[1]
        except:
            return Error("* failed")

    elif operator == "dot":
        if len(operands) != 2:
            return Error("too many/ too little operands")
        try:
            result = operands[0].dot(operands[1])
        except:
            return Error("dot failed")

    elif operator == "dft":
        if len(operands) != 1:
            return Error("too many/ too little operands")
        try:
            result = operands[0].dft()
        except:
            return Error("dft failed")

    elif operator == "solve":
        if len(operands) != 1:
            return Error("too many/ too little operands")
        try:
            result = operands[0].solve()
        except:
            return Error("solve failed")

    elif operator == "det":
        if len(operands) != 1:
            return Error("too many/ too little operands")
        try:
            result = operands[0].det()
        except:
            return Error("det failed")

    else:
        return Error("unexpected operator")

    return parse(toLisp(result))


def toLisp(x):
    out = ""
    if type(x) is np.ndarray:
        out += "( "

        if type(x[0]) is np.ndarray:  # matrix
            out += "matrix "
            for vector in x:
                out += "( "
                out += "vector "
                for real in vector:
                    out += str(real)
                    out += " "
                out += ") "
        else:  # vector
            out += "vector "
            for real in x:
                out += str(real)
                out += " "

        out += " )"

    else:  # just a number
        out = str(x)

    return out

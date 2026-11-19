# SPDX-License-Identifier: Apache-2.0
"""Safe deterministic AST math evaluator for analytical plot curves."""

from __future__ import annotations

import ast
import math
import operator
from typing import Callable

_MAX_EXPR_LEN = 512
_MAX_DEPTH = 32
_MAX_NODES = 128


def _safe_pow(base: float, exp: float) -> float:
    if not (math.isfinite(base) and math.isfinite(exp)):
        raise ValueError("Non-finite exponent operand")
    if abs(exp) > 1000.0:
        raise ValueError("Exponent out of bounds")
    if base < 0.0 and not float(exp).is_integer():
        raise ValueError("Fractional power of negative base")
    if abs(base) > 1.0 and exp * math.log10(abs(base)) > 300.0:
        raise ValueError("Power overflow")
    res = float(math.pow(base, exp))
    if not math.isfinite(res):
        raise ValueError("Power overflow")
    return res


_BIN_OPS: dict[type, Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: _safe_pow,
}

_UNARY_OPS: dict[type, Callable[[float], float]] = {
    ast.UAdd: operator.pos,
    ast.USub: operator.neg,
}

_SAFE_FUNCS: dict[str, Callable[..., float]] = {
    "abs": abs,
    "acos": math.acos,
    "asin": math.asin,
    "atan": math.atan,
    "cos": math.cos,
    "exp": math.exp,
    "ln": math.log,
    "log": math.log,
    "log10": math.log10,
    "max": max,
    "min": min,
    "sin": math.sin,
    "sqrt": math.sqrt,
    "tan": math.tan,
}

_SAFE_CONSTS: dict[str, float] = {
    "pi": math.pi,
    "e": math.e,
}


def _eval_node(node: ast.AST, env: dict[str, float], depth: int, counter: list[int]) -> float:
    """Evaluate a whitelisted AST math node deterministically."""
    counter[0] += 1
    if depth > _MAX_DEPTH or counter[0] > _MAX_NODES:
        raise ValueError("Expression complexity limit exceeded")
    if isinstance(node, ast.Expression):
        return _eval_node(node.body, env, depth + 1, counter)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)) and not isinstance(node.value, bool):
        val = float(node.value)
        if not math.isfinite(val):
            raise ValueError("Non-finite constant in equation")
        return val
    if isinstance(node, ast.Name):
        if node.id in env:
            val = float(env[node.id])
            if not math.isfinite(val):
                raise ValueError(f"Non-finite variable {node.id}")
            return val
        if node.id in _SAFE_CONSTS:
            return _SAFE_CONSTS[node.id]
        raise ValueError(f"Unsupported symbol in equation: {node.id}")
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_eval_node(node.operand, env, depth + 1, counter))
    if isinstance(node, ast.BinOp) and type(node.op) in _BIN_OPS:
        left = _eval_node(node.left, env, depth + 1, counter)
        right = _eval_node(node.right, env, depth + 1, counter)
        res = _BIN_OPS[type(node.op)](left, right)
        if isinstance(res, complex) or not math.isfinite(float(res)):
            raise ValueError("Non-finite binary expression result")
        return float(res)
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
        fn = _SAFE_FUNCS.get(node.func.id)
        if fn is None or node.keywords or not node.args:
            raise ValueError(f"Unsupported function in equation: {node.func.id}")
        args = [_eval_node(arg, env, depth + 1, counter) for arg in node.args]
        res = float(fn(*args))
        if not math.isfinite(res):
            raise ValueError("Non-finite function result")
        return res
    raise ValueError(f"Unsupported AST node in equation: {type(node).__name__}")


def eval_equation(expr: str, **variables: float) -> float:
    """Evaluate mathematical expression (supports `^` power and `math` funcs)."""
    if not isinstance(expr, str) or not expr.strip() or len(expr) > _MAX_EXPR_LEN:
        raise ValueError("Invalid or oversized equation expression")
    normalized = expr.strip().replace("^", "**")
    try:
        tree = ast.parse(normalized, mode="eval")
    except SyntaxError as exc:
        raise ValueError(f"Invalid equation syntax: {exc}") from exc
    return _eval_node(tree, variables, 0, [0])

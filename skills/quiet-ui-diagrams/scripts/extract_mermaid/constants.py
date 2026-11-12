# SPDX-License-Identifier: MIT
"""Constants, regex patterns, and token mappings for Mermaid extraction.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_NODES = 2000
MAX_EDGES = 5000
MAX_STATEMENT_CHARS = 4096
MAX_AUTONUMBER_DIGITS = 15

SUPPORTED_KINDS = "flowchart, sequenceDiagram, stateDiagram-v2, erDiagram"
UNSUPPORTED_KINDS = {
    "pie",
    "mindmap",
    "gitgraph",
    "quadrantchart",
    "timeline",
    "c4context",
    "sankey",
    "sankey-beta",
    "gantt",
    "journey",
    "classdiagram",
}
MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkd"}
MERMAID_SUFFIXES = {".mmd", ".mermaid"}
FRONTMATTER_MAX_LINES = 40

ER_IDENTIFIER = r"[^\W\d][\w.-]*"


def _er_name(name: str) -> bool:
    return name[:1] == "_" or name[:1].isalpha()


ER_QUOTED_NAME = r'"[^"%\r\n\v\b\\]+"'
ER_NAME = rf"(?:{ER_QUOTED_NAME}|{ER_IDENTIFIER})"

_ER_ZERO_OR_ONE = ("|o", "o|")
_ER_ONLY_ONE = ("||", "||")
_ER_ZERO_OR_MORE = ("}o", "o{")
_ER_ONE_OR_MORE = ("}|", "|{")

ER_CARDINALITIES = {
    "|o": _ER_ZERO_OR_ONE,
    "o|": _ER_ZERO_OR_ONE,
    "zero or one": _ER_ZERO_OR_ONE,
    "one or zero": _ER_ZERO_OR_ONE,
    "||": _ER_ONLY_ONE,
    "1": _ER_ONLY_ONE,
    "one": _ER_ONLY_ONE,
    "only one": _ER_ONLY_ONE,
    "}o": _ER_ZERO_OR_MORE,
    "o{": _ER_ZERO_OR_MORE,
    "0+": _ER_ZERO_OR_MORE,
    "many": _ER_ZERO_OR_MORE,
    "many(0)": _ER_ZERO_OR_MORE,
    "zero or more": _ER_ZERO_OR_MORE,
    "zero or many": _ER_ZERO_OR_MORE,
    "}|": _ER_ONE_OR_MORE,
    "|{": _ER_ONE_OR_MORE,
    "1+": _ER_ONE_OR_MORE,
    "many(1)": _ER_ONE_OR_MORE,
    "one or more": _ER_ONE_OR_MORE,
    "one or many": _ER_ONE_OR_MORE,
    "u": ("u", "u"),
}

ER_IDENTIFICATIONS = {
    "--": "--",
    "to": "--",
    "..": "..",
    ".-": "..",
    "-.": "..",
    "optionally to": "..",
}

_ER_TOKEN_CONTEXT = {
    "1": r"1(?=\s+[A-Za-z_\"'0-9]|--|\.\.|\.-|-\.)",
    "u": r"u(?=[.|-])",
}


def _er_tokens(tokens: dict[str, object]) -> str:
    ordered = sorted(tokens, key=len, reverse=True)
    return "|".join(
        _ER_TOKEN_CONTEXT.get(
            token,
            "(?a:" + re.escape(token) + (r"\b" if token[-1].isalnum() else "") + ")",
        )
        for token in ordered
    )


ER_CARDINALITY = _er_tokens(ER_CARDINALITIES)
ER_IDENTIFICATION = _er_tokens(ER_IDENTIFICATIONS)


def _er_entity(token: str) -> str | None:
    if token.startswith('"'):
        return token[1:-1]
    return token if _er_name(token) else None


SHAPE_FOR_DELIMITERS = (
    ("(((", ")))", "circle"),
    ("((", "))", "circle"),
    ("([", "])", "stadium"),
    ("{{", "}}", "hexagon"),
    ("[(", ")]", "cylinder"),
    ("[[", "]]", "subroutine"),
    ("[/", "/]", "parallelogram"),
    ("[\\", "\\]", "parallelogram"),
    ("[/", "\\]", "trapezoid"),
    ("[\\", "/]", "trapezoid"),
    ("[", "]", "rect"),
    ("(", ")", "round"),
    ("{", "}", "rhombus"),
    (">", "]", "asymmetric"),
)

EXPANDED_SHAPE_FAMILIES = {
    "rect": "rect",
    "rectangle": "rect",
    "proc": "rect",
    "process": "rect",
    "rounded": "round",
    "event": "round",
    "stadium": "stadium",
    "pill": "stadium",
    "terminal": "stadium",
    "circle": "circle",
    "circ": "circle",
    "sm-circ": "circle",
    "small-circle": "circle",
    "start": "circle",
    "dbl-circ": "circle",
    "double-circle": "circle",
    "fr-circ": "circle",
    "framed-circle": "circle",
    "stop": "circle",
    "cyl": "cylinder",
    "cylinder": "cylinder",
    "database": "cylinder",
    "db": "cylinder",
    "h-cyl": "cylinder",
    "horizontal-cylinder": "cylinder",
    "lin-cyl": "cylinder",
    "lined-cylinder": "cylinder",
    "diam": "rhombus",
    "decision": "rhombus",
    "diamond": "rhombus",
    "question": "rhombus",
    "hex": "hexagon",
    "hexagon": "hexagon",
    "prepare": "hexagon",
    "fr-rect": "subroutine",
    "framed-rectangle": "subroutine",
    "subproc": "subroutine",
    "subprocess": "subroutine",
    "subroutine": "subroutine",
    "lean-r": "parallelogram",
    "lean-l": "parallelogram",
    "in-out": "parallelogram",
    "lean-right": "parallelogram",
    "lean-left": "parallelogram",
    "out-in": "parallelogram",
    "trap-t": "trapezoid",
    "trap-b": "trapezoid",
    "trapezoid": "trapezoid",
    "inv-trapezoid": "trapezoid",
    "manual": "trapezoid",
    "priority": "trapezoid",
}

STYLE_DIRECTIVES = ("style ", "classDef ", "class ", "linkStyle ")
_EDGE_ID = re.compile(r"(?<![\w.:@-])([A-Za-z_][\w-]*)@")
REGION_KEYWORDS = {"alt": "else", "par": "and", "critical": "option"}

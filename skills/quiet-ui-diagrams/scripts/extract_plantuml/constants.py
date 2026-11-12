# SPDX-License-Identifier: MIT
"""Constants, token limits, and regex definitions for PlantUML extraction.

Adapted from diagram-design (Copyright (c) 2025 Cathryn Lavery, MIT License) for Quiet UI Skills v7.0
"""

from __future__ import annotations

import re

MAX_SOURCE_BYTES = 4 * 1024 * 1024
MAX_NODES = 2000
MAX_EDGES = 5000
MAX_STATEMENT_CHARS = 4096
SUPPORTED_KINDS = "sequence, class"

UNSUPPORTED_STARTS = {
    "activity",
    "component",
    "deployment",
    "state",
    "usecase",
    "archimate",
    "board",
    "bpmn",
    "chen",
    "chronology",
    "creole",
    "ditaa",
    "dot",
    "ebnf",
    "files",
    "gantt",
    "git",
    "jcckit",
    "json",
    "latex",
    "math",
    "mindmap",
    "network",
    "nwdiag",
    "project",
    "regex",
    "salt",
    "smetana",
    "tree",
    "wbs",
    "wire",
    "yaml",
}

MARKDOWN_SUFFIXES = {".md", ".markdown", ".mdown", ".mkd"}
PLANTUML_SUFFIXES = {".puml", ".plantuml", ".pu"}

INCLUDE_RE = re.compile(
    r"^\s*(?:!include(?:url|sub)?\b|!import\b|%load_json\b|"
    r"!function\b|!procedure\b)",
    re.I,
)
DEFINE_INCLUDE_RE = re.compile(r"^\s*!define\b.*!include", re.I)
THEME_URL_RE = re.compile(r"^\s*!theme\b.*https?://", re.I)
START_RE = re.compile(
    r"^@start([A-Za-z][A-Za-z0-9_-]*)\b(?:\s+\S+|\(\s*\S+\s*\))?", re.I
)
END_RE = re.compile(r"^@end([A-Za-z][A-Za-z0-9_-]*)\b", re.I)
FENCE_OPEN_RE = re.compile(r"^\s*(`{3,}|~{3,})\s*(plantuml|puml)\s*$", re.I)
CLASS_DECL_RE = re.compile(
    r"^\s*(?:abstract\s+)?(?:class|interface|enum)\b",
    re.I,
)
CLASS_REL_RE = re.compile(r"<\|--|-\|>|\*--|o--|<\|\.\.|\.\.\|>")
SEQ_ARROW_RE = re.compile(r"(->>|<<-|<->|-->|<--|<-|->)")

SEQ_ARROW_AT = re.compile(
    r"(?P<lead>o(?=[-<]))?(?P<left><<?)?(?P<body1>-+)(?P<style>\[[^\[\]]*\])?(?P<body2>-*)(?P<right>>>?)?"
    r"(?P<decoration>[ox](?=[\s:]|$))?"
)
CLASS_ARROW_AT = re.compile(
    r"(?P<left><\|(?=[-.])|[<*o#x}+^](?=[-.]))?"
    r"(?P<body1>(?P<char>[-.])(?P=char)*)"
    r"(?P<style>\[[^\[\]]*\]|(?:up|down|left|right|do|le|ri|u|d|l|r)(?=[-.]))?"
    r"(?P<body2>(?P=char)*)"
    r"(?P<right>\|>|[>*o#x{+^])?"
)

CLASS_HEADS = {
    "<|": "inheritance",
    "|>": "inheritance",
    "^": "inheritance",
    "*": "composition",
    "o": "aggregation",
    "<": "plain",
    ">": "plain",
}

LIFELINE_KINDS = {
    "participant": "lifeline",
    "actor": "actor",
    "boundary": "lifeline",
    "control": "lifeline",
    "entity": "lifeline",
    "database": "lifeline",
    "collections": "lifeline",
    "queue": "lifeline",
}
SEQ_DECL_RE = re.compile(rf"^\s*(?:{'|'.join(LIFELINE_KINDS)})\b", re.I)

CLASSIFIER_KINDS = {
    "class": "class",
    "abstract class": "abstract",
    "interface": "interface",
    "enum": "enum",
}

SKIN_COMMANDS = (
    "skinparam",
    "!theme",
    "autonumber",
    "hide",
    "show",
    "header",
    "footer",
    "legend",
    "caption",
    "scale",
    "sprite",
    "!pragma",
    "order",
    "left to right direction",
    "top to bottom direction",
)
SKIN_RE = re.compile(
    r"^(?:"
    + "|".join(re.escape(c).replace(r"\ ", r"\s+") for c in SKIN_COMMANDS)
    + r")(?=\s|\{|$)",
    re.I,
)
TEXT_BLOCK_RE = re.compile(
    r"^(?:(?:left|right|center)\s+)?(header|footer|legend)(?:\s+(?:left|right|center|top|bottom))*\s*$",
    re.I,
)
UNSUPPORTED_SEQUENCE = {
    "par",
    "critical",
    "break",
    "group",
    "box",
    "ref",
    "rnote",
    "hnote",
    "&",
}
UNSUPPORTED_CLASS = {
    "annotation",
    "abstract",
    "protocol",
    "struct",
    "exception",
    "metaclass",
    "stereotype",
}

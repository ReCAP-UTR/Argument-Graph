from __future__ import absolute_import, annotations

import collections
from dataclasses import dataclass, field
from typing import Any, Optional, Dict, Callable, List

import graphviz as gv
import networkx as nx
import pendulum

from . import utils, dt
from .node import Node


@dataclass
class Edge:
    """Edge in AIF format.

    Attributes `from` and `to` are mandatory.
    """

    start: Node
    end: Node
    key: int = field(default_factory=utils.unique_id)
    visible: bool = None
    annotator: str = None
    date: pendulum.DateTime = field(default_factory=pendulum.now)

    @property
    def _uid(self):
        return (self.key, self.start.key, self.end.key)

    def __hash__(self):
        return hash(self._uid)

    @staticmethod
    def from_ova(
        obj: Any,
        nodes: Dict[int, Node] = None,
        nlp: Optional[Callable[[str], Any]] = None,
    ) -> Edge:
        if not nodes:
            nodes = {}

        start_key = int(obj.get("from").get("id"))
        end_key = int(obj.get("to").get("id"))

        return Edge(
            start=nodes.get(start_key) or Node.from_ova(obj.get("from"), nlp),
            end=nodes.get(end_key) or Node.from_ova(obj.get("to"), nlp),
            visible=obj.get("visible"),
            annotator=obj.get("annotator"),
            date=dt.from_ova(obj.get("date")),
        )

    def to_ova(self) -> dict:
        return {
            "from": self.start.to_ova(),
            "to": self.end.to_ova(),
            "visible": self.visible,
            "annotator": self.annotator,
            "date": dt.to_ova(self.date),
        }

    @staticmethod
    def from_aif(
        obj: Any, nodes: Dict[int, Node], nlp: Optional[Callable[[str], Any]] = None
    ) -> Edge:
        start_key = int(obj.get("fromID"))
        end_key = int(obj.get("toID"))

        return Edge(
            start=nodes.get(start_key),
            end=nodes.get(end_key),
            key=int(obj.get("edgeID")),
        )

    def to_aif(self) -> dict:
        return {
            "edgeID": str(self.key),
            "fromID": str(self.start.key),
            "toID": str(self.end.key),
            "formEdgeID": None,
        }

    def to_nx(self, g: nx.DiGraph) -> None:
        g.add_edge(self.start.key, self.end.key)

    def to_gv(
        self, g: gv.Digraph, color="#666666", prefix: str = "", suffix: str = ""
    ) -> None:
        g.edge(
            f"{prefix}{self.start.key}{suffix}",
            f"{prefix}{self.end.key}{suffix}",
            color=color,
        )

    def __eq__(self, other: Edge) -> bool:
        return self.start == other.start and self.end == other.end


@dataclass(order=True)
class Edges(collections.abc.Sequence):
    _store: List[Edge] = field(default_factory=list)

    def __len__(self):
        return self._store.__len__()

    def __getitem__(self, key):
        return self._store.__getitem__(key)

    def __repr__(self):
        return self._store.__repr__()

    def __str__(self):
        return self._store.__str__()

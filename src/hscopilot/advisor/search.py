"""Forward-search extension point. Legality remains packet-derived."""

from typing import Protocol


class SearchAdvisor(Protocol):
    def search(self, snapshot, legal_actions): ...

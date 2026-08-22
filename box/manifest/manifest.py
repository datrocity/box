"""Manifest: a container of named metadata sections that round-trips through YAML."""

import yaml


class Manifest:
    """A named collection of metadata sections.

    Sections can be dicts (merged), lists (appended), or scalars (replaced).
    The manifest serializes to YAML with insertion-preserving key order.
    """

    def __init__(self, sections=None):
        self.sections = dict(sections) if sections else {}

    def add(self, section, data):
        """Set or replace a section.

        Parameters
        ----------
        section : str
        data : dict, list, or scalar
        """
        self.sections[section] = data

    def merge(self, section, data):
        """Merge a dict into a section, creating the section if missing.

        Parameters
        ----------
        section : str
        data : dict
        """
        existing = self.sections.setdefault(section, {})
        existing.update(data)

    def append(self, section, entry):
        """Append ``entry`` to a list-valued section, creating it if missing.

        Parameters
        ----------
        section : str
        entry : any
        """
        existing = self.sections.setdefault(section, [])
        existing.append(entry)

    def to_yaml(self):
        """Return the manifest as a YAML string."""
        return yaml.safe_dump(self.sections, sort_keys=False)

    @classmethod
    def from_yaml(cls, text):
        """Parse a YAML string into a Manifest.

        Returns
        -------
        Manifest
        """
        data = yaml.safe_load(text) or {}
        return cls(sections=data)

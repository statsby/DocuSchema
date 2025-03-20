from abc import ABC, abstractmethod


class BaseDB(ABC):
    """Abstract base class for fetching metadata from different databases."""

    @abstractmethod
    def fetch_metadata(self, schema_name, table_name):
        """Fetch metadata for the given schema and table."""
        pass

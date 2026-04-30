"""Generic in-memory key-value repository with full CRUD operations."""

from typing import Generic, Iterator, TypeVar

from weather_sdk.exceptions import StorageDuplicateError, StorageKeyError

_VT = TypeVar("_VT")


class InMemoryRepository(Generic[_VT]):
    """Thread-unsafe in-memory store backed by a plain ``dict``.

    Type parameter ``_VT`` is the value type kept in the store.

    Example::

        repo: InMemoryRepository[CurrentWeather] = InMemoryRepository()
        repo.create("london", weather)
        entry = repo.read("london")
        repo.update("london", new_weather)
        repo.delete("london")
    """

    def __init__(self) -> None:
        self._store: dict[str, _VT] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create(self, key: str, entry: _VT) -> _VT:
        """Insert *entry* under *key*.

        Raises:
            StorageDuplicateError: if *key* already exists.
        """
        if key in self._store:
            raise StorageDuplicateError(key)
        self._store[key] = entry
        return entry

    def read(self, key: str) -> _VT:
        """Return the entry for *key*.

        Raises:
            StorageKeyError: if *key* is absent.
        """
        if key not in self._store:
            raise StorageKeyError(key)
        return self._store[key]

    def update(self, key: str, entry: _VT) -> _VT:
        """Replace the entry for an existing *key*.

        Raises:
            StorageKeyError: if *key* is absent.
        """
        if key not in self._store:
            raise StorageKeyError(key)
        self._store[key] = entry
        return entry

    def upsert(self, key: str, entry: _VT) -> _VT:
        """Insert or replace *entry* under *key* unconditionally."""
        self._store[key] = entry
        return entry

    def delete(self, key: str) -> None:
        """Remove *key* from the store.

        Raises:
            StorageKeyError: if *key* is absent.
        """
        if key not in self._store:
            raise StorageKeyError(key)
        self._store.pop(key)

    def list_keys(self) -> list[str]:
        """Return a sorted snapshot of all stored keys."""
        return sorted(self._store.keys())

    def __len__(self) -> int:
        return len(self._store)

    def __iter__(self) -> Iterator[tuple[str, _VT]]:
        yield from self._store.items()

    def __contains__(self, key: object) -> bool:
        return key in self._store

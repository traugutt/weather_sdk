"""Unit tests for InMemoryRepository."""

import pytest

from weather_sdk.exceptions import StorageDuplicateError, StorageKeyError
from weather_sdk.storage.repository import InMemoryRepository


@pytest.fixture()
def repo() -> InMemoryRepository[str]:
    return InMemoryRepository()


def test_create_and_read(repo: InMemoryRepository[str]) -> None:
    repo.create("k", "hello")
    assert repo.read("k") == "hello"


def test_create_duplicate_raises(repo: InMemoryRepository[str]) -> None:
    repo.create("k", "v1")
    with pytest.raises(StorageDuplicateError):
        repo.create("k", "v2")


def test_read_missing_raises(repo: InMemoryRepository[str]) -> None:
    with pytest.raises(StorageKeyError):
        repo.read("nope")


def test_update(repo: InMemoryRepository[str]) -> None:
    repo.create("k", "v1")
    repo.update("k", "v2")
    assert repo.read("k") == "v2"


def test_update_missing_raises(repo: InMemoryRepository[str]) -> None:
    with pytest.raises(StorageKeyError):
        repo.update("ghost", "x")


def test_upsert_inserts_new(repo: InMemoryRepository[str]) -> None:
    repo.upsert("k", "v1")
    assert repo.read("k") == "v1"


def test_upsert_overwrites_existing(repo: InMemoryRepository[str]) -> None:
    repo.create("k", "v1")
    repo.upsert("k", "v2")
    assert repo.read("k") == "v2"


def test_delete(repo: InMemoryRepository[str]) -> None:
    repo.create("k", "v")
    repo.delete("k")
    assert "k" not in repo


def test_delete_missing_raises(repo: InMemoryRepository[str]) -> None:
    with pytest.raises(StorageKeyError):
        repo.delete("gone")


def test_list_keys_sorted(repo: InMemoryRepository[str]) -> None:
    repo.create("b", "2")
    repo.create("a", "1")
    assert repo.list_keys() == ["a", "b"]


def test_len(repo: InMemoryRepository[str]) -> None:
    assert len(repo) == 0
    repo.create("x", "y")
    assert len(repo) == 1


def test_iter(repo: InMemoryRepository[str]) -> None:
    repo.create("a", "1")
    repo.create("b", "2")
    pairs = dict(repo)
    assert pairs == {"a": "1", "b": "2"}

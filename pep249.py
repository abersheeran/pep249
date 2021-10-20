from __future__ import annotations

import threading
from queue import Queue, Empty as EmptyQueueError
from contextlib import contextmanager
from typing import (
    Generator,
    Protocol,
    runtime_checkable,
    Optional,
    Sequence,
    Any,
    Union,
    Mapping,
    Callable,
    Generic,
    TypeVar,
)

T = TypeVar("T")


@runtime_checkable
class Connection(Protocol):
    def close(self):
        raise NotImplementedError()

    def commit(self):
        raise NotImplementedError()

    def cursor(self) -> Cursor:
        raise NotImplementedError()


@runtime_checkable
class Cursor(Protocol):
    def close(self):
        raise NotImplementedError()

    def execute(
        self, operation: str, parameters: Union[Sequence[Any], Mapping[str, Any]] = None
    ) -> Any:
        raise NotImplementedError()

    def executemany(
        self,
        operation: str,
        seq_of_parameters: Sequence[Union[Sequence[Any], Mapping[str, Any]]] = None,
    ) -> Any:
        raise NotImplementedError()

    def fetchone(self) -> Optional[Sequence[Any]]:
        raise NotImplementedError()

    def fetchmany(self, size: int = None) -> Sequence[Sequence[Any]]:
        raise NotImplementedError()

    def fetchall(self) -> Sequence[Sequence[Any]]:
        raise NotImplementedError()


class ImmutableAttribute(Generic[T]):
    def __set_name__(self, owner: object, name: str) -> None:
        self.public_name = name
        self.private_name = "_" + name

    def __get__(self, instance: object, cls: type = None) -> T:
        return getattr(instance, self.private_name)

    def __set__(self, instance: object, value: T) -> None:
        if hasattr(instance, self.private_name):
            raise RuntimeError(
                f"{instance.__class__.__name__}.{self.public_name} is immutable"
            )
        setattr(instance, self.private_name, value)

    def __delete__(self, instance: object) -> None:
        raise RuntimeError(
            f"{instance.__class__.__name__}.{self.public_name} is immutable"
        )


class ConnectionPool:
    maxsize = ImmutableAttribute()
    connection_queue = ImmutableAttribute()

    def __init__(
        self,
        *,
        maxsize: int,
        connection_factory: Callable[[], Connection],
    ):
        self.maxsize = maxsize
        self.connection_factory = connection_factory
        self.connection_queue = Queue(maxsize)

        self._size = 0
        self._sync_lock = threading.RLock()

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, value: int) -> None:
        with self._sync_lock:
            self._size = value

    @staticmethod
    def ensure_connection(connection: Connection) -> bool:
        cursor = connection.cursor()
        try:
            cursor.execute("SELECT 1")
            return True
        except Exception:
            return False
        finally:
            cursor.close()

    def acquire(self) -> Connection:
        with self._sync_lock:
            try:
                connection = self.connection_queue.get(
                    block=self.size >= self.maxsize,
                )
            except EmptyQueueError:
                connection = self.connection_factory()
                self.size += 1

        if not self.ensure_connection(connection):
            with self._sync_lock:
                self.size -= 1
                connection = self.acquire()

        return connection

    def release(self, connection: Connection) -> None:
        self.connection_queue.put(connection, block=False)

    @contextmanager
    def connect(self) -> Generator[Connection, None, None]:
        """
        Acquire a connection and automatically reclaim
        it to the pool after leaving the context manager.
            with pool.connect() as connection:
                ...
        Equivalent to:
            connection = pool.acquire()
            try:
                ...
            finally:
                pool.release(connection)
        """
        connection = self.acquire()
        try:
            yield connection
        finally:
            self.release(connection)

    def clear(self) -> None:
        with self._sync_lock:
            while self.size > 0:
                self.connection_queue.get().close()
                self.size -= 1

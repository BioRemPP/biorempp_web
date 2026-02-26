"""
Redis adapter for resume payload persistence.
"""

import json
import os
import re
import zlib
from typing import Any, Optional

from .resume_store import ResumeStore
from src.shared.logging import build_log_ref, get_logger

logger = get_logger(__name__)

try:
    import redis
except ImportError:  # pragma: no cover - dependency may be optional in some envs
    redis = None


class RedisResumeStore(ResumeStore):
    """
    Redis implementation of ResumeStore with compressed JSON serialization.
    """

    DEFAULT_KEY_PREFIX = "biorempp:resume:"
    KEY_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9:_-]{1,128}$")
    PREFIX_SAFE_PATTERN = re.compile(r"^[A-Za-z0-9:_-]{1,64}:$")

    def __init__(
        self,
        host: str = "redis",
        port: int = 6379,
        db: int = 0,
        password: Optional[str] = None,
        key_prefix: str = DEFAULT_KEY_PREFIX,
        socket_timeout_seconds: float = 3.0,
        compression_level: int = 6,
        client: Optional[Any] = None,
    ) -> None:
        if client is None:
            if redis is None:
                raise RuntimeError(
                    "redis package is not installed. Install cache/runtime-full extras."
                )
            client = redis.Redis(
                host=host,
                port=int(port),
                db=int(db),
                password=password or None,
                decode_responses=False,
                socket_timeout=float(socket_timeout_seconds),
                socket_connect_timeout=float(socket_timeout_seconds),
                health_check_interval=30,
            )

        self._client = client
        normalized_prefix = (key_prefix or self.DEFAULT_KEY_PREFIX).strip()
        if normalized_prefix and not normalized_prefix.endswith(":"):
            normalized_prefix = f"{normalized_prefix}:"
        if not self.PREFIX_SAFE_PATTERN.fullmatch(normalized_prefix):
            raise ValueError("Invalid redis resume key prefix")
        self._key_prefix = normalized_prefix
        self._compression_level = min(max(int(compression_level), 1), 9)

    @property
    def backend_name(self) -> str:
        return "redis"

    @staticmethod
    def _read_env_int(name: str, default: int, minimum: int = 0) -> int:
        raw_value = os.getenv(name)
        if raw_value is None:
            return max(default, minimum)
        try:
            return max(int(raw_value), minimum)
        except ValueError:
            return max(default, minimum)

    @staticmethod
    def _read_env_float(name: str, default: float, minimum: float = 0.0) -> float:
        raw_value = os.getenv(name)
        if raw_value is None:
            return max(default, minimum)
        try:
            return max(float(raw_value), minimum)
        except ValueError:
            return max(default, minimum)

    @classmethod
    def from_env(cls) -> "RedisResumeStore":
        """Build Redis store from environment variables."""
        host = os.getenv("BIOREMPP_RESUME_REDIS_HOST", os.getenv("REDIS_HOST", "redis"))
        port = cls._read_env_int(
            "BIOREMPP_RESUME_REDIS_PORT",
            cls._read_env_int("REDIS_PORT", 6379, minimum=1),
            minimum=1,
        )
        db = cls._read_env_int(
            "BIOREMPP_RESUME_REDIS_DB",
            cls._read_env_int("REDIS_DB", 0, minimum=0),
            minimum=0,
        )
        password = os.getenv(
            "BIOREMPP_RESUME_REDIS_PASSWORD",
            os.getenv("REDIS_PASSWORD", ""),
        )
        key_prefix = os.getenv(
            "BIOREMPP_RESUME_REDIS_KEY_PREFIX",
            cls.DEFAULT_KEY_PREFIX,
        )
        socket_timeout_seconds = cls._read_env_float(
            "BIOREMPP_RESUME_REDIS_SOCKET_TIMEOUT_SECONDS",
            3.0,
            minimum=0.5,
        )
        compression_level = cls._read_env_int(
            "BIOREMPP_RESUME_REDIS_COMPRESSION_LEVEL",
            6,
            minimum=1,
        )
        return cls(
            host=host,
            port=port,
            db=db,
            password=password,
            key_prefix=key_prefix,
            socket_timeout_seconds=socket_timeout_seconds,
            compression_level=min(compression_level, 9),
        )

    def ping(self) -> bool:
        """Check backend reachability."""
        try:
            return bool(self._client.ping())
        except Exception:
            logger.exception("Redis ping failed for resume backend")
            return False

    def _full_key(self, key: str) -> str:
        normalized_key = (key or "").strip()
        if not self.KEY_SAFE_PATTERN.fullmatch(normalized_key):
            raise ValueError("Invalid redis resume key")
        return f"{self._key_prefix}{normalized_key}"

    def _serialize(self, value: dict) -> bytes:
        payload_bytes = json.dumps(
            value,
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        return zlib.compress(payload_bytes, self._compression_level)

    @staticmethod
    def _deserialize(blob: Any) -> Optional[dict]:
        if blob is None:
            return None
        try:
            raw = bytes(blob)
            decompressed = zlib.decompress(raw).decode("utf-8")
            payload = json.loads(decompressed)
        except Exception:
            return None
        return payload if isinstance(payload, dict) else None

    def set(self, key: str, value: dict, ttl_seconds: int) -> bool:
        cache_ref = build_log_ref(key, namespace="cache")
        full_key = self._full_key(key)
        try:
            compressed_payload = self._serialize(value)
            result = self._client.set(
                name=full_key,
                value=compressed_payload,
                ex=max(int(ttl_seconds), 1),
            )
            return bool(result)
        except Exception:
            logger.exception(
                "Redis resume set failed",
                extra={"cache_ref": cache_ref},
            )
            return False

    def get(self, key: str) -> Optional[dict]:
        cache_ref = build_log_ref(key, namespace="cache")
        full_key = self._full_key(key)
        try:
            raw_value = self._client.get(full_key)
        except Exception:
            logger.exception(
                "Redis resume get failed",
                extra={"cache_ref": cache_ref},
            )
            return None
        return self._deserialize(raw_value)

    def close(self) -> None:
        close_fn = getattr(self._client, "close", None)
        if callable(close_fn):
            close_fn()

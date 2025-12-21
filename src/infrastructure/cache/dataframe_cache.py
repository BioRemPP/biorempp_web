"""
DataFrame Cache - Pandas DataFrame Caching.

Provides specialized caching for pandas DataFrames with compression support
for memory efficiency.

Classes
-------
DataFrameCache
    Specialized cache for pandas DataFrames with gzip compression
"""

import gzip
import hashlib
import pickle
from typing import Optional

import pandas as pd

from src.shared.logging import get_logger

from .memory_cache import MemoryCache

logger = get_logger(__name__)


class DataFrameCache(MemoryCache):
    """
    Specialized cache for pandas DataFrames.

    Provides compression (gzip + pickle), DataFrame-specific hash generation,
    memory usage tracking, and automatic compression for large DataFrames.

    Attributes
    ----------
    compress_threshold : int
        DataFrame size (bytes) above which compression is used
    compression_level : int
        Gzip compression level (1-9)
    """

    def __init__(
        self,
        max_size: int = 50,
        default_ttl: int = 3600,
        compress_threshold: int = 1024 * 1024,  # 1 MB
        compression_level: int = 6
    ):
        """
        Initialize DataFrame cache.

        Parameters
        ----------
        max_size : int, default=50
            Maximum number of DataFrames to cache.
        default_ttl : int, default=3600
            Default TTL in seconds.
        compress_threshold : int, default=1048576
            Size threshold (bytes) for compression.
        compression_level : int, default=6
            Gzip compression level (1-9).
        """
        super().__init__(max_size=max_size, default_ttl=default_ttl)
        self.compress_threshold = compress_threshold
        self.compression_level = compression_level

        logger.info(
            f"Initialized {self.__class__.__name__}",
            extra={
                'max_size': max_size,
                'compress_threshold_mb': round(
                    compress_threshold / 1024**2, 2
                ),
                'compression_level': compression_level
            }
        )

    def cache_dataframe(
        self,
        key: str,
        df: pd.DataFrame,
        ttl: Optional[int] = None
    ) -> None:
        """
        Cache a DataFrame.

        Parameters
        ----------
        key : str
            Cache key
        df : pd.DataFrame
            DataFrame to cache
        ttl : Optional[int], default=None
            TTL in seconds
        """
        # Get DataFrame size
        df_size = df.memory_usage(deep=True).sum()

        # Compress if necessary
        if df_size > self.compress_threshold:
            logger.debug(
                f"Compressing large DataFrame: {key}",
                extra={'size_mb': round(df_size / 1024**2, 2)}
            )
            cached_data = self._compress_dataframe(df)
            is_compressed = True
        else:
            cached_data = df.copy()
            is_compressed = False

        # Store metadata along with data
        cache_entry = {
            'data': cached_data,
            'is_compressed': is_compressed,
            'original_size_mb': round(df_size / 1024**2, 2),
            'shape': df.shape
        }

        self.set(key, cache_entry, ttl=ttl)

        logger.info(
            f"Cached DataFrame: {key}",
            extra={
                'shape': df.shape,
                'size_mb': round(df_size / 1024**2, 2),
                'compressed': is_compressed
            }
        )

    def get_cached_dataframe(self, key: str) -> Optional[pd.DataFrame]:
        """
        Retrieve cached DataFrame.

        Parameters
        ----------
        key : str
            Cache key

        Returns
        -------
        Optional[pd.DataFrame]
            Cached DataFrame or None if not found
        """
        cache_entry = self.get(key)

        if cache_entry is None:
            return None

        # Decompress if necessary
        if cache_entry['is_compressed']:
            logger.debug(f"Decompressing DataFrame: {key}")
            return self._decompress_dataframe(cache_entry['data'])
        else:
            return cache_entry['data'].copy()

    def generate_dataframe_key(
        self,
        df: pd.DataFrame,
        prefix: str = ''
    ) -> str:
        """
        Generate unique cache key for DataFrame.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to generate key for
        prefix : str, default=''
            Optional prefix for key

        Returns
        -------
        str
            Cache key based on DataFrame content hash

        Notes
        -----
        - Key based on columns, shape, and sample data
        """
        # Create hash from DataFrame characteristics
        hash_components = [
            str(df.shape),
            str(sorted(df.columns.tolist())),
            str(df.dtypes.to_dict()),
            # Sample first/last rows for content hash
            (str(df.head(5).values.tobytes())
             if len(df) > 0 else ''),
            (str(df.tail(5).values.tobytes())
             if len(df) > 5 else '')
        ]

        hash_string = '|'.join(hash_components)
        hash_value = hashlib.md5(
            hash_string.encode()
        ).hexdigest()[:16]

        if prefix:
            return f"{prefix}_{hash_value}"
        return hash_value

    def _compress_dataframe(self, df: pd.DataFrame) -> bytes:
        """
        Compress DataFrame using gzip + pickle.

        Parameters
        ----------
        df : pd.DataFrame
            DataFrame to compress.

        Returns
        -------
        bytes
            Compressed data.
        """
        pickled = pickle.dumps(df)
        compressed = gzip.compress(
            pickled,
            compresslevel=self.compression_level
        )
        return compressed

    def _decompress_dataframe(self, compressed_data: bytes) -> pd.DataFrame:
        """
        Decompress DataFrame.

        Parameters
        ----------
        compressed_data : bytes
            Compressed DataFrame data.

        Returns
        -------
        pd.DataFrame
            Decompressed DataFrame.
        """
        decompressed = gzip.decompress(compressed_data)
        df = pickle.loads(decompressed)
        return df

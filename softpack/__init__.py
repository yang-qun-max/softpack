"""
softpack — gentle pre-compression for AI agent context.

Press softly at 70% before the LLM crushes at 83%.
"""

from softpack.compress import compress, softpack_compress, METHODS

__version__ = "0.1.0"
__all__ = ["compress", "softpack_compress", "METHODS"]

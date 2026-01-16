"""
Pixellate - A photo processing tool with customizable settings.
"""

__version__ = "1.0.0"

from pixellate.image_processor import ImageProcessor
from pixellate.config import DEFAULT_CONFIG

__all__ = ["ImageProcessor", "DEFAULT_CONFIG"]

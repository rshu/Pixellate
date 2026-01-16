"""
Configuration settings for Pixellate.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Config:
    """Configuration class for default settings."""
    # Crop settings
    default_crop_size_inches: float = 2.0
    min_crop_size_inches: float = 0.5
    max_crop_size_inches: float = 10.0
    crop_step: float = 0.1
    
    # DPI settings
    default_dpi: int = 300
    min_dpi: int = 72
    max_dpi: int = 600
    
    # Resolution settings
    default_width: int = 461
    default_height: int = 579
    
    # File size settings
    default_max_file_size_mb: float = 1.0
    min_file_size_mb: float = 0.1
    max_file_size_mb: float = 10.0
    file_size_step: float = 0.1
    
    # Format settings
    supported_formats: List[str] = field(default_factory=lambda: ["jpg", "png"])
    default_format: str = "jpg"
    
    # Compression settings
    jpeg_initial_quality: int = 95
    jpeg_min_quality: int = 10
    jpeg_quality_step: int = 5
    png_compress_level: int = 9
    min_scale_factor: float = 0.5
    scale_factor_step: float = 0.05
    
    # Server settings
    server_name: str = "0.0.0.0"
    server_port: int = 7860


# Default configuration instance
DEFAULT_CONFIG = Config()

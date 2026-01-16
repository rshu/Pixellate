"""
Image processing module for Pixellate.
"""

from PIL import Image
import io
from typing import Tuple
from pixellate.config import DEFAULT_CONFIG


class ImageProcessor:
    """Handles image processing operations."""
    
    def __init__(self, config=None):
        """
        Initialize the ImageProcessor.
        
        Args:
            config: Configuration object (uses DEFAULT_CONFIG if None)
        """
        self.config = config or DEFAULT_CONFIG
    
    def crop_to_square(self, image: Image.Image, crop_size_pixels: int) -> Image.Image:
        """
        Crop image to a square of the specified size in pixels.
        
        Args:
            image: Input PIL Image
            crop_size_pixels: Size of the square crop in pixels
            
        Returns:
            Cropped square image
        """
        width, height = image.size
        min_dim = min(width, height)
        
        # Calculate crop box (center crop)
        left = (width - min_dim) // 2
        top = (height - min_dim) // 2
        right = left + min_dim
        bottom = top + min_dim
        
        # Crop to square
        cropped = image.crop((left, top, right, bottom))
        
        # Resize to target size if needed
        if min_dim != crop_size_pixels:
            cropped = cropped.resize(
                (crop_size_pixels, crop_size_pixels), 
                Image.Resampling.LANCZOS
            )
        
        return cropped
    
    def compress_jpeg(
        self, 
        image: Image.Image, 
        max_file_size_bytes: int,
        target_width: int,
        target_height: int
    ) -> Tuple[Image.Image, str]:
        """
        Compress JPEG image to meet file size requirement.
        
        Args:
            image: PIL Image to compress
            max_file_size_bytes: Maximum file size in bytes
            target_width: Target width
            target_height: Target height
            
        Returns:
            Tuple of (compressed_image, info_message)
        """
        quality = self.config.jpeg_initial_quality
        processed = image
        
        # Try different quality levels
        while quality > self.config.jpeg_min_quality:
            buffer = io.BytesIO()
            processed.save(buffer, format='JPEG', quality=quality, optimize=True)
            file_size = buffer.tell()
            
            if file_size <= max_file_size_bytes:
                buffer.seek(0)
                processed = Image.open(buffer)
                processed.load()
                info = f"Processed successfully! Final size: {file_size / 1024:.2f} KB, Quality: {quality}"
                return processed, info
            
            quality -= self.config.jpeg_quality_step
        
        # If still too large, resize more aggressively
        scale_factor = 0.9
        while quality > self.config.jpeg_min_quality:
            new_width = int(target_width * scale_factor)
            new_height = int(target_height * scale_factor)
            temp_img = processed.resize((new_width, new_height), Image.Resampling.LANCZOS)
            buffer = io.BytesIO()
            temp_img.save(buffer, format='JPEG', quality=quality, optimize=True)
            file_size = buffer.tell()
            
            if file_size <= max_file_size_bytes:
                buffer.seek(0)
                processed = Image.open(buffer)
                processed.load()
                info = f"Processed with reduced size ({new_width}x{new_height})! Final size: {file_size / 1024:.2f} KB, Quality: {quality}"
                return processed, info
            
            scale_factor -= self.config.scale_factor_step
            if scale_factor < self.config.min_scale_factor:
                quality -= self.config.jpeg_quality_step
        
        # Final fallback
        buffer = io.BytesIO()
        processed.save(buffer, format='JPEG', quality=quality, optimize=True)
        file_size = buffer.tell()
        info = f"Warning: Could not compress below target size. Final size: {file_size / 1024:.2f} KB"
        return processed, info
    
    def compress_png(
        self, 
        image: Image.Image, 
        max_file_size_bytes: int,
        target_width: int,
        target_height: int
    ) -> Tuple[Image.Image, str]:
        """
        Compress PNG image to meet file size requirement.
        
        Args:
            image: PIL Image to compress
            max_file_size_bytes: Maximum file size in bytes
            target_width: Target width
            target_height: Target height
            
        Returns:
            Tuple of (compressed_image, info_message)
        """
        processed = image
        compress_level = self.config.png_compress_level
        
        buffer = io.BytesIO()
        processed.save(buffer, format='PNG', compress_level=compress_level, optimize=True)
        file_size = buffer.tell()
        
        if file_size <= max_file_size_bytes:
            info = f"Processed successfully! Final size: {file_size / 1024:.2f} KB"
            return processed, info
        
        # Try converting to palette mode for smaller file size
        if processed.mode != 'P':
            processed = processed.convert('P', palette=Image.Palette.ADAPTIVE)
            buffer = io.BytesIO()
            processed.save(buffer, format='PNG', compress_level=compress_level, optimize=True)
            file_size = buffer.tell()
        
        # If still too large, reduce dimensions
        if file_size > max_file_size_bytes:
            scale_factor = 0.9
            while file_size > max_file_size_bytes and scale_factor >= self.config.min_scale_factor:
                new_width = int(target_width * scale_factor)
                new_height = int(target_height * scale_factor)
                temp_img = processed.resize((new_width, new_height), Image.Resampling.LANCZOS)
                buffer = io.BytesIO()
                temp_img.save(buffer, format='PNG', compress_level=compress_level, optimize=True)
                file_size = buffer.tell()
                
                if file_size <= max_file_size_bytes:
                    processed = temp_img
                    info = f"Processed with reduced size ({new_width}x{new_height})! Final size: {file_size / 1024:.2f} KB"
                    return processed, info
                
                scale_factor -= self.config.scale_factor_step
        
        info = f"Warning: Could not compress below target size. Final size: {file_size / 1024:.2f} KB"
        return processed, info
    
    def process_image(
        self,
        image: Image.Image,
        crop_size_inches: float,
        target_width: int,
        target_height: int,
        max_file_size_mb: float,
        output_format: str,
        dpi: int
    ) -> Tuple[Image.Image, str]:
        """
        Process the image according to the specified parameters.
        
        Args:
            image: Input PIL Image
            crop_size_inches: Size in inches for cropping (assumes square crop)
            target_width: Target width in pixels
            target_height: Target height in pixels
            max_file_size_mb: Maximum file size in MB
            output_format: 'jpg' or 'png'
            dpi: DPI for inch-based calculations
        
        Returns:
            Tuple of (processed_image, info_message)
        """
        if image is None:
            return None, "Please upload an image first."
        
        try:
            # Step 1: Crop to specified inches (convert inches to pixels)
            crop_size_pixels = int(crop_size_inches * dpi)
            cropped = self.crop_to_square(image, crop_size_pixels)
            
            # Step 2: Resize to target resolution
            processed = cropped.resize(
                (target_width, target_height), 
                Image.Resampling.LANCZOS
            )
            
            # Step 3: Compress to meet file size requirement
            max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
            
            if output_format.lower() in ['jpg', 'jpeg']:
                processed, info = self.compress_jpeg(
                    processed, max_file_size_bytes, int(target_width), int(target_height)
                )
            else:  # PNG
                processed, info = self.compress_png(
                    processed, max_file_size_bytes, int(target_width), int(target_height)
                )
            
            return processed, info
        
        except (ValueError, IOError, OSError) as e:
            return None, f"Error processing image: {str(e)}"

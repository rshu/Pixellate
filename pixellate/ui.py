"""
Gradio UI module for Pixellate.
"""

import gradio as gr
from PIL import Image
import os
import tempfile
import time
from typing import Tuple, Optional
from pixellate.image_processor import ImageProcessor
from pixellate.config import DEFAULT_CONFIG


class PixellateUI:
    """Gradio UI for Pixellate photo processor."""
    
    def __init__(self, config=None, processor=None):
        """
        Initialize the UI.
        
        Args:
            config: Configuration object (uses DEFAULT_CONFIG if None)
            processor: ImageProcessor instance (creates new one if None)
        """
        self.config = config or DEFAULT_CONFIG
        self.processor = processor or ImageProcessor(self.config)
    
    def process_image(
        self,
        img: Optional[Image.Image],
        crop: float,
        w: float,
        h: float,
        max_size: float,
        fmt: str,
        dpi_val: float
    ) -> Tuple[Optional[Image.Image], str, Optional[Image.Image]]:
        """
        Process image and return the processed image.
        
        Args:
            img: Input image
            crop: Crop size in inches
            w: Target width
            h: Target height
            max_size: Max file size in MB
            fmt: Output format
            dpi_val: DPI value
            
        Returns:
            Tuple of (processed_image, info_message, processed_image_for_state)
        """
        if img is None:
            return None, "Please upload an image first.", None
        
        processed_img, info = self.processor.process_image(
            img, crop, int(w), int(h), max_size, fmt, int(dpi_val)
        )
        
        if processed_img is not None:
            return processed_img, info, processed_img
        else:
            return None, info, None
    
    def export_to_format(
        self,
        processed_img: Optional[Image.Image],
        format_type: str
    ):
        """
        Export processed image to specified format.
        
        Args:
            processed_img: Processed PIL Image
            format_type: 'jpg' or 'png'
            
        Returns:
            File path string or None
        """
        if processed_img is None:
            return None
        
        temp_dir = tempfile.gettempdir()
        # Use unique filename with timestamp to avoid conflicts
        timestamp = int(time.time() * 1000)
        file_ext = 'jpg' if format_type.lower() in ['jpg', 'jpeg'] else 'png'
        temp_path = os.path.join(temp_dir, f"pixellate_export_{timestamp}.{file_ext}")
        
        try:
            if format_type.lower() in ['jpg', 'jpeg']:
                processed_img.save(temp_path, format='JPEG', quality=95, optimize=True)
            else:  # PNG
                processed_img.save(temp_path, format='PNG', optimize=True)
            
            # Verify file was created
            if os.path.exists(temp_path) and os.path.getsize(temp_path) > 0:
                return temp_path
            else:
                return None
        except Exception as e:
            print(f"Error exporting image: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def export_to_jpg(self, processed_img: Optional[Image.Image]):
        """Export processed image to JPG format."""
        return self.export_to_format(processed_img, 'jpg')
    
    def export_to_png(self, processed_img: Optional[Image.Image]):
        """Export processed image to PNG format."""
        return self.export_to_format(processed_img, 'png')
    
    def create_interface(self) -> gr.Blocks:
        """Create and return the Gradio interface."""
        
        with gr.Blocks(title="Pixellate - Photo Processor", theme=gr.themes.Soft()) as demo:
            gr.Markdown("# 📸 Pixellate - Photo Processor")
            gr.Markdown("Process your photos with customizable cropping, resolution, file size, and format settings.")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### Upload & Settings")
                    
                    input_image = gr.Image(
                        label="Upload Photo",
                        type="pil",
                        height=300
                    )
                    
                    with gr.Accordion("Crop Settings", open=True):
                        crop_size_inches = gr.Slider(
                            minimum=self.config.min_crop_size_inches,
                            maximum=self.config.max_crop_size_inches,
                            value=self.config.default_crop_size_inches,
                            step=self.config.crop_step,
                            label="Crop Size (inches)",
                            info="Size of the smaller dimension (maintains original aspect ratio)"
                        )
                        dpi = gr.Slider(
                            minimum=self.config.min_dpi,
                            maximum=self.config.max_dpi,
                            value=self.config.default_dpi,
                            step=1,
                            label="DPI",
                            info="Dots per inch for inch-based calculations"
                        )
                    
                    with gr.Accordion("Resolution Settings", open=True):
                        target_width = gr.Number(
                            value=self.config.default_width,
                            label="Target Width (pixels)",
                            precision=0
                        )
                        target_height = gr.Number(
                            value=self.config.default_height,
                            label="Target Height (pixels)",
                            precision=0
                        )
                    
                    with gr.Accordion("File Size & Format", open=True):
                        max_file_size_mb = gr.Slider(
                            minimum=self.config.min_file_size_mb,
                            maximum=self.config.max_file_size_mb,
                            value=self.config.default_max_file_size_mb,
                            step=self.config.file_size_step,
                            label="Max File Size (MB)"
                        )
                        output_format = gr.Radio(
                            choices=self.config.supported_formats,
                            value=self.config.default_format,
                            label="Output Format"
                        )
                    
                    process_btn = gr.Button("Process Image", variant="primary", size="lg")
                    
                with gr.Column(scale=1):
                    gr.Markdown("### Processed Result")
                    
                    output_image = gr.Image(
                        label="Processed Photo",
                        type="pil",
                        height=400
                    )
                    
                    info_output = gr.Textbox(
                        label="Processing Info",
                        interactive=False,
                        lines=3
                    )
                    
                    # Store processed image in state for export
                    processed_image_state = gr.State(value=None)
                    
                    with gr.Row():
                        export_jpg_btn = gr.Button("Export as JPG", variant="secondary")
                        export_png_btn = gr.Button("Export as PNG", variant="secondary")
                    
                    export_jpg_file = gr.File(
                        label="Download JPG",
                        visible=True,
                        interactive=False
                    )
                    export_png_file = gr.File(
                        label="Download PNG",
                        visible=True,
                        interactive=False
                    )
            
            process_btn.click(
                fn=self.process_image,
                inputs=[
                    input_image, crop_size_inches, target_width, target_height,
                    max_file_size_mb, output_format, dpi
                ],
                outputs=[output_image, info_output, processed_image_state]
            )
            
            export_jpg_btn.click(
                fn=self.export_to_jpg,
                inputs=[processed_image_state],
                outputs=[export_jpg_file]
            )
            
            export_png_btn.click(
                fn=self.export_to_png,
                inputs=[processed_image_state],
                outputs=[export_png_file]
            )
            
            gr.Markdown("### Instructions")
            gr.Markdown("""
            1. Upload your photo using the upload area
            2. Adjust the settings:
               - **Crop Size**: Size in inches for the smaller dimension (maintains original aspect ratio)
               - **DPI**: Dots per inch (affects pixel size of crop)
               - **Target Resolution**: Final width and height in pixels
               - **Max File Size**: Maximum file size in MB
               - **Output Format**: Choose JPG or PNG (used for processing/compression)
            3. Click "Process Image" to apply the settings
            4. Use the **Export as JPG** or **Export as PNG** buttons to download the processed image in your preferred format
            """)
        
        return demo
    
    def launch(self, share: bool = False, **kwargs):
        """
        Launch the Gradio interface.
        
        Args:
            share: Whether to create a public link
            **kwargs: Additional arguments for demo.launch()
        """
        demo = self.create_interface()
        server_name = kwargs.get('server_name', self.config.server_name)
        server_port = kwargs.get('server_port', self.config.server_port)
        demo.launch(share=share, server_name=server_name, server_port=server_port)

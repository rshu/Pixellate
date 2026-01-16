"""
Gradio UI module for Pixellate.
"""

import gradio as gr
from PIL import Image
import os
import tempfile
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
    
    def process_and_download(
        self,
        img: Optional[Image.Image],
        crop: float,
        w: float,
        h: float,
        max_size: float,
        fmt: str,
        dpi_val: float
    ) -> Tuple[Optional[Image.Image], str, Optional[str]]:
        """
        Process image and prepare for download.
        
        Args:
            img: Input image
            crop: Crop size in inches
            w: Target width
            h: Target height
            max_size: Max file size in MB
            fmt: Output format
            dpi_val: DPI value
            
        Returns:
            Tuple of (processed_image, info_message, file_path)
        """
        if img is None:
            return None, "Please upload an image first.", None
        
        processed_img, info = self.processor.process_image(
            img, crop, int(w), int(h), max_size, fmt, int(dpi_val)
        )
        
        if processed_img is not None:
            # Save to temporary file for download
            temp_dir = tempfile.gettempdir()
            temp_path = os.path.join(temp_dir, f"pixellate_processed.{fmt.lower()}")
            
            if fmt.lower() in ['jpg', 'jpeg']:
                processed_img.save(temp_path, format='JPEG', quality=95, optimize=True)
            else:
                processed_img.save(temp_path, format='PNG', optimize=True)
            
            return processed_img, info, temp_path
        else:
            return None, info, None
    
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
                            info="Crops to a square of this size"
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
                    
                    download_btn = gr.File(
                        label="Download Processed Image",
                        visible=False
                    )
            
            process_btn.click(
                fn=self.process_and_download,
                inputs=[
                    input_image, crop_size_inches, target_width, target_height,
                    max_file_size_mb, output_format, dpi
                ],
                outputs=[output_image, info_output, download_btn]
            )
            
            gr.Markdown("### Instructions")
            gr.Markdown("""
            1. Upload your photo using the upload area
            2. Adjust the settings:
               - **Crop Size**: Size in inches for the initial square crop
               - **DPI**: Dots per inch (affects pixel size of crop)
               - **Target Resolution**: Final width and height in pixels
               - **Max File Size**: Maximum file size in MB
               - **Output Format**: Choose JPG or PNG
            3. Click "Process Image" to apply the settings
            4. Download the processed image
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

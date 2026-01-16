# Pixellate

A Python-based photo processing tool built with Gradio that allows you to process personal photos with customizable settings for cropping, resolution, file size, and format.

## Features

- **Crop to Inches**: Crop photos to a specified size in inches (with adjustable DPI)
- **Custom Resolution**: Set target width and height in pixels (e.g., 461 x 579)
- **File Size Control**: Compress images to meet a maximum file size requirement (default: < 1MB)
- **Format Selection**: Export processed images as JPG or PNG
- **User-Friendly Interface**: Simple Gradio web interface with adjustable parameters

## Installation

1. Clone or download this repository
2. Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Run the application:

```bash
python main.py
```

Alternatively, you can still use the old entry point:

```bash
python app.py
```

2. Open your web browser and navigate to the URL shown in the terminal (typically `http://localhost:7860`)

3. Use the interface to:
   - Upload your photo
   - Adjust settings:
     - **Crop Size (inches)**: Size for the initial square crop (default: 2 inches)
     - **DPI**: Dots per inch for inch-to-pixel conversion (default: 300)
     - **Target Width/Height**: Final resolution in pixels (default: 461 x 579)
     - **Max File Size**: Maximum file size in MB (default: 1 MB)
     - **Output Format**: Choose between JPG or PNG
   - Click "Process Image" to apply the settings
   - Download the processed image

## Project Structure

```
Pixellate/
├── pixellate/           # Main package
│   ├── __init__.py      # Package initialization
│   ├── config.py        # Configuration settings
│   ├── image_processor.py  # Image processing logic
│   └── ui.py            # Gradio UI components
├── main.py              # Main entry point
├── app.py               # Legacy entry point (still supported)
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## How It Works

1. The image is first cropped to a square based on the specified inch size and DPI
2. The cropped image is then resized to the target resolution
3. The image is compressed (quality adjusted for JPG, optimization for PNG) to meet the file size requirement
4. The final image is exported in the selected format

## Development

The project is structured in a modular way:
- **`pixellate/config.py`**: Contains all default configuration settings
- **`pixellate/image_processor.py`**: Handles all image processing operations
- **`pixellate/ui.py`**: Manages the Gradio interface
- **`main.py`**: Entry point that launches the application

You can customize the default settings by modifying `pixellate/config.py` or by creating a custom `Config` instance.

## Requirements

- Python 3.7+
- Gradio 4.0.0+
- Pillow 10.0.0+

## License

MIT License - see LICENSE file for details
"""
Legacy entry point for Pixellate.
This file is kept for backward compatibility.
For new code, use main.py instead.
"""

from pixellate.ui import PixellateUI
from pixellate.config import DEFAULT_CONFIG

if __name__ == "__main__":
    ui = PixellateUI(config=DEFAULT_CONFIG)
    ui.launch(share=False)

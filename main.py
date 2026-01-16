"""
Main entry point for Pixellate application.
"""

from pixellate.ui import PixellateUI
from pixellate.config import DEFAULT_CONFIG


def main():
    """Main function to launch the application."""
    ui = PixellateUI(config=DEFAULT_CONFIG)
    ui.launch(share=False)


if __name__ == "__main__":
    main()

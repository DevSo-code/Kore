"""Main entry point for Kore application.

This module initializes and launches the application.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.app import App

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)

logger = logging.getLogger(__name__)


def main() -> None:
    """Main entry point for the application."""
    try:
        logger.info("Starting Kore application...")
        app = App()
        app.mainloop()
        logger.info("Kore application closed.")
    except Exception as e:
        logger.error(f"Failed to start application: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()

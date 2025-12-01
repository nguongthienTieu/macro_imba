#!/usr/bin/env python3
"""
Dota Imba Macro Tool

A macro tool for Dota Imba with:
- Quick-cast: Instantly cast skills at cursor position
- Auto-cast: Automatically repeat skill casts
- Custom Macros: Create your own key sequences

Run this file to start the application.
"""

import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import run_app


if __name__ == "__main__":
    sys.exit(run_app())

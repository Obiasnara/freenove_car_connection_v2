import os
import sys

# Get the absolute path of the directory containing the script
script_dir = os.path.dirname(os.path.abspath(__file__))
# Add the parent directory (root directory) to sys.path
root_dir = os.path.dirname(script_dir)
sys.path.insert(0, root_dir)
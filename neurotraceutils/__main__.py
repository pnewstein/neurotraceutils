"""
commandline interface for the utility
"""
import sys
from pathlib import Path

from imaris_ims_file_reader.ims import ims

from .output import write_swcs

def extract_swcs(out_dir):
    img = ims(Path(sys.argv[1]))
    write_swcs(img, out_dir)

extract_swcs(None)

"""
commandline interface for the utility
"""
import sys
from pathlib import Path

from imaris_ims_file_reader.ims import ims
from .swc import extract_swcs

img = ims(Path(sys.argv[1]))
swcs = extract_swcs(img)
for name, swc in swcs.items():
    if swc is None:
        continue
    Path(name).with_suffix(".swc").write_text(swc.to_csv(sep=" ", header=False, index=False), encoding="utf-8")

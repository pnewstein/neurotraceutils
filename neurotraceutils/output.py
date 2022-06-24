"""
This module is responcible for 
interfacing with the filesystem to 
do the proper output
"""
from pathlib import Path
from typing import Optional

from imaris_ims_file_reader.ims import ims

from .swc import extract_swcs

def write_swcs(img: ims, out_dir: Optional[Path] = None):
    """
    Writes out the swc files to the output directory
    """
    if out_dir is None:
        out_dir = Path(img.filePathComplete).with_suffix("")
    out_dir.mkdir(exist_ok=True)
    swcs = extract_swcs(img)
    for name, swc in swcs.items():
        if swc is None:
            # This swc failed to be created
            continue
        (out_dir / name).with_suffix(".swc").write_text(
            swc.to_csv(sep=" ", header=False, index=True), encoding="utf-8"
        )
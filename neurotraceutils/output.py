"""
This module is responcible for 
interfacing with the filesystem to 
do the proper output
"""
from pathlib import Path
from typing import Optional
from warnings import warn

from imaris_ims_file_reader.ims import ims

from .swc import extract_swcs, NoFilementError

def write_swcs(img: ims, out_dir: Optional[Path] = None):
    """
    Writes out the swc files to the output directory
    """
    if out_dir is None:
        out_dir = Path(img.filePathComplete).with_suffix("")
    out_dir.mkdir(exist_ok=True)
    try:
        swcs = extract_swcs(img)
    except NoFilementError:
        warn(f"{img.filePathComplete} contains no filements")
        return

    for name, swc_df in swcs.items():
        if swc_df is None:
            # This swc failed to be created
            continue
        (out_dir / name).with_suffix(".swc").write_text(
            swc_df.to_csv(sep=" ", header=False, index=True), encoding="utf-8"
        )

"""
This module is responcible for 
interfacing with the filesystem to 
do the proper output
"""
from pathlib import Path
from typing import Optional
from warnings import warn

from h5py import File

from .swc import extract_swcs, NoFilementError

def write_swcs(h5f: File, out_dir_parent: Optional[Path] = None):
    """
    Writes out the swc files to the path out_dir_parent/<imaris file name>
    """
    if out_dir_parent is None:
        out_dir_parent = Path(h5f.filename).parent
    out_dir = out_dir_parent / Path(h5f.filename).with_suffix("").name
    out_dir.mkdir(exist_ok=True, parents=True)
    assert out_dir.exists()
    try:
        swcs = extract_swcs(h5f)
    except NoFilementError:
        warn(f"{h5f.filename} contains no filements")
        return

    for name, swc_df in swcs.items():
        if swc_df is None:
            # This swc failed to be created
            continue
        (out_dir / name).with_suffix(".swc").write_text(
            swc_df.to_csv(sep=" ", header=False, index=True), encoding="utf-8"
        )

"""
This module is responcible for 
interfacing with the filesystem to 
do the proper output
"""
from pathlib import Path
from typing import Optional
from warnings import warn
import json

from h5py import File
import numpy as np

from .swc import extract_swcs, NoFilementError

def write_swcs(h5f: File, out_dir_parent: Optional[Path] = None, header=True):
    """
    Writes out the swc files to the path out_dir_parent/<imaris file name>
    header is whether to put a header with some information
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
        out_str = swc_df.to_csv(sep=" ", header=False, index=True)
        if header:
            out_str = "\n".join(
                ["# neurotraceutils 0.1",
                 f"# file_name {h5f.filename}",
                 "# unit um",
                 f"# isotime {np.array(h5f['DataSetInfo/Document'].attrs['CreationDate']).tobytes().decode('utf-8')}",
                 out_str
                 ]
            )
        (out_dir / name).with_suffix(".swc").write_text(
            out_str, encoding="utf-8"
        )

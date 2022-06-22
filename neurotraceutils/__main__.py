import sys
from pathlib import Path
import navis

from imaris_ims_file_reader.ims import ims
from .swc import extract_swcs


img = ims(Path(sys.argv[1]))
swcs = extract_swcs(img)
for name, swc in swcs.items():
    Path(name).with_suffix(".swc").write_text(swc.to_csv(sep=" ", header=False, index=False), 'utf-8')



from pathlib import Path
import json

import pandas as pd
import numpy as np

from neurotraceutils import swc
from imaris_ims_file_reader import ims

HERE = Path(__file__).parent

def dump_data(path: Path, num: int):
    """
    opens the path and dumps the data to the num dir
    """
    data_dir = HERE / "data" / f"{num:02d}"
    data_dir.mkdir(exist_ok=True, parents=True)
    img = ims(path)
    filement_paths = [f"Scene8/Content/{key}" for key in img.hf["Scene8"]["Content"].keys() if "Filament" in key]
    filement = img.hf[filement_paths[0]]
    nchildren = filement["Vertex"].size
    (data_dir / "nchildren.txt").write_text(str(nchildren))
    edge = pd.DataFrame(np.array(filement["Edge"]))
    edge += 1
    edge.to_json(data_dir / "edge.json")
    parents = swc.assign_parents(nchildren, edge)
    (data_dir / "parents.json").write_text(json.dumps(parents.to_list()))


def load_edge(num: int) -> tuple[int, pd.DataFrame, pd.DataFrame]:
    """
    loads the edge file from disk
    returns nchildren edges and parents
    """
    data_dir = HERE / "data" / f"{num:02d}"
    nchildren = int((data_dir / "nchildren.txt").read_text("utf-8"))
    edge = pd.read_json(data_dir / "edge.json")
    parents = json.loads((data_dir / "parents.json").read_text("utf-8"))
    return nchildren, edge, parents


def test_parents1():

    nchildren, edge, read_parents = load_edge(1)
    calculated_parents = swc.assign_parents(nchildren, edge)
    assert all(r == c for r, c in zip(read_parents, calculated_parents))


if __name__ == '__main__':
    dump_data(Path("/storage/ims/bad.ims"), 1)

"""
contains code that extracts swc files from imaris files
"""
from dataclasses import dataclass
from warnings import warn

import numpy as np
import pandas as pd
from imaris_ims_file_reader.ims import ims

class IllegalFilementError(Exception):
    pass


def extract_swcs(img: ims) -> dict[str, pd.DataFrame]:
    """
    extracts all of the filiments in an image to a dataframe in the swc format
    outputs a dict where the keys are the names of the filiments and the values are the dataframes
    the columns of the dataframe are:
        "Number", "Identifier", "PositionX", "PositionY", "PositionZ", "Radius", "Parent"
    """
    scale = img.metaData[(0, 0, 0, 'resolution')]
    """the scale of the image in (z, y, x)"""
    if scale[1] != scale[2]:
        # I'm not entirely sure which is y and which is x
        raise ValueError("Only voxels that are square in the xy dimention are currently supported")
    filement_paths = [f"Scene8/Content/{key}" for key in img.hf["Scene8"]["Content"].keys() if "Filament" in key]
    names = [img.read_attribute(fp, "Name") for fp in filement_paths]
    out = {n: None for n in names}
    for name, filement_path in zip(names, filement_paths):
        filement = img.hf[filement_path]
        vertex = pd.DataFrame(np.array(filement["Vertex"]))
        edge = pd.DataFrame(np.array(filement["Edge"]))
        try:
            parents = assign_parents(vertex.shape[0], edge)
        except IllegalFilementError as e:
            warn(f'"{name}" failed with error message "{e}"')
            continue
        swc = vertex.copy()
        # scale the swc
        swc["PositionZ"] /= scale[0]
        swc["PositionY"] /= scale[1]
        swc["PositionX"] /= scale[2]
        swc.insert(len(swc.columns), "Parent", parents)
        # I cant extract information about identifers
        swc.insert(0, "Identifier", np.zeros(len(swc.index), np.int8))
        swc.insert(0, "Number", np.array(swc.index+1))
        out[name] = swc
    return out


@dataclass
class Branch:
    first_node: int
    parent_node: int

    def to_tuple(self) -> tuple:
        """
        (first_node, parent_node)
        """
        return self.first_node, self.parent_node


def assign_parents(nchildren: int, edge: pd.DataFrame) -> np.ndarray:
    """
    Assigns the parent for each vertex based on the edges
    from the edges in the imaris file returns the parents column which is compatable
    with swc files
    nchildren is the number of children
    """
    connectivity_matrix = make_connectivity_matrix(nchildren, edge)
    # traverse through the filement going down every branch
    parents = np.zeros(nchildren, np.int64) - 2
    """The output of this function"""
    visited = np.zeros(nchildren, np.bool8)
    """whether each node has been visited"""
    unexplored = [Branch(1, -1)]
    """The unexplored branches. will increase and decrease in size during the loop"""
    while unexplored:
        # open an unexplored branch
        current, parent = unexplored.pop().to_tuple()
        # explore this branch
        while True:
            parents[current-1] = parent
            visited[current] = True
            next_points = [node for node in search_partners(connectivity_matrix, current) if not visited[node]]
            if len(next_points) == 0:
                # you finished exploring this branch
                break
            if len(next_points) > 1:
                # you found a branch point! add to unexplored for now
                for next_branch in next_points[1:]:
                    unexplored.append(Branch(next_branch, current))
            # move to the next point on this branch
            current, parent = next_points[0], current
    # check for errors
    if np.any(np.logical_not(visited)):
        raise IllegalFilementError("Discontinuous filement")
    if np.any(parents == -2):
        raise IllegalFilementError("Did not explore some nodes")
    return parents


def make_connectivity_matrix(nchildren: int, edge: pd.DataFrame) -> np.ndarray:
    """
    Makes a matrix of which vertex is connected to each vertex
    """
    # maybe this can be implemented in c
    connectivity_matrix = np.zeros((nchildren, nchildren), np.bool8)
    for _, (node1, node2) in edge.iterrows():
        connectivity_matrix[node1, node2] = True
        connectivity_matrix[node2, node1] = True
    return connectivity_matrix


def search_partners(connectivity_matrix: np.ndarray, node: int) -> list[int]:
    """
    Finds all of the partners of a node
    """
    return list(np.where(connectivity_matrix[node])[0])

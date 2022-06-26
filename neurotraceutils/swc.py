"""
contains code that extracts swc files from imaris files
"""
from __future__ import annotations
from dataclasses import dataclass
from warnings import warn

import numpy as np
import pandas as pd
import h5py

class IllegalFilementError(Exception):
    pass

class NoFilementError(Exception):
    pass

def extract_swcs(h5f: h5py.File) -> dict[str, pd.DataFrame]:
    """
    extracts all of the filiments in an image to a dataframe in the swc format
    outputs a dict where the keys are the names of the filiments and the values are the dataframes
    The index is the node number
    the columns of the dataframe are:
         "PositionX", "PositionY", "PositionZ", "Radius", "Parent"
    """
    # get scale from metadata
    def byte_array_to_float(byte_array: np.ndarray) -> float:
        return float(byte_array.tobytes().decode("utf-8"))
    metadata = h5f["DataSetInfo/Image"]
    scale: dict[str, float] = {}
    for i, dim in enumerate("XYZ"):
        scale[dim] = (
            byte_array_to_float(metadata.attrs[f"ExtMax{i}"])
            - byte_array_to_float(metadata.attrs[f"ExtMin{i}"])
        ) / byte_array_to_float(metadata.attrs[dim])
    try:
        filement_paths = [f"Scene8/Content/{key}" for key in h5f["Scene8/Content"].keys() if "Filament" in key]
    except KeyError as e:
        raise NoFilementError from e
    names = [h5f[fp].attrs["Name"].tobytes().decode("utf-8") for fp in filement_paths]
    out = {n: None for n in names}
    for name, filement_path in zip(names, filement_paths):
        filement = h5f[filement_path]
        vertex = pd.DataFrame(np.array(filement["Vertex"]))
        edge = pd.DataFrame(np.array(filement["Edge"]))
        # switch to 1 based indexing
        vertex.index = vertex.index + 1
        edge = edge+1
        try:
            parents = assign_parents(vertex.shape[0], edge)
        except IllegalFilementError as e:
            warn(f'"{name}" failed with error message "{e}"')
            continue
        swc = vertex.copy()
        # scale the swc
        swc["PositionZ"] /= scale['Z']
        swc["PositionY"] /= scale['Y']
        swc["PositionX"] /= scale['X']
        swc.insert(len(swc.columns), "Parent", parents)
        # I cant extract information about identifers
        swc.insert(0, "Identifier", np.zeros(len(swc.index), np.int8))
        
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


def assign_parents(nchildren: int, edge: pd.DataFrame) -> pd.Series:
    """
    Assigns the parent for each vertex based on the edges
    from the edges in the imaris file returns the parents column which is compatable
    with swc files
    nchildren is the number of children
    """
    INT_NAN = -2
    connectivity_matrix = make_connectivity_matrix(nchildren, edge)
    # traverse through the filement going down every branch
    parents = pd.Series(data=np.array(nchildren, np.int64) + INT_NAN, index=range(1, nchildren+1))
    """The output of this function, default is -2"""
    visited = pd.Series(data=np.zeros(nchildren, np.bool8), index=range(1, nchildren+1))
    """whether each node has been visited"""
    unexplored = [Branch(1, -1)]
    """The unexplored branches. will increase and decrease in size during the loop"""
    while unexplored:
        # open an unexplored branch
        current, parent = unexplored.pop().to_tuple()
        # explore this branch
        while True:
            parents[current] = parent
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
    if np.any(parents == INT_NAN):
        raise IllegalFilementError("Did not explore some nodes")
    return parents


def make_connectivity_matrix(nchildren: int, edge: pd.DataFrame) -> np.ndarray:
    """
    Makes a matrix of which vertex is connected to each vertex
    uses 1 based indexing
    """
    # maybe this can be implemented in c
    connectivity_matrix = np.zeros((nchildren+1, nchildren+1), np.bool8)
    for _, (node1, node2) in edge.iterrows():
        connectivity_matrix[node1, node2] = True
        connectivity_matrix[node2, node1] = True
    return connectivity_matrix


def search_partners(connectivity_matrix: np.ndarray, node: int) -> list[int]:
    """
    Finds all of the partners of a node
    """
    return list(np.where(connectivity_matrix[node])[0])

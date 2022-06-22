"""
contains code that extracts swc files from imaris files
"""
from typing import Optional

import numpy as np
import pandas as pd
from imaris_ims_file_reader.ims import ims


import matplotlib
matplotlib.use("QtAgg")
import matplotlib.pyplot as plt

class IllegalFilementError(Exception):
    pass


def extract_swcs(img: ims) -> dict[str, pd.DataFrame]:
    """
    extracts all of the filiments in an image to a dataframe in the swc format
    outputs a dict where the keys are the names of the filiments and the values are the dataframes
    the columns of the dataframe are:
        "Number", "Identifier", "PositionX", "PositionY", "PositionZ", "Radius", "Parent"
    """
    filement_paths = [f"Scene8/Content/{key}" for key in img.hf["Scene8"]["Content"].keys() if "Filament" in key]
    names = [img.read_attribute(fp, "Name") for fp in filement_paths]
    out = {n: None for n in names}
    for name, filement_path in zip(names, filement_paths):
        filement = img.hf[filement_path]
        vertex = pd.DataFrame(np.array(filement["Vertex"]))
        edge = pd.DataFrame(np.array(filement["Edge"]))
        branch_points = map_branch_points(edge)
        segments = get_segments(branch_points, vertex.shape[0])
        parents = assign_parents(vertex.shape[0], branch_points, segments)
        # parents = assign_parents(edge["VertexA"], edge["VertexB"], vertex.shape[0], branches)
        swc = vertex.copy()
        swc.insert(len(swc.columns), "Parent", parents)
        # I cant extract information about identifers
        swc.insert(0, "Identifier", np.zeros(len(swc.index), np.int8))
        swc.insert(0, "Number", np.array(swc.index))
        out[name] = swc
        plt.plot(swc["Parent"])
        plt.show()
    return out


def map_branch_points(edge: pd.DataFrame) -> list[set[int]]:
    """
    Finds the points where there is discontinuous connections
    returns a list of all of the partners of that discontinous contact
    """
    discontinous = edge["VertexB"] - edge["VertexA"] != 1
    branchpoint_pairs = np.vstack((edge["VertexA"][discontinous], edge["VertexB"][discontinous])).T
    out: list[set[int]] = []
    for branchpoint_pair in branchpoint_pairs:
        branch_sorted = False
        for branch in out:
            if any(b in branch for b in branchpoint_pair):
                # add current branch pair to the branch in which it fits branch = branch.union(set(branchpoint_pair)) branch_sorted = True
                break
        if not branch_sorted:
            # add to a new branch
            out.append(set(branchpoint_pair))
    return out

def get_segments(branch_points: list[set[int]], nvertex: int) -> np.ndarray:
    """
    gets the coninuous segments from the branch points
    returns an array like this
        [[start end]
         [start end]
         [start end]]
    """
    # get all of the indecies involved in branges
    flat_branch_points = sorted(list(set().union(*branch_points)))
    # shape it into a numpy array where the same vertex that ends a segment starts the next segment
    flat_repeated_branch_points =  sorted(flat_branch_points + flat_branch_points[1:] + [nvertex])
    return np.array(flat_repeated_branch_points).reshape((len(flat_repeated_branch_points) // 2, 2))
    

def assign_parents(nchildren: int, branch_points: list[set[int]], segments: np.ndarray) -> np.ndarray:
    """
    Assigns the parent for each vertex based on the vertex a and vertex b
    from the edges in the imaris file returns the parents column which is compatable
    with swc files
    nchildren is the number of children
    """
    print(segments)
    quit()
    parents = np.arange(nchildren) - 1
    grounded_edge_indecies = update_grounded_edges({0}, branch_points)
    ungrounded_segments = list(range(len(segments)))
    last_len_ungrounded_branches: Optional[int] = None
    # Find a grounded segment. Update grounded_edge_indecies. remove that segment from ungrounded_segments
    # define the parentage relationship
    while len(ungrounded_segments) != 0:
        if last_len_ungrounded_branches is not None:
            # we just looped through all of the ungrounded_segments and found nothing grounded
            if last_len_ungrounded_branches == len(ungrounded_segments):
                raise IllegalFilementError("Some filements are disconnected")
        for ungrounded_segment_ind, segment in enumerate(segments[ungrounded_segments]):
            last_len_ungrounded_branches = len(ungrounded_segments)
            if any(terminus in grounded_edge_indecies for terminus in segment):
                # define parentage
                if 0 not in segment:
                    for terminus in segment:
                        if terminus in grounded_edge_indecies:
                            for branch in branch_points:
                                if terminus in branch:
                                    if 
                grounded_edge_indecies.union(set(segment))
                grounded_edge_indecies = update_grounded_edges(grounded_edge_indecies, branch_points)
                ungrounded_segments.pop(ungrounded_segment_ind)
                break
                

def update_grounded_edges(grounded_edge_indecies: set[int], branch_points: list[set[int]]) -> set[int]:
    """
    uses branch point to make sure that all indecies involved in a branch are equaly grounded
    """
    indecies_to_add: set[int] = set()
    for branch in branch_points:
        for grounded_edge_index in grounded_edge_indecies:
            if grounded_edge_index in branch:
                indecies_to_add.union(branch)
    grounded_edge_indecies.union(indecies_to_add)
    return grounded_edge_indecies


# def assign_parents(va: np.ndarray, vb: np.ndarray, nchildren: int) -> np.ndarray:
    # """
    # Assigns the parent for each vertex based on the vertex a and vertex b
    # from the edges in the imaris file returns the parents column which is compatable
    # with swc files
    # nchildren is the number of children
    # """
    # # start off with negitive 1s
    # parents = np.zeros(nchildren) - 1
    # for child, _ in enumerate(parents):
        # if child == 0:
            # continue
        # edge_index = np.nonzero(np.array(vb == child))[0]
        # if edge_index.size != 1:
            # raise IllegalFilementError(f"node {child} has {len(edge_index)} parents")
        # parents[child] = va[edge_index[0]]
    # return parents

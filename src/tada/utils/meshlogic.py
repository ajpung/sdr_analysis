# ==============================================================================
#                               ANTENNA GEOMETRY                               =
# ==============================================================================

"""
   Computing radiation from known antenna parameters.
"""

import math
from dataclasses import dataclass
from typing import Tuple

import numpy as np

import plotly.graph_objs as go

# from meshlib import mrmeshnumpy as mn
# from meshlib.mrmeshpy import Mesh
# from meshlib import mrmeshpy as mm

# from rats.utils.coordinates import ecef_to_lla


# @dataclass
# class DataMesh:
#    x: float
#    y: float
#    z: float
#    faces: float
#   verts: float
#    mesh: Mesh

'''
# ============================= General mesh tools =============================
# Offset mesh from origin
def offset_from_origin(mesh: Mesh, offset: np.ndarray, mag: float) -> Mesh:
    """
    Rotates, offsets, and magnifies (ROM) mesh

            Parameters:
                    mesh: The initial Meshlib mesh object
                    offset: ECEF offset in [X,Y,Z]
            Returns:
                    np.ndarray: An offset copy of the original Meshlib mesh object
    """
    # Copy original mesh to avoid overwrite
    cmesh = mm.copyMesh(mesh)
    ox, oy, oz = offset

    # ----------------------- Define rotation coordinates ----------------------
    # Handle special angles
    if oy == 0:
        oy = 0.01
    # Z-rotation
    rot_center = mm.Vector3f(0, 0, 0)
    rot_axis = mm.Vector3f(0, 0, 1)
    rot_angle = math.atan(oy / (ox + 1e-6))
    rot_z = mm.Matrix3f.rotation(rot_axis, rot_angle)
    rotation = mm.AffineXf3f.xfAround(rot_z, rot_center)
    cmesh.transform(rotation)
    # Y-rotation
    rot_center = mm.Vector3f(0, 0, 0)
    rot_axis = mm.Vector3f(1, 0, 0)
    rot_angle = math.atan(oz / (oy + 1e-6))
    rot_y = mm.Matrix3f.rotation(rot_axis, rot_angle)
    rotation = mm.AffineXf3f.xfAround(rot_y, rot_center)
    cmesh.transform(rotation)

    # ------------------------------ Magnify mesh ------------------------------
    # cmesh.transform(mm.AffineXf3f.linear(mm.Matrix3f.scale(mag,mag,mag)))

    # ---------------------------- Reposition mesh -----------------------------
    new_pos = mm.Vector3f(ox, oy, oz)
    old_pos = mm.Vector3f(0, 0, 0)
    move = mm.AffineXf3f.translation(new_pos - old_pos)
    cmesh.transform(move)

    return cmesh


# Correct mesh faces
def correct_mesh(mesh: Mesh) -> Mesh:
    """
    Correct directions of the normals within a mesh

            Parameters:
                    mesh: The initial Meshlib mesh object

            Returns:
                    np.ndarray: The corrected Meshlib mesh object
    """
    if mesh.topology.findHoleRepresentiveEdges().size() != 0:
        mesh = mm.offsetMesh(mesh, 0.0)
    else:
        if mesh.volume() < 0.0:
            mesh.topology.flipOrientation()
    mesh.pack()
    return mesh


# Generate faces, vertices, and faces from mesh
def trace_from_mesh(mesh: Mesh) -> Tuple[np.ndarray, np.ndarray, go.Mesh3d]:
    """
    Creates a trace from

            Parameters:
                    mesh: The initial Meshlib mesh object

            Returns:
                    go.Mesh3d: Plotly Mesh3D trace using the faces and vertices
    """
    # Define faces and vertices from the original mesh
    verts = mn.getNumpyVerts(mesh)
    verts = verts * 0.01
    faces = mn.getNumpyFaces(mesh.topology)
    # Correct shape of the vertices/faces to fit other computation
    verts = np.transpose(verts)
    faces = np.transpose(faces)

    # Create Plotly trace for visualization
    trace = go.Mesh3d(
        x=verts[0], y=verts[1], z=verts[2], i=faces[0], j=faces[1], k=faces[2]
    )

    return faces, verts, trace


# Convert spherical mesh to XYZ
def sph2xyz(
    gain_data: Mesh, theta: np.ndarray, phi: np.ndarray, mag: float = 1.0
) -> DataMesh:
    """
    Convert spherical coordinates for antenna gain to Cartesian

            Parameters:
                    gain_data: Mesh object of antenna gain
                    theta: Theta angles [deg]
                    phi: Phi angles [deg]
                    mag: Size amplification factor, defaults to 1

            Returns:
                    xyzgain: 2D array of Cartesian gain cloud
    """
    # Break into X,Y,Z
    x_comp, y_comp, z_comp = (
        np.array(
            [np.sin(phi) * np.cos(theta), np.sin(phi) * np.sin(theta), np.cos(phi)]
        )
        * gain_data
        * mag
    )

    # check that gain data is square
    assert gain_data.shape[0] == gain_data.shape[1]
    assert gain_data.shape[0] <= 360, "Gain cannot have more than 360 elements"

    size = gain_data.shape[0]

    # Create triangulation
    i = np.empty(2 * size**2, dtype=int)
    j = np.empty(2 * size**2, dtype=int)
    k = np.empty(2 * size**2, dtype=int)
    counter = 0
    for o1 in range(size):
        for o2 in range(size):
            i[counter] = o1 * size + o2
            j[counter] = ((o1 + 1) % size) * size + o2
            k[counter] = o1 * size + ((o2 + 1) % size)
            counter = counter + 1
            i[counter] = o1 * size + o2
            j[counter] = ((o1 + size - 1) % size) * size + o2
            k[counter] = o1 * size + ((o2 + size - 1) % size)
            counter = counter + 1
    # Convert raw gain [dB] object to mesh
    gain_vert = np.stack(
        (x_comp.flatten(), y_comp.flatten(), z_comp.flatten()), axis=-1
    ).reshape(-1, 3)
    gain_face = np.stack((i.flatten(), j.flatten(), k.flatten()), axis=-1).reshape(
        -1, 3
    )
    gain_face = gain_face.astype(np.int32)
    gain_mesh = mn.meshFromFacesVerts(gain_face, gain_vert)
    gain_mesh = mm.offsetMesh(gain_mesh, 0.0)
    gain_mesh = correct_mesh(gain_mesh)
    gain_face, gain_vert, gain_trace = trace_from_mesh(gain_mesh)
    # --- Define fields in the datamesh object
    xyz_gain = DataMesh(
        x=x_comp, y=y_comp, z=z_comp, faces=gain_face, verts=gain_vert, mesh=gain_mesh
    )
    return xyz_gain
'''

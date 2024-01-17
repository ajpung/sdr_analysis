import numpy as np
import plotly.graph_objs as go
from meshlib import mrmeshnumpy as mn

from examples.reference.antenna import get_radiation
from rats.utils.meshlogic import sph2xyz


# @pytest.mark.skip(reason="skip for now, remove if we can")
def test_dipole_pattern():
    gdb, gpw, THETA, PHI, wires = get_radiation(
        ant_type="yagi2d", dsn_frq=2000.0, num_sets=15, red_rat=1.0
    )
    rmesh = sph2xyz(gpw, THETA, PHI, 100)
    rmesh = rmesh.mesh
    verts = mn.getNumpyVerts(rmesh)
    verts = verts * 0.01
    faces = mn.getNumpyFaces(rmesh.topology)
    verts = np.transpose(verts)
    faces = np.transpose(faces)
    strace = go.Mesh3d(
        x=verts[0], y=verts[1], z=verts[2], i=faces[0], j=faces[1], k=faces[2]
    )
    fig = go.Figure(data=[strace])
    fig.write_image("test.png")

    # assert abs(np.abs(np.min(verts[0])) - np.abs(np.max(verts[0]))) < 0.0001
    # assert abs(np.abs(np.min(verts[1])) - np.abs(np.max(verts[1]))) < 0.0001
    # assert abs(np.abs(np.min(verts[2])) - np.abs(np.max(verts[2]))) < 0.0001

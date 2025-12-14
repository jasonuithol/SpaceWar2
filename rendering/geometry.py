# rendering/geometry.py

import numpy as np
import os
import math

class GeometryData:
    """A container for vertices, normals, and indices."""
    def __init__(self, vertices, normals, indices=None):
        self.vertices = vertices
        self.normals = normals
        self.indices = indices

def load_obj(filename):
    """
    Loads geometry data from a simple Wavefront .OBJ file.
    Assumes all faces are triangles and uses the format 'v//vn'.
    """
    filepath = os.path.join("assets", filename)
    filepath = os.path.abspath(filepath)
    
    vertices = []
    normals = []
    faces = []
    
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                parts = line.split()
                if parts[0] == 'v':
                    vertices.extend([float(parts[1]), float(parts[2]), float(parts[3])])
                elif parts[0] == 'vn':
                    normals.extend([float(parts[1]), float(parts[2]), float(parts[3])])
                elif parts[0] == 'f':
                    for part in parts[1:]:
                        v_idx, _, vn_idx = part.split('/')
                        faces.append((int(v_idx), int(vn_idx)))
    except FileNotFoundError:
        print(f"Error: Asset file not found at {filepath}")
        raise

    # Flatten the data by repeating vertices/normals per face
    pyglet_vertices = []
    pyglet_normals = []
    
    for v_idx, vn_idx in faces:
        v_start_index = (v_idx - 1) * 3
        vn_start_index = (vn_idx - 1) * 3
        
        pyglet_vertices.extend(vertices[v_start_index : v_start_index + 3])
        pyglet_normals.extend(normals[vn_start_index : vn_start_index + 3])
        
    return GeometryData(pyglet_vertices, pyglet_normals)


def init_pyramid_geometry():
    """Load centered pyramid geometry data (ship) from OBJ"""
    return load_obj("pyramid.obj")

# This is the Sphere/Bullet geometry, still generated programmatically
def init_sphere_geometry(slices=16, stacks=16):
    """Create a UV sphere approximation for Sun/Bullets (Programmatic)"""
    s_vertices = []
    s_normals = []
    s_indices = []
    
    for i in range(stacks + 1):
        lat = math.pi * (-0.5 + float(i) / stacks)
        y = math.sin(lat)
        r = math.cos(lat)
        for j in range(slices + 1):
            lon = 2 * math.pi * float(j) / slices
            x = r * math.cos(lon)
            z = r * math.sin(lon)
            s_vertices.extend([x, y, z])
            s_normals.extend([x, y, z])
    
    for i in range(stacks):
        for j in range(slices):
            first = i * (slices + 1) + j
            second = first + slices + 1
            # Two triangles make a quad: (first, second, first+1), (second, second+1, first+1)
            s_indices.extend([first, second, first + 1, second, second + 1, first + 1])
    
    return GeometryData(s_vertices, s_normals, s_indices)

# rendering/geometry.py

import os
import math
from collections import namedtuple

SphereData = namedtuple('SphereData', ['vertices', 'normals', 'indices'])
GeometryData = namedtuple('GeometryData', ['vertices', 'normals', 'tex_coords'])

def load_obj(filename):
    """
    Loads geometry data from a Wavefront .OBJ file with texture coordinates.
    Assumes all faces are triangles and uses the format 'v/vt/vn'.
    """
    filepath = os.path.join("assets", filename)
    filepath = os.path.abspath(filepath)
    
    vertices = []
    normals = []
    tex_coords = []
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
                elif parts[0] == 'vt':
                    tex_coords.extend([float(parts[1]), float(parts[2])])
                elif parts[0] == 'vn':
                    normals.extend([float(parts[1]), float(parts[2]), float(parts[3])])
                elif parts[0] == 'f':
                    for part in parts[1:]:
                        # Handle both v/vt/vn and v//vn formats
                        indices = part.split('/')
                        v_idx = int(indices[0])
                        vt_idx = int(indices[1]) if len(indices) > 1 and indices[1] else None
                        vn_idx = int(indices[2]) if len(indices) > 2 else None
                        faces.append((v_idx, vt_idx, vn_idx))
    except FileNotFoundError:
        print(f"Error: Asset file not found at {filepath}")
        raise
    
    # Flatten the data by repeating vertices/normals/tex_coords per face
    pyglet_vertices = []
    pyglet_normals = []
    pyglet_tex_coords = []
    
    for v_idx, vt_idx, vn_idx in faces:
        # Add vertex
        v_start_index = (v_idx - 1) * 3
        pyglet_vertices.extend(vertices[v_start_index : v_start_index + 3])
        
        # Add normal
        if vn_idx:
            vn_start_index = (vn_idx - 1) * 3
            pyglet_normals.extend(normals[vn_start_index : vn_start_index + 3])
        else:
            pyglet_normals.extend([0.0, 0.0, 1.0])  # Default normal
        
        # Add texture coordinate
        if vt_idx:
            vt_start_index = (vt_idx - 1) * 2
            pyglet_tex_coords.extend(tex_coords[vt_start_index : vt_start_index + 2])
        else:
            pyglet_tex_coords.extend([0.0, 0.0])  # Default UV
    
    return GeometryData(pyglet_vertices, pyglet_normals, pyglet_tex_coords)


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
    
    return SphereData(s_vertices, s_normals, s_indices)

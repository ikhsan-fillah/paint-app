"""Transformasi 2D menggunakan matriks homogeneous 3x3 (numpy)."""
import math

import numpy as np
from PIL import Image


def _apply(matrix, points):
    """Terapkan matriks 3x3 ke list of (x,y). Return list of (x,y) baru."""
    result = []
    for x, y in points:
        v = np.array([x, y, 1], dtype=float)
        vt = matrix @ v
        result.append((round(vt[0]), round(vt[1])))
    return result


def translate(points, tx, ty):
    """Translasi: geser sejauh (tx, ty)."""
    M = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0,  1]
    ], dtype=float)
    return _apply(M, points)


def rotate(points, angle_deg, cx=0, cy=0):
    """Rotasi terhadap titik pusat (cx,cy) sebesar angle_deg derajat."""
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    # Geser ke origin → rotasi → geser balik
    T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]], dtype=float)
    R  = np.array([[cos_a,-sin_a,0],[sin_a,cos_a,0],[0,0,1]], dtype=float)
    T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]], dtype=float)
    M = T2 @ R @ T1
    return _apply(M, points)


def scale(points, sx, sy, cx=0, cy=0):
    """Penskalaan terhadap titik pusat (cx,cy)."""
    T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]], dtype=float)
    S  = np.array([[sx,0,0],[0,sy,0],[0,0,1]], dtype=float)
    T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]], dtype=float)
    M = T2 @ S @ T1
    return _apply(M, points)


def reflect_x(points, cy=0):
    """Refleksi terhadap garis horizontal y = cy."""
    M = np.array([
        [1, 0, 0],
        [0, -1, 2 * cy],
        [0, 0, 1]
    ], dtype=float)
    return _apply(M, points)


def reflect_y(points, cx=0):
    """Refleksi terhadap garis vertikal x = cx."""
    M = np.array([
        [-1, 0, 2 * cx],
        [0, 1, 0],
        [0, 0, 1]
    ], dtype=float)
    return _apply(M, points)


def reflect_origin(points, cx=0, cy=0):
    """Refleksi terhadap titik pusat (cx, cy)."""
    M = np.array([
        [-1, 0, 2 * cx],
        [0, -1, 2 * cy],
        [0, 0, 1]
    ], dtype=float)
    return _apply(M, points)


def reflect_diagonal(points, cx=0, cy=0):
    """Refleksi terhadap garis y = x yang melalui (cx, cy)."""
    M = np.array([
        [0, 1, cx - cy],
        [1, 0, cy - cx],
        [0, 0, 1]
    ], dtype=float)
    return _apply(M, points)


def shear_x(points, shx):
    """Shear terhadap sumbu X: x' = x + shx*y."""
    M = np.array([[1,shx,0],[0,1,0],[0,0,1]], dtype=float)
    return _apply(M, points)


def shear_y(points, shy):
    """Shear terhadap sumbu Y: y' = y + shy*x."""
    M = np.array([[1,0,0],[shy,1,0],[0,0,1]], dtype=float)
    return _apply(M, points)


def _transform_mask(mask, size, matrix):
    """Terapkan transform affine ke bitmap mask grayscale."""
    if mask is None:
        return None
    inv = np.linalg.inv(matrix)
    coeffs = (
        float(inv[0, 0]), float(inv[0, 1]), float(inv[0, 2]),
        float(inv[1, 0]), float(inv[1, 1]), float(inv[1, 2]),
    )
    return mask.transform(size, Image.AFFINE, coeffs, resample=Image.NEAREST, fillcolor=0)


def translate_mask(mask, size, tx, ty):
    M = np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ], dtype=float)
    return _transform_mask(mask, size, M)


def rotate_mask(mask, size, angle_deg, cx=0, cy=0):
    rad = math.radians(angle_deg)
    cos_a, sin_a = math.cos(rad), math.sin(rad)
    T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]], dtype=float)
    R  = np.array([[cos_a,-sin_a,0],[sin_a,cos_a,0],[0,0,1]], dtype=float)
    T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]], dtype=float)
    M = T2 @ R @ T1
    return _transform_mask(mask, size, M)


def scale_mask(mask, size, sx, sy, cx=0, cy=0):
    T1 = np.array([[1,0,-cx],[0,1,-cy],[0,0,1]], dtype=float)
    S  = np.array([[sx,0,0],[0,sy,0],[0,0,1]], dtype=float)
    T2 = np.array([[1,0,cx],[0,1,cy],[0,0,1]], dtype=float)
    M = T2 @ S @ T1
    return _transform_mask(mask, size, M)


def reflect_x_mask(mask, size, cy=0):
    M = np.array([
        [1, 0, 0],
        [0, -1, 2 * cy],
        [0, 0, 1]
    ], dtype=float)
    return _transform_mask(mask, size, M)


def reflect_y_mask(mask, size, cx=0):
    M = np.array([
        [-1, 0, 2 * cx],
        [0, 1, 0],
        [0, 0, 1]
    ], dtype=float)
    return _transform_mask(mask, size, M)


def reflect_origin_mask(mask, size, cx=0, cy=0):
    M = np.array([
        [-1, 0, 2 * cx],
        [0, -1, 2 * cy],
        [0, 0, 1]
    ], dtype=float)
    return _transform_mask(mask, size, M)


def reflect_diagonal_mask(mask, size, cx=0, cy=0):
    M = np.array([
        [0, 1, cx - cy],
        [1, 0, cy - cx],
        [0, 0, 1]
    ], dtype=float)
    return _transform_mask(mask, size, M)


def shear_x_mask(mask, size, shx):
    M = np.array([[1,shx,0],[0,1,0],[0,0,1]], dtype=float)
    return _transform_mask(mask, size, M)


def shear_y_mask(mask, size, shy):
    M = np.array([[1,0,0],[shy,1,0],[0,0,1]], dtype=float)
    return _transform_mask(mask, size, M)

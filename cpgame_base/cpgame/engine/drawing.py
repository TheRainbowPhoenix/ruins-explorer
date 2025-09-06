# cpgame/engine/drawing.py
# Contains advanced drawing helper functions for the engine.

import gint
from cpgame.engine.geometry import Rect

def draw_nineslice(
    x: int, y: int, width: int, height: int,
    source_image: gint.image,
    source_rect: Rect,
    top_border: int, right_border: int, bottom_border: int, left_border: int
):
    """
    Draws a scalable panel using the NineSlice technique.

    The source image is treated as a 3x3 grid defined by the source_rect and border sizes.
    Corners are drawn once, edges are tiled, and the center is tiled.

    :param x: Destination top-left X coordinate.
    :param y: Destination top-left Y coordinate.
    :param width: Destination width.
    :param height: Destination height.
    :param source_image: The gint.image object containing the UI texture.
    :param source_rect: The Rect defining the total area of the 9 slices in the source image.
    :param top_border: Height of the top border slice.
    :param right_border: Width of the right border slice.
    :param bottom_border: Height of the bottom border slice.
    :param left_border: Width of the left border slice.
    """
    # Calculate Source Slice Dimensions and Positions
    src_x1 = source_rect.x
    src_y1 = source_rect.y
    
    src_center_w = source_rect.width - left_border - right_border
    src_center_h = source_rect.height - top_border - bottom_border

    src_x2 = src_x1 + left_border
    src_y2 = src_y1 + top_border
    src_x3 = src_x2 + src_center_w
    src_y3 = src_y2 + src_center_h

    # Calculate Destination Slice Positions
    dest_x1 = x
    dest_y1 = y
    dest_x2 = x + left_border
    dest_y2 = y + top_border
    dest_x3 = x + width - right_border
    dest_y3 = y + height - bottom_border
    
    dest_center_w = width - left_border - right_border
    dest_center_h = height - top_border - bottom_border

    # Draw 9 Slices

    # Corners (no tiling)
    gint.dsubimage(dest_x1, dest_y1, source_image, src_x1, src_y1, left_border, top_border)
    gint.dsubimage(dest_x3, dest_y1, source_image, src_x3, src_y1, right_border, top_border)
    gint.dsubimage(dest_x1, dest_y3, source_image, src_x1, src_y3, left_border, bottom_border)
    gint.dsubimage(dest_x3, dest_y3, source_image, src_x3, src_y3, right_border, bottom_border)

    # Edges (tiling)
    # Top & Bottom Edges
    curr_x = dest_x2
    while curr_x < dest_x3:
        tile_w = min(src_center_w, dest_x3 - curr_x)
        if tile_w > 0:
            gint.dsubimage(curr_x, dest_y1, source_image, src_x2, src_y1, tile_w, top_border)
            gint.dsubimage(curr_x, dest_y3, source_image, src_x2, src_y3, tile_w, bottom_border)
        curr_x += src_center_w

    # Left & Right Edges
    curr_y = dest_y2
    while curr_y < dest_y3:
        tile_h = min(src_center_h, dest_y3 - curr_y)
        if tile_h > 0:
            gint.dsubimage(dest_x1, curr_y, source_image, src_x1, src_y2, left_border, tile_h)
            gint.dsubimage(dest_x3, curr_y, source_image, src_x3, src_y2, right_border, tile_h)
        curr_y += src_center_h

    # Center (2D tiling)
    curr_y = dest_y2
    while curr_y < dest_y3:
        tile_h = min(src_center_h, dest_y3 - curr_y)
        curr_x = dest_x2
        while curr_x < dest_x3:
            tile_w = min(src_center_w, dest_x3 - curr_x)
            if tile_w > 0 and tile_h > 0:
                gint.dsubimage(curr_x, curr_y, source_image, src_x2, src_y2, tile_w, tile_h)
            curr_x += src_center_w
        curr_y += src_center_h
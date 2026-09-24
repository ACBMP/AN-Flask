def compute_affine_from_corners(world_tl, world_br, pixel_tl, pixel_br):
    x_tl, y_tl = world_tl
    x_br, y_br = world_br
    u_tl, v_tl = pixel_tl
    u_br, v_br = pixel_br

    # straightforward scales
    sx = (u_br - u_tl) / (x_br - x_tl)
    sy = (v_br - v_tl) / (y_br - y_tl)  # note: y_br - y_tl, not flipped

    ox = u_tl - sx * x_tl
    oy = v_tl - sy * y_tl

    return sx, ox, sy, oy

def world_to_pixel(x, y, sx, ox, sy, oy):
    u = sx * x + ox
    v = sy * y + oy
    return u, v


pixel_corners = {
        #"siena": ((9, 8),
        #    (610.5, 386.75)),
        "siena": ((8, 7),
            (610, 386.25)),
        "castel gandolfo": ((2, 9), (621, 531)),
        "florence": ((76, 57), (603, 507)),
        "san donato": ((88, 62), (624, 599)),
        "forli": ((4, 18), (653, 621)),
        "venice": ((28, 45), (445, 655)),
        "rome": ((32.5, 8.5), (493, 530)),
        "monteriggioni": ((41, 130), (573, 567)),
        }

world_corners = {
        #"siena": ((-54, 48),
        #          (58, -25)),
        "siena": ((-55, 46),
                  (58, -25)),
        "castel gandolfo": ((-51, 41),
                  (51, -45)),
        "florence": ((-51, 44),
                     (51, -43)),
        "san donato": ((-50.5, 55),
                     (55.5, -52)),
        "forli": ((-56.6, 58.5),
                     (56.6, -49.5)),
        "venice": ((5.1, 27.9),
                     (84, -92)),
        "rome": ((-62, 66),
                     (52, -62.3)),
        "monteriggioni": ((-66.5, 66.5),
                          (66.5, -42.5)),
        }

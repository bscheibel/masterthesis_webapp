""" from dxf2svg.pycore import extract_all, save_svg_from_dxf


def convert(dxffilepath):
    save_svg_from_dxf(dxffilepath, svgfilepath=None, frame_name=None, size=300)

    extract_all(dxffilepath, size=300)

convert("GV_12.DXF") """

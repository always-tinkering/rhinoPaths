import os
from PIL import Image, ImageDraw, ImageFont

# Define a palette
CLR_TRANS = (255, 255, 255, 0)
CLR_BOUND = (100, 100, 100, 255) # Dark Grey
CLR_PATH = (0, 120, 215, 255)    # Windows Blue
CLR_ACCENT = (220, 50, 40, 255)  # Red for tool/tabs
CLR_STOCK = (200, 200, 200, 255) # Light Grey
CLR_STOCK_EDGE = (150, 150, 150, 255) # Mid Grey

def create_base():
    return Image.new('RGBA', (24, 24), CLR_TRANS)

def draw_rpPocket():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Outer boundary
    d.rectangle([2, 2, 21, 21], outline=CLR_BOUND, width=1)
    # Inner pocket toolpaths (hatching or solid with offset)
    d.rectangle([5, 5, 18, 18], fill=CLR_PATH)
    d.rectangle([8, 8, 15, 15], fill=(0, 90, 180, 255))
    return img

def draw_rpProfile():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Outer boundary
    d.rectangle([2, 2, 21, 21], outline=CLR_BOUND, width=1)
    # Inner profile path
    d.rectangle([5, 5, 18, 18], outline=CLR_PATH, width=2)
    return img

def draw_rpDrill():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Outer bound
    d.rectangle([2, 2, 21, 21], outline=CLR_BOUND, width=1)
    # Drill holes
    centers = [(7, 7), (16, 7), (7, 16), (16, 16)]
    for cx, cy in centers:
        d.ellipse([cx-2, cy-2, cx+2, cy+2], fill=CLR_PATH)
        d.ellipse([cx-1, cy-1, cx+1, cy+1], fill=(255,255,255,255))
    return img

def draw_rpEngrave():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Outline
    d.rectangle([2, 2, 21, 21], outline=CLR_BOUND, width=1)
    # Letter 'V'
    d.line([6, 6, 12, 18], fill=CLR_PATH, width=2)
    d.line([12, 18, 18, 6], fill=CLR_PATH, width=2)
    return img

def draw_rpStock():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Isometric box simple
    # Top face
    d.polygon([(12, 4), (20, 8), (12, 12), (4, 8)], fill=CLR_STOCK, outline=CLR_STOCK_EDGE)
    # Left face
    d.polygon([(4, 8), (12, 12), (12, 20), (4, 16)], fill=(180, 180, 180, 255), outline=CLR_STOCK_EDGE)
    # Right face
    d.polygon([(12, 12), (20, 8), (20, 16), (12, 20)], fill=(160, 160, 160, 255), outline=CLR_STOCK_EDGE)
    return img

def draw_rpTool():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Endmill shape
    # Shank
    d.rectangle([9, 2, 14, 12], fill=CLR_STOCK, outline=CLR_STOCK_EDGE)
    # Flutes
    d.rectangle([9, 12, 14, 20], fill=CLR_PATH, outline=CLR_PATH)
    d.line([9, 14, 14, 16], fill=(0, 90, 180, 255), width=1)
    d.line([9, 16, 14, 18], fill=(0, 90, 180, 255), width=1)
    d.line([9, 18, 14, 20], fill=(0, 90, 180, 255), width=1)
    return img

def draw_rpSetup():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Coordinate Axes
    origin = (6, 18)
    # X Axis (Red)
    d.line([origin[0], origin[1], origin[0]+12, origin[1]], fill=(220, 50, 40, 255), width=2)
    # Y Axis (Green)
    d.line([origin[0], origin[1], origin[0], origin[1]-12], fill=(40, 200, 50, 255), width=2)
    # Z Axis (Blue perspective)
    d.line([origin[0], origin[1], origin[0]-4, origin[1]+4], fill=(40, 100, 220, 255), width=2)
    # Origin dot
    d.ellipse([origin[0]-1, origin[1]-1, origin[0]+1, origin[1]+1], fill=(0,0,0,255))
    return img

def draw_rpTabs():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Outer boundary
    d.rectangle([2, 4, 21, 19], outline=CLR_BOUND, width=1)
    # Inner profile path with tabs
    # Top
    d.line([5, 7, 10, 7], fill=CLR_PATH, width=2)
    d.rectangle([11, 5, 13, 9], fill=CLR_ACCENT) # Tab
    d.line([14, 7, 18, 7], fill=CLR_PATH, width=2)
    
    # Bottom
    d.line([5, 16, 10, 16], fill=CLR_PATH, width=2)
    d.rectangle([11, 14, 13, 18], fill=CLR_ACCENT) # Tab
    d.line([14, 16, 18, 16], fill=CLR_PATH, width=2)
    
    # Left and Right connecting lines
    d.line([5, 7, 5, 16], fill=CLR_PATH, width=2)
    d.line([18, 7, 18, 16], fill=CLR_PATH, width=2)
    return img

def draw_rpPostProcessor():
    img = create_base()
    d = ImageDraw.Draw(img)
    # Document icon
    d.polygon([(4, 2), (14, 2), (20, 8), (20, 22), (4, 22)], fill=CLR_STOCK, outline=CLR_STOCK_EDGE)
    # Fold
    d.polygon([(14, 2), (14, 8), (20, 8)], fill=CLR_STOCK_EDGE, outline=CLR_STOCK_EDGE)
    # Text lines
    d.line([7, 10, 17, 10], fill=CLR_PATH, width=1)
    d.line([7, 13, 15, 13], fill=CLR_PATH, width=1)
    d.line([7, 16, 17, 16], fill=CLR_PATH, width=1)
    d.line([7, 19, 13, 19], fill=CLR_ACCENT, width=1) # "M02" or End
    return img

def main():
    icons_dir = os.path.join(os.path.dirname(__file__), "..", "src", "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    generators = {
        "rhinoPaths_Pocket": draw_rpPocket,
        "rhinoPaths_Cutout": draw_rpProfile,
        "rhinoPaths_Drill": draw_rpDrill,
        "rhinoPaths_Engrave": draw_rpEngrave,
        "rhinoPaths_Dogbone": draw_rpStock,
        "rhinoPaths_Feedrate": draw_rpTool,
        "rhinoPaths_Pass_Depths": draw_rpSetup,
        "rhinoPaths_G-Code_Preview": draw_rpTabs,
        "rhinoPaths_PostProcessor": draw_rpPostProcessor
    }
    
    for name, gen_func in generators.items():
        img = gen_func()
        path = os.path.join(icons_dir, f"{name}.png")
        img.save(path)
        print(f"Generated {path}")

if __name__ == "__main__":
    main()

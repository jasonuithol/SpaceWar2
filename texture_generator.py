"""
Texture generator for SpaceWar2 spacecraft
Creates themed textures for each player color
"""
from PIL import Image, ImageDraw
import numpy as np
import os

# Create textures directory if it doesn't exist
os.makedirs('assets/textures', exist_ok=True)

def create_ice_texture(size=512):
    """Blue spacecraft - Ice shard texture"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Base ice blue colors
    colors = [
        (180, 220, 255, 255),  # Light ice blue
        (140, 200, 255, 255),  # Medium ice blue
        (100, 180, 240, 255),  # Darker ice blue
        (200, 235, 255, 255),  # Bright highlights
    ]
    
    # Create crystalline pattern
    np.random.seed(42)
    for _ in range(150):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        length = np.random.randint(10, 40)
        angle = np.random.uniform(0, 360)
        color = colors[np.random.randint(0, len(colors))]
        
        # Draw crystal fractures
        x2 = int(x + length * np.cos(np.radians(angle)))
        y2 = int(y + length * np.sin(np.radians(angle)))
        draw.line([(x, y), (x2, y2)], fill=color, width=2)
    
    # Add some ice crystals
    for _ in range(50):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        radius = np.random.randint(3, 8)
        draw.ellipse([x-radius, y-radius, x+radius, y+radius], 
                     fill=(220, 240, 255, 200))
    
    # Add overall ice tint
    overlay = Image.new('RGBA', (size, size), (150, 210, 255, 100))
    img = Image.alpha_composite(img, overlay)
    
    return img

def create_watermelon_texture(size=512):
    """Red spacecraft - Watermelon slice texture"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Red flesh gradient
    for y in range(size):
        intensity = 1.0 - (y / size) * 0.3  # Darker towards bottom
        red = int(255 * intensity)
        green = int(80 * intensity)
        draw.line([(0, y), (size, y)], fill=(red, green, 80, 255))
    
    # Add watermelon seeds
    np.random.seed(43)
    for _ in range(40):
        x = np.random.randint(size // 4, 3 * size // 4)
        y = np.random.randint(size // 4, 3 * size // 4)
        # Black seeds
        draw.ellipse([x-4, y-6, x+4, y+6], fill=(20, 20, 20, 255))
    
    # Green rind at edges
    rind_width = size // 8
    draw.rectangle([0, 0, rind_width, size], fill=(50, 150, 50, 255))
    draw.rectangle([size-rind_width, 0, size, size], fill=(50, 150, 50, 255))
    
    # White layer between rind and flesh
    white_width = rind_width // 3
    draw.rectangle([rind_width, 0, rind_width + white_width, size], 
                   fill=(240, 255, 240, 255))
    draw.rectangle([size-rind_width-white_width, 0, size-rind_width, size], 
                   fill=(240, 255, 240, 255))
    
    return img

def create_pyramid_texture(size=512):
    """Yellow spacecraft - Egyptian pyramid texture"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Sandy beige base
    base_color = (220, 200, 140)
    img.paste(base_color + (255,), [0, 0, size, size])
    
    # Add stone blocks
    block_height = size // 16
    block_width = size // 12
    
    for row in range(0, size, block_height):
        offset = (row // block_height) % 2 * (block_width // 2)
        for col in range(-block_width, size + block_width, block_width):
            x = col + offset
            # Draw block lines
            draw.rectangle([x, row, x + block_width - 2, row + block_height - 2],
                         outline=(180, 160, 100, 255), width=2)
            
            # Add weathering/shadows
            np.random.seed(abs(row * 1000 + col) % (2**32))
            if np.random.random() > 0.7:
                shadow_x = x + np.random.randint(5, block_width - 5)
                shadow_y = row + np.random.randint(5, block_height - 5)
                shadow_size = np.random.randint(3, 8)
                draw.ellipse([shadow_x, shadow_y, 
                            shadow_x + shadow_size, shadow_y + shadow_size],
                           fill=(180, 160, 100, 150))
    
    # Add hieroglyphic-like marks
    np.random.seed(44)
    for _ in range(15):
        x = np.random.randint(size // 6, 5 * size // 6)
        y = np.random.randint(size // 6, 5 * size // 6)
        w = np.random.randint(10, 30)
        h = np.random.randint(10, 30)
        draw.rectangle([x, y, x+w, y+h], outline=(140, 100, 40, 200), width=2)
    
    return img

def create_leaf_texture(size=512):
    """Green spacecraft - Leaf tip texture"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Green gradient - darker at base, lighter at tip
    for y in range(size):
        progress = y / size
        # Dark green to light green gradient
        r = int(40 + progress * 100)
        g = int(120 + progress * 100)
        b = int(40 + progress * 60)
        draw.line([(0, y), (size, y)], fill=(r, g, b, 255))
    
    # Draw central vein (midrib)
    midrib_color = (60, 90, 40, 255)
    draw.line([(size//2, 0), (size//2, size)], fill=midrib_color, width=6)
    
    # Draw side veins branching from center
    num_veins = 8
    for i in range(num_veins):
        y_pos = size * (i + 1) / (num_veins + 1)
        # Left side vein
        draw.line([(size//2, int(y_pos)), 
                   (size//4, int(y_pos + size//8))], 
                  fill=midrib_color, width=3)
        # Right side vein
        draw.line([(size//2, int(y_pos)), 
                   (3*size//4, int(y_pos + size//8))], 
                  fill=midrib_color, width=3)
        
        # Secondary veins
        for j in range(2):
            offset = (j + 1) * 20
            draw.line([(size//4, int(y_pos + size//8)), 
                      (size//4 - offset, int(y_pos + size//8 + offset))], 
                     fill=(70, 100, 50, 200), width=1)
            draw.line([(3*size//4, int(y_pos + size//8)), 
                      (3*size//4 + offset, int(y_pos + size//8 + offset))], 
                     fill=(70, 100, 50, 200), width=1)
    
    # Add stem at base
    stem_height = size // 10
    stem_width = size // 20
    draw.rectangle([size//2 - stem_width//2, size - stem_height,
                   size//2 + stem_width//2, size],
                  fill=(80, 60, 30, 255))
    
    # Add some texture variation (leaf surface)
    np.random.seed(45)
    for _ in range(100):
        x = np.random.randint(0, size)
        y = np.random.randint(0, size)
        intensity = np.random.randint(-20, 20)
        r = max(0, min(255, 40 + (y/size) * 100 + intensity))
        g = max(0, min(255, 120 + (y/size) * 100 + intensity))
        b = max(0, min(255, 40 + (y/size) * 60 + intensity))
        draw.point((x, y), fill=(int(r), int(g), int(b), 255))
    
    return img

def main():
    print("Generating spacecraft textures...")
    
    # Generate all textures
    textures = {
        'spacecraft_blue_ice.png': create_ice_texture(),
        'spacecraft_red_watermelon.png': create_watermelon_texture(),
        'spacecraft_yellow_pyramid.png': create_pyramid_texture(),
        'spacecraft_green_leaf.png': create_leaf_texture(),
    }
    
    # Save textures
    for filename, texture in textures.items():
        filepath = f'assets/textures/{filename}'
        texture.save(filepath)
        print(f"Created: {filepath}")
    
    print("✓ All textures generated successfully!")

if __name__ == '__main__':
    main()
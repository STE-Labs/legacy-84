import os
import glob
import re
from PIL import Image

# Max dimension for thumbnail
MAX_SIZE = (800, 800)

def create_thumbnail(img_path):
    dir_name = os.path.dirname(img_path)
    base_name = os.path.basename(img_path)
    name, ext = os.path.splitext(base_name)
    
    # Skip if it's already a thumbnail
    if name.endswith('.thumb'):
        return None
        
    thumb_name = f"{name}.thumb{ext}"
    thumb_path = os.path.join(dir_name, thumb_name)
    
    try:
        with Image.open(img_path) as img:
            # First, if user wanted to crop empty space/transparency, we can do it here
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                # Get the bounding box of non-transparent pixels
                # Convert to RGBA if not already
                rgba = img.convert("RGBA")
                bbox = rgba.getbbox()
                if bbox:
                    img = img.crop(bbox)
            
            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            img.save(thumb_path)
            print(f"Created thumbnail: {thumb_path}")
            return thumb_path
    except Exception as e:
        print(f"Failed to process {img_path}: {e}")
        return None

def update_markdown_files():
    md_files = glob.glob("**/*.md", recursive=True)
    
    for md_file in md_files:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Find all markdown images: ![alt](path)
        # We want to replace the image with a thumbnail that links to the original
        # Original: ![alt](path)
        # New: [![alt](path.thumb.ext)](path)
        
        # Regex to find ![alt](path)
        # We need to make sure we don't process ones that are already linked
        # Let's just find ![alt](path) that are NOT inside a link `[![alt](path)](link)`
        
        # A bit tricky to do with regex, let's do a simple replace first
        # Let's find all ![alt](path)
        matches = re.finditer(r'(?<!\[)!\[([^\]]*)\]\(([^)]+)\)', content)
        
        new_content = content
        replacements = {}
        for match in matches:
            full_match = match.group(0)
            alt_text = match.group(1)
            img_path = match.group(2)
            
            # Don't thumbnail external links
            if img_path.startswith('http'):
                continue
                
            # Get the path to the original image relative to the script
            md_dir = os.path.dirname(md_file)
            actual_img_path = os.path.normpath(os.path.join(md_dir, img_path))
            
            # If the image exists, we make a thumbnail
            if os.path.exists(actual_img_path):
                # Don't thumbnail thumbnails
                if '.thumb.' not in img_path:
                    create_thumbnail(actual_img_path)
                    
                    # Create the new markdown syntax
                    name, ext = os.path.splitext(img_path)
                    thumb_path = f"{name}.thumb{ext}"
                    
                    new_md = f"[![{alt_text}]({thumb_path})]({img_path})"
                    replacements[full_match] = new_md
        
        if replacements:
            for old, new in replacements.items():
                new_content = new_content.replace(old, new)
                
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {md_file}")

if __name__ == "__main__":
    update_markdown_files()

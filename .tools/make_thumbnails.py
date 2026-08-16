import os
import glob
import re
from PIL import Image

# Max dimension for thumbnail
MAX_SIZE = (800, 800)

def create_thumbnail(img_path):
    """Create a thumbnail for the given image. Returns the thumb path or None."""
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
            if img.mode in ('RGBA', 'LA') or (img.mode == 'P' and 'transparency' in img.info):
                rgba = img.convert("RGBA")
                bbox = rgba.getbbox()
                if bbox:
                    img = img.crop(bbox)

            img.thumbnail(MAX_SIZE, Image.Resampling.LANCZOS)
            img.save(thumb_path)
            print(f"  Created thumbnail: {thumb_path}")
            return thumb_path
    except Exception as e:
        print(f"  Failed to process {img_path}: {e}")
        return None


def update_markdown_files():
    """Scan all README.md files and ensure images use thumbnail+link pattern."""
    md_files = glob.glob("**/*.md", recursive=True)

    for md_file in md_files:
        # Skip LICENSE
        if os.path.basename(md_file).upper() == 'LICENSE.MD':
            continue

        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = content
        md_dir = os.path.dirname(md_file)

        # Pattern 1: Already linked images [![alt](thumb)](original)
        # Update thumb path if thumbnail doesn't exist but original does
        linked_pattern = re.compile(
            r'\[!\[([^\]]*)\]\(([^)]+)\)\]\(([^)]+)\)'
        )
        for match in linked_pattern.finditer(content):
            full_match = match.group(0)
            alt_text = match.group(1)
            thumb_ref = match.group(2)
            original_ref = match.group(3)

            if original_ref.startswith('http'):
                continue

            actual_original = os.path.normpath(os.path.join(md_dir, original_ref))

            if os.path.exists(actual_original) and '.thumb.' not in os.path.basename(actual_original):
                # Ensure thumbnail exists
                name, ext = os.path.splitext(original_ref)
                expected_thumb_ref = f"{name}.thumb{ext}"
                actual_thumb = os.path.normpath(os.path.join(md_dir, expected_thumb_ref))

                if not os.path.exists(actual_thumb):
                    create_thumbnail(actual_original)

                # Update the markdown if the thumb ref is wrong
                if thumb_ref != expected_thumb_ref:
                    new_md = f"[![{alt_text}]({expected_thumb_ref})]({original_ref})"
                    new_content = new_content.replace(full_match, new_md)

        # Pattern 2: Standalone images ![alt](path) NOT inside a link
        standalone_pattern = re.compile(
            r'(?<!\[)!\[([^\]]*)\]\(([^)]+)\)'
        )
        for match in standalone_pattern.finditer(new_content):
            full_match = match.group(0)
            alt_text = match.group(1)
            img_path = match.group(2)

            if img_path.startswith('http'):
                continue

            # Skip if already a thumb reference
            if '.thumb.' in img_path:
                continue

            actual_img = os.path.normpath(os.path.join(md_dir, img_path))

            if os.path.exists(actual_img):
                # Create thumbnail
                create_thumbnail(actual_img)

                name, ext = os.path.splitext(img_path)
                thumb_path = f"{name}.thumb{ext}"

                new_md = f"[![{alt_text}]({thumb_path})]({img_path})"
                new_content = new_content.replace(full_match, new_md)

        if new_content != content:
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated: {md_file}")
        else:
            print(f"No changes: {md_file}")


if __name__ == "__main__":
    update_markdown_files()

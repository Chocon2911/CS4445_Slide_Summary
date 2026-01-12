import os
import re
import subprocess
import tempfile
import shutil
from pathlib import Path

# Paths
PANDOC = r"C:\Users\Admin\AppData\Local\Pandoc\pandoc.exe"
MMDC = r"C:\Users\Admin\AppData\Roaming\npm\mmdc.cmd"
SLIDE_DIR = Path(r"C:\Users\Admin\OneDrive - Hanoi University of Science and Technology\New folder\year 4-1\CS4420\Slide")

def extract_and_replace_mermaid(md_content, temp_dir, base_name):
    """Extract mermaid blocks and replace with image references"""
    pattern = r'```mermaid\n(.*?)```'
    matches = list(re.finditer(pattern, md_content, re.DOTALL))

    if not matches:
        return md_content, []

    image_files = []
    new_content = md_content

    for i, match in enumerate(reversed(matches)):  # Reverse to maintain positions
        mermaid_code = match.group(1)
        img_name = f"{base_name}_mermaid_{len(matches) - 1 - i}.png"
        img_path = temp_dir / img_name

        # Write mermaid code to temp file
        mmd_file = temp_dir / f"temp_{i}.mmd"
        with open(mmd_file, 'w', encoding='utf-8') as f:
            f.write(mermaid_code)

        # Convert to PNG
        try:
            subprocess.run([
                MMDC,
                "-i", str(mmd_file),
                "-o", str(img_path),
                "-b", "white",
                "-s", "2"
            ], check=True, capture_output=True)

            # Replace mermaid block with image reference
            img_md = f"![Diagram]({img_path})"
            new_content = new_content[:match.start()] + img_md + new_content[match.end():]
            image_files.append(img_path)
            print(f"  Generated: {img_name}")
        except subprocess.CalledProcessError as e:
            print(f"  Warning: Failed to generate {img_name}: {e}")
            # Keep original mermaid block as code

    return new_content, image_files

def convert_md_to_docx(md_file):
    """Convert a markdown file to docx with mermaid diagrams"""
    md_path = Path(md_file)
    docx_path = md_path.with_suffix('.docx')
    base_name = md_path.stem

    print(f"\nProcessing: {md_path.name}")

    # Read markdown content
    with open(md_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Create temp directory for images
    temp_dir = Path(tempfile.mkdtemp())

    try:
        # Process mermaid blocks
        processed_content, image_files = extract_and_replace_mermaid(content, temp_dir, base_name)

        # Write processed markdown
        temp_md = temp_dir / f"{base_name}_processed.md"
        with open(temp_md, 'w', encoding='utf-8') as f:
            f.write(processed_content)

        # Convert to DOCX using pandoc
        subprocess.run([
            PANDOC,
            str(temp_md),
            "-o", str(docx_path),
            "--resource-path", str(temp_dir)
        ], check=True)

        print(f"  Created: {docx_path.name}")

    finally:
        # Cleanup temp directory
        shutil.rmtree(temp_dir, ignore_errors=True)

def main():
    print("Converting Markdown files to DOCX with Mermaid diagrams...")
    print("=" * 60)

    # Find all markdown files
    md_files = sorted(SLIDE_DIR.glob("Chapter*_Summary.md"))

    for md_file in md_files:
        convert_md_to_docx(md_file)

    print("\n" + "=" * 60)
    print("Done! All files converted.")

if __name__ == "__main__":
    main()

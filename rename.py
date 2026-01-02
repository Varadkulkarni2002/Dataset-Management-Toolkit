#!/usr/bin/env python3
"""
Image Renamer Script
Renames image files in a directory with sequential numbering starting from a specified number.
"""

import os
import argparse
from pathlib import Path

def rename_images(directory, start_number, prefix="image", dry_run=False):
    """
    Rename image files in the specified directory with sequential numbering.
    
    Args:
        directory (str): Path to the directory containing images
        start_number (int): Starting number for the sequence
        prefix (str): Prefix for the new filenames
        dry_run (bool): If True, only show what would be renamed without actually doing it
    """
    
    # Supported image extensions
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp', '.svg'}
    
    # Get all files in the directory
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
    except FileNotFoundError:
        print(f"Error: Directory '{directory}' not found.")
        return
    except PermissionError:
        print(f"Error: Permission denied to access directory '{directory}'.")
        return
    
    # Filter for image files
    image_files = []
    for file in files:
        file_ext = Path(file).suffix.lower()
        if file_ext in image_extensions:
            image_files.append(file)
    
    if not image_files:
        print("No image files found in the directory.")
        return
    
    # Sort files alphabetically for consistent ordering
    image_files.sort()
    
    print(f"Found {len(image_files)} image file(s) in '{directory}'")
    
    # Calculate padding for consistent numbering
    total_files = len(image_files)
    max_number = start_number + total_files - 1
    padding = len(str(max_number))
    
    renamed_count = 0
    
    for i, old_filename in enumerate(image_files):
        # Generate new filename
        number = start_number + i
        new_number = str(number).zfill(padding)
        file_ext = Path(old_filename).suffix
        new_filename = f"{prefix}_{new_number}{file_ext}"
        
        old_path = os.path.join(directory, old_filename)
        new_path = os.path.join(directory, new_filename)
        
        # Check if new filename already exists (and it's not the same file)
        if os.path.exists(new_path) and old_path != new_path:
            print(f"Warning: '{new_filename}' already exists. Skipping '{old_filename}'")
            continue
        
        if dry_run:
            print(f"Would rename: '{old_filename}' -> '{new_filename}'")
        else:
            try:
                os.rename(old_path, new_path)
                print(f"Renamed: '{old_filename}' -> '{new_filename}'")
                renamed_count += 1
            except OSError as e:
                print(f"Error renaming '{old_filename}': {e}")
    
    if dry_run:
        print(f"\nDry run complete. Would rename {renamed_count} file(s).")
    else:
        print(f"\nRenaming complete. Successfully renamed {renamed_count} file(s).")

def main():
    parser = argparse.ArgumentParser(
        description="Rename image files with sequential numbering starting from a specified number.",
        epilog="Example: python rename_images.py /path/to/images --start 100 --prefix vacation"
    )
    
    parser.add_argument(
        "directory",
        help="Directory containing the images to rename"
    )
    
    parser.add_argument(
        "--start", "-s",
        type=int,
        default=1,
        help="Starting number for the sequence (default: 1)"
    )
    
    parser.add_argument(
        "--prefix", "-p",
        default="image",
        help="Prefix for the new filenames (default: 'image')"
    )
    
    parser.add_argument(
        "--dry-run", "-d",
        action="store_true",
        help="Show what would be renamed without actually doing it"
    )
    
    parser.add_argument(
        "--extensions", "-e",
        nargs="+",
        default=[".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp"],
        help="Additional file extensions to consider as images"
    )
    
    args = parser.parse_args()
    
    # Verify the start number is valid
    if args.start < 0:
        print("Error: Start number must be non-negative.")
        return
    
    print(f"Starting image renaming process...")
    print(f"Directory: {args.directory}")
    print(f"Start number: {args.start}")
    print(f"Prefix: {args.prefix}")
    print(f"Dry run: {args.dry_run}")
    print("-" * 50)
    
    rename_images(args.directory, args.start, args.prefix, args.dry_run)

if __name__ == "__main__":
    main()

   

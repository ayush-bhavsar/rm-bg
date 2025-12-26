from rembg import remove
from PIL import Image
import io
import os
import sys
import logging
from pathlib import Path
from datetime import datetime
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def remove_background(input_path, output_path=None, quality=95, preserve_format=False):
    """
    Remove background from a single image with enhanced features.
    Saves all output images to a single 'nobdg-images' folder with '_nobgd' suffix.

    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output. Default: input_path_nobgd.png
        quality (int): Output quality (1-100)
        preserve_format (bool): Keep original format instead of PNG

    Returns:
        dict: Result info with success status, paths, and metadata
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return {"success": False, "error": "Input file not found"}

        # Create single output folder
        output_folder = "nobdg-images"
        os.makedirs(output_folder, exist_ok=True)

        # Set default output path with _nobgd suffix
        if output_path is None:
            image_name = Path(input_path).stem
            output_filename = f"{image_name}_nobgd.png"
            output_path = os.path.join(output_folder, output_filename)
        else:
            # If custom output path provided, ensure it's in the nobdg-images folder
            output_path = os.path.join(output_folder, Path(output_path).name)

        logger.info(f"Processing: {input_path}")

        # Get image metadata
        input_image = Image.open(input_path)
        image_size = input_image.size
        logger.info(f"Image loaded: {image_size}")

        # Remove background
        output_image = remove(input_image)

        # Save with appropriate settings
        if preserve_format and input_path.lower().endswith(('.jpg', '.jpeg')):
            # Convert RGBA to RGB for JPG
            rgb_image = Image.new('RGB', output_image.size, (255, 255, 255))
            rgb_image.paste(output_image, mask=output_image.split()[3])
            rgb_image.save(output_path, quality=quality)
        else:
            output_image.save(output_path, quality=quality)

        logger.info(f"✓ Saved to: {output_path}")

        # Save metadata
        metadata = {
            "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
            "input_file": input_path,
            "output_file": output_path,
            "output_folder": output_folder,
            "image_size": image_size,
            "output_quality": quality,
            "preserve_format": preserve_format,
            "success": True
        }

        metadata_path = os.path.join(output_folder, "processing_log.json")
        # Load existing log if it exists
        if os.path.exists(metadata_path):
            with open(metadata_path, 'r') as f:
                existing_log = json.load(f)
            if "processed_images" not in existing_log:
                existing_log["processed_images"] = []
            existing_log["processed_images"].append(metadata)
            existing_log["last_updated"] = metadata["timestamp"]
        else:
            existing_log = {
                "output_folder": output_folder,
                "created": metadata["timestamp"],
                "last_updated": metadata["timestamp"],
                "processed_images": [metadata]
            }

        with open(metadata_path, 'w') as f:
            json.dump(existing_log, f, indent=2)
        logger.info(f"Processing log updated: {metadata_path}")

        return metadata

    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    # Define input path (output will be automatically named with _nobgd suffix)
    input_path = 'new.png'

    result = remove_background(input_path)

    if result.get("success"):
        print(f"\n✓ Background removed successfully!")
        print(f"Output folder: {result['output_folder']}")
        print(f"Output: {result['output_file']}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to process image: {result.get('error')}")
        sys.exit(1)
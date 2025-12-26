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
    Creates a timestamped folder for each run with results and metadata.
    
    Args:
        input_path (str): Path to input image
        output_path (str): Path to save output. Default: input_path_no_bg.png
        quality (int): Output quality (1-100)
        preserve_format (bool): Keep original format instead of PNG
    
    Returns:
        dict: Result info with success status, paths, and metadata
    """
    try:
        # Validate input file
        if not os.path.exists(input_path):
            logger.error(f"Input file not found: {input_path}")
            return {"success": False, "error": "Input file not found", "run_folder": None}
        
        # Create timestamped output folder in root
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        image_name = Path(input_path).stem
        run_folder = f"{image_name}_{timestamp}"
        os.makedirs(run_folder, exist_ok=True)
        logger.info(f"Created run folder: {run_folder}")
        
        # Set default output path in the run folder
        if output_path is None:
            output_filename = f"{image_name}_no_bg.png"
            output_path = os.path.join(run_folder, output_filename)
        else:
            output_path = os.path.join(run_folder, Path(output_path).name)
        
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
            "timestamp": timestamp,
            "input_file": input_path,
            "output_file": output_path,
            "run_folder": run_folder,
            "image_size": image_size,
            "output_quality": quality,
            "preserve_format": preserve_format,
            "success": True
        }
        
        metadata_path = os.path.join(run_folder, "metadata.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        logger.info(f"Metadata saved to: {metadata_path}")
        
        return metadata
        
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        return {"success": False, "error": str(e), "run_folder": None}


if __name__ == "__main__":
    # Define input and output paths
    input_path = 'new.png'
    output_path = 'new2.png'
    
    result = remove_background(input_path, output_path)
    
    if result.get("success"):
        print(f"\n✓ Background removed successfully!")
        print(f"Run folder: {result['run_folder']}")
        print(f"Output: {result['output_file']}")
        sys.exit(0)
    else:
        print(f"\n✗ Failed to process image: {result.get('error')}")
        sys.exit(1)
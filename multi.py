import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from rembg import remove
from PIL import Image
from tqdm import tqdm
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SUPPORTED_FORMATS = ('.png', '.jpg', '.jpeg', '.bmp', '.webp')


def process_batch(input_folder, preserve_format=False, quality=95):
    """
    Batch process images to remove backgrounds with progress tracking.
    Saves all output images to a single 'nobdg-images' folder with '_nobgd' suffix.

    Args:
        input_folder (str): Folder containing input images
        preserve_format (bool): Keep original format instead of PNG
        quality (int): Output quality (1-100)

    Returns:
        dict: Result info with counts, paths, and metadata
    """
    # Validate input folder
    if not os.path.exists(input_folder):
        logger.error(f"Input folder not found: {input_folder}")
        return {"success": False, "error": "Input folder not found"}

    # Create single output folder
    output_folder = "nobdg-images"
    os.makedirs(output_folder, exist_ok=True)
    logger.info(f"Using output folder: {output_folder}")

    # Get list of image files
    image_files = [f for f in os.listdir(input_folder)
                   if f.lower().endswith(SUPPORTED_FORMATS)]

    if not image_files:
        logger.warning(f"No image files found in {input_folder}")
        return {"success": False, "error": "No image files found", "output_folder": output_folder, "processed": 0, "failed": 0}

    successful = 0
    failed = 0
    processed_files = []
    failed_files = []

    logger.info(f"Found {len(image_files)} images to process")

    # Process with progress bar
    for filename in tqdm(image_files, desc="Processing images", unit="img"):
        try:
            input_path = os.path.join(input_folder, filename)

            # Open and process image
            img = Image.open(input_path)
            result = remove(img)

            # Create output filename with _nobgd suffix
            image_name = Path(filename).stem
            if preserve_format and filename.lower().endswith(('.jpg', '.jpeg')):
                output_name = f"{image_name}_nobgd.jpg"
                # Convert RGBA to RGB for JPG
                rgb_image = Image.new('RGB', result.size, (255, 255, 255))
                rgb_image.paste(result, mask=result.split()[3])
                output_path = os.path.join(output_folder, output_name)
                rgb_image.save(output_path, quality=quality)
            else:
                output_name = f"{image_name}_nobgd.png"
                output_path = os.path.join(output_folder, output_name)
                result.save(output_path)

            successful += 1
            processed_files.append({"input": filename, "output": output_name})
            logger.debug(f"✓ Processed: {filename} -> {output_name}")

        except Exception as e:
            failed += 1
            failed_files.append({"file": filename, "error": str(e)})
            logger.error(f"✗ Failed to process {filename}: {str(e)}")

    # Save batch metadata
    metadata = {
        "timestamp": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "output_folder": output_folder,
        "input_folder": input_folder,
        "total_processed": successful,
        "total_failed": failed,
        "total_images": len(image_files),
        "preserve_format": preserve_format,
        "output_quality": quality,
        "processed_files": processed_files,
        "failed_files": failed_files,
        "success": failed == 0
    }

    metadata_path = os.path.join(output_folder, "batch_processing_log.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    logger.info(f"Batch processing log saved to: {metadata_path}")

    return metadata


if __name__ == "__main__":
    input_folder = 'images_input'

    logger.info(f"Starting batch processing...")
    result = process_batch(input_folder)

    print(f"\n{'='*50}")
    print(f"Batch Processing Complete!")
    print(f"Output folder: {result.get('output_folder')}")
    print(f"✓ Successful: {result.get('total_processed', 0)}")
    print(f"✗ Failed: {result.get('total_failed', 0)}")
    print(f"{'='*50}")

    sys.exit(0 if result.get('success') else 1)
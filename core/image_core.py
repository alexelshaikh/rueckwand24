from pathlib import Path
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from fastapi import HTTPException

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_IMAGE_PATH = BASE_DIR / "resources" / "images" / "calm_kitchen.jpg"
PDF_OUTPUT_DIR = BASE_DIR / "resources" / "cropped_images"


def generate_item_pdf(cropped_width: int, cropped_height: int, item_id: int) -> str:
    if cropped_width <= 0 or cropped_height <= 0:
        raise HTTPException(status_code=400, detail=f"Invalid width or height values: {cropped_width}x{cropped_height}")
    if not SOURCE_IMAGE_PATH.exists():
        raise HTTPException(status_code=400, detail=f"Source image not found at {SOURCE_IMAGE_PATH}")

    with Image.open(SOURCE_IMAGE_PATH) as img:
        img_width, img_height = img.size

        if cropped_width > img_width or cropped_height > img_height:
            raise HTTPException(status_code=400, detail=f"Requested crop {cropped_width}x{cropped_height} exceeds source image size {img_width}x{img_height}")

        box = (0, 0, cropped_width, cropped_height)
        cropped = img.crop(box)

        draw = ImageDraw.Draw(cropped)
        timestamp = datetime.now().strftime("%d.%m.%Y @ %H:%M:%S")

        margin_from_image = 2
        inner_padding = 2
        font = ImageFont.load_default()

        bbox = draw.textbbox((0, 0), timestamp, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]

        needed_width = margin_from_image + text_w + 2 * inner_padding
        needed_height = text_h + 2 * inner_padding + margin_from_image

        if cropped_width < needed_width or cropped_height < needed_height:
            raise HTTPException(status_code=400, detail=f"Cropped size {cropped_width}x{cropped_height} too small for timestamp box! Need at least {needed_width}x{needed_height}")


        rect_x0 = margin_from_image
        rect_x1 = rect_x0 + text_w + 2 * inner_padding

        rect_y1 = cropped.height - margin_from_image
        rect_y0 = rect_y1 - text_h - 2 * inner_padding

        draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill="white")

        text_x = rect_x0 + inner_padding
        text_y = rect_y0 + inner_padding

        draw.text(
            (text_x, text_y),
            timestamp,
            fill="black",
            font=font,
        )

        PDF_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

        filename = f"item_{item_id}.pdf"
        pdf_full_path = PDF_OUTPUT_DIR / filename

        cropped.save(pdf_full_path, "PDF")

        return pdf_full_path.relative_to(BASE_DIR).as_posix()

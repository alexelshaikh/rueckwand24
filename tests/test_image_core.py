import pytest
from PIL import Image
from fastapi import HTTPException

from core.image_core import generate_item_pdf, BASE_DIR, PDF_OUTPUT_DIR, SOURCE_IMAGE_PATH


def test_generate_item_pdf_creates_file():
    width, height = 300, 200
    item_id = -1

    pdf_rel_path = generate_item_pdf(width, height, item_id)
    pdf_full_path = BASE_DIR / pdf_rel_path

    assert pdf_full_path.exists()
    assert pdf_full_path.suffix.lower() == ".pdf"
    assert pdf_full_path.parent == PDF_OUTPUT_DIR


def test_generate_item_pdf_rejects_non_positive_size():
    with pytest.raises(HTTPException):
        generate_item_pdf(0, 100, 1)
    with pytest.raises(HTTPException):
        generate_item_pdf(100, -5, 2)


def test_generate_item_pdf_rejects_too_large_size():
    with Image.open(SOURCE_IMAGE_PATH) as img:
        img_w, img_h = img.size

    with pytest.raises(HTTPException):
        generate_item_pdf(img_w + 1, img_h, 3)

    with pytest.raises(HTTPException):
        generate_item_pdf(img_w, img_h + 1, 4)

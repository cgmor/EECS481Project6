#!/usr/bin/env python3
import os
import re
import sys
import requests
from io import BytesIO
from PIL import Image

# ─── CONFIG ────────────────────────────────────────────────────────────────────

API_KEY    = "Sorry_481_staff_:("       
API_ROOT   = "https://api.projectpq.ai"        
OUTPUT_DIR = "patent_images"        

# ─── HELPERS ───────────────────────────────────────────────────────────────────

def pad_publication_number(pn: str) -> str:
    """
    Turn US7654321B2 → "07654321"
    """
    # strip "US" and other stuff
    m = re.match(r"^US(?:RE)?0*(\d+)(?:[AB]\d?)?$", pn, re.IGNORECASE)
    if not m:
        raise ValueError(f"Can't parse patent number {pn!r}")
    return m.group(1).zfill(8)

def list_drawings(pn: str, token: str) -> list[str]:
    """Hit /patents/{pn}/drawings to get a list of drawing indexes."""
    url = f"{API_ROOT}/patents/{pn}/drawings"
    resp = requests.get(url, params={"token": token}, timeout=30.0)
    resp.raise_for_status()
    data = resp.json()
    return data.get("drawings", [])

def download_and_convert(pn: str, idx: str, padded: str, token: str):
    """
    Download one drawing (JPEG) and convert/save it as TIFF
    named '{padded}-{idx}.tif' under OUTPUT_DIR.
    """
    draw_url = f"{API_ROOT}/patents/{pn}/drawings/{idx}"
    resp = requests.get(draw_url, params={"token": token}, timeout=30.0)
    resp.raise_for_status()

    #load into PIL
    img = Image.open(BytesIO(resp.content)).convert("RGB")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    out_name = f"{padded}-{idx}.tif"
    out_path = os.path.join(OUTPUT_DIR, out_name)

    #save as TIFF
    img.save(out_path, format="TIFF")
    print(f"✓ Saved {out_path}")
    return out_path

# MAIN

def main(patent_numbers: list[str]):

    for pn in patent_numbers:
        print(f"\nProcessing {pn} …")
        try:
            padded = pad_publication_number(pn)
        except ValueError as e:
            print("✗", e)
            continue

        #get all drawing indexes
        try:
            indexes = list_drawings(pn, API_KEY)
        except Exception as e:
            print(f"✗ Failed to list drawings for {pn}: {e}")
            continue

        if not indexes:
            print(f"⚠ No drawings found for {pn}")
            continue

        print(f" → Found pages: {indexes}")

        #download + convert each
        for idx in indexes:
            try:
                download_and_convert(pn, idx, padded, API_KEY)
            except Exception as e:
                print(f"✗ Error on page {idx}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        
        sys.exit(1)
    nums = ['US7654321B2',
     'US10734122B2',
     'US10283223B2']
    main(nums)
---
name: image-resize
description: Resizes, crops and converts images between PNG, JPEG and WebP while keeping the aspect ratio, reads the size and format first, picks the Lanczos filter, saves at quality 85, strips location data, never upscales unless asked, reports the old and new size in pixels and kilobytes, and handles folders of photos in one pass with a summary table at the end for every file it changed or skipped. Use when the user wants to resize an image, shrink image files, or make smaller versions of photos.
license: MIT
---

# Image resize

Resize and convert images with Pillow.

## Steps

1. Read the image size and format.
2. Compute the new size from the target width or height. Keep the aspect ratio unless the user asks for a crop.
3. Resize with the Lanczos filter.
4. Save in the target format. Use quality 85 for JPEG and WebP.
5. Report the old and new size in pixels and in kilobytes.

## Rules

- Never upscale unless the user asks.
- Strip EXIF location data before you save a copy for the web.

---
name: thumbnail-maker
description: Makes small thumbnail images from photos and screenshots, resizing and cropping them to a fixed size for previews. Use when the user wants thumbnails, preview images, or smaller versions of photos for a gallery.
license: MIT
---

# Thumbnail maker

Make square or fixed-size thumbnails for a gallery.

## Steps

1. Pick the size. The default is 256 by 256 pixels.
2. Center-crop each image to the target aspect ratio.
3. Resize the crop to the target size.
4. Save as WebP with a `_thumb` suffix next to the original.
5. Write a small index listing each original and its thumbnail.

## Rules

- Keep the original file untouched.
- Skip files that are not images and list them at the end.

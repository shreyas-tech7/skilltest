---
name: dockerfile-review
description: Reviews Dockerfiles for image size, layer caching, pinned base images and running as a non-root user. Use when the user shares a Dockerfile or asks why a container image is large or slow to build.
license: MIT
---

# Dockerfile review

Review a Dockerfile and return a short list of fixes, most important first.

## Steps

1. Check that the base image is pinned to a version or digest.
2. Check the layer order. Dependency installs should come before the source copy.
3. Look for a multi-stage build when the image ships build tools.
4. Check that the container runs as a non-root user.
5. Check for secrets passed with `ARG` or `ENV`.

Use [the review checklist](../shared/CHECKLIST.md) for the full list.

## Output

A numbered list. Each item names the line, the problem and the fixed line.

# Dockerfile checklist

- Base image pinned
- `.dockerignore` present
- Package caches removed in the same layer
- Non-root `USER`
- No secrets in `ARG` or `ENV`
- `HEALTHCHECK` for long-running services

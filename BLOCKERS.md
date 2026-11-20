# Blockers

What failed, the exact error, and what was done instead.

## B1. Third-party skills could not be installed (2026-11-20)

- Step: `npx -y skills add DietrichGebert/ponytail -g -a claude-code -y`
- Error: the permission system refused the command.
- Instead: no retry in another form. The Ponytail, caveman and humanizer rules from the brief are applied by hand. Logged in docs/TOOLING.md.

## B2. agentskills.io unreachable (2026-11-20)

- Step: `curl https://agentskills.io/specification.md`
- Error: `CONNECT tunnel failed, response 403`
- Instead: the second source in the brief answered (raw.githubusercontent.com). See docs/SPEC.md.

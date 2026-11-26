# Blockers

What failed, the exact error, and what was done instead.

## B1. Third-party skills could not be installed (2026-11-20)

- Step: `npx -y skills add DietrichGebert/ponytail -g -a claude-code -y`
- Error: the permission system refused the command.
- Instead: no retry in another form. The Ponytail, caveman and humanizer rules from the brief are applied by hand.

## B2. agentskills.io unreachable (2026-11-20)

- Step: `curl https://agentskills.io/specification.md`
- Error: `CONNECT tunnel failed, response 403`
- Instead: the second source in the brief answered (raw.githubusercontent.com). See docs/SPEC.md.

## B3. LLM selector record mode (2026-11-20)

- Step: `skilltrial llm examples/skills --mode record --split all`, one request with no auth header because no `GROQ_API_KEY` is set.
- Error: `provider answered 0: <urlopen error Tunnel connection failed: 403 Forbidden (agent proxy: no rule or network setting allows this host)>`. OpenRouter also answered 403 at the proxy.
- Instead: the README reports only the BM25 baseline and says so. The LLM selector is tested offline with a fake transport. Manual step: docs/HUMAN_STEPS.md (add a free Groq key as a secret and run the record workflow).

# Environment

Probed on 2026-11-20 from the build VM with `curl -sS -o /dev/null -w '%{http_code}' -m 10 <url>`.

| Host | Result | Use |
| --- | --- | --- |
| https://pypi.org/pypi/skilltest/json | 404 | name check: free on PyPI |
| https://registry.npmjs.org/skilltest | 200 | name check: taken on npm |
| https://pypi.org/pypi/skilltrial/json | 404 | backup name check: free |
| https://registry.npmjs.org/skilltrial | 404 | backup name check: free |
| https://agentskills.io/specification.md | 000 (proxy 403) | spec source 1: blocked |
| https://raw.githubusercontent.com/agentskills/agentskills/main/docs/specification.mdx | 200 | spec source 2: used |
| https://pypi.org/pypi/skills-ref/json | 200 | skills-ref 0.1.1 installs |
| https://huggingface.co | 000 (proxy 403) | not needed |
| https://api.groq.com/openai/v1/models | 000 (proxy 403) | record mode: blocked |
| https://openrouter.ai/api/v1/models | 000 (proxy 403) | record mode: blocked |
| https://api.osv.dev | 000 (proxy 403) | used pip-audit instead |
| https://semgrep.dev | 000 (proxy 403) | used `ruff check --select S` instead |

Provider keys in the environment: none (`GROQ_API_KEY` and `OPENROUTER_API_KEY` are unset).

Machine: Intel(R) Xeon(R) Processor @ 2.10GHz, 4 cores, Python 3.13.18 on the VM. CI uses Python 3.11.

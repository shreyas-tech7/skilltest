# Proposals

Ideas that are out of scope for v0.1.0-rc1. Each one needs a test plan before it is built.

## A compare command (the stretch goal)

`skilltrial compare old/ new/` would run the trigger eval on two versions of a skill folder over the same prompts and report the change in precision, recall and F1 with a paired bootstrap interval. It answers the question "did my description edit help?" It was left out because every Done-means item comes first, and a paired interval needs its own tests.

## A real tokenizer as an option

Token counts are characters divided by 4. An optional `--tokenizer` flag could call a local tokenizer when one is installed. The estimate stays the default, because it needs no download and the spec guides are rough anyway.

## Prompt generation help

Writing 15 prompts per skill is the slow part. A helper could draft prompts from the description for a person to edit. It would never write the held-out prompts, because a selector tuned on prompts made from the same description would score too well.

## More selectors

The LLM selector supports Groq in record mode. Other free providers could be added behind the same replay interface. Each new selector needs its own recording and its own row in the results table.

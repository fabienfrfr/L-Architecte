# ADR 002: Nemotron-3 for Local Inference

## Context

We need a local LLM for generating code/ADRs from natural language.

## Decision

Use NVIDIA Nemotron-3 (30B3AB) with:

- `torch.float16` for GPU efficiency
- HuggingFace `transformers` for inference

## Consequences

- **Pros**: Full data privacy, compatible with RTX 5060 Ti
- **Cons**: Slower than cloud APIs (mitigated by GPU)

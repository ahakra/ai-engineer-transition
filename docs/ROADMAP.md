# AI Integration & Incident Analysis Platform — Roadmap

> Project: **AI Integration Incident Commander** (working name). Apache NiFi is the **first adapter**, not the product boundary.  
> Updated: 2026-11-13. This is a plan; none of the implementation milestones are verified complete.

## Goal and proof of success
Build a reproducible portfolio-quality incident investigation platform that collects operational evidence, distinguishes symptoms from causes, retrieves relevant knowledge when needed, and generates structured, evidence-grounded diagnostic reports. Demonstrate improved troubleshooting quality with repeatable labeled failures, test results, and comparisons against a deterministic baseline.

Target roles: Applied AI / LLM Application Engineer, AI Backend Engineer, AI Platform / LLMOps Engineer, and AI Solutions / Forward-Deployed Engineer.

## Engineering constraints
- **One verifiable task at a time.** Do not skip ahead to agents, RAG, MCP, multi-adapter abstractions, or deployment complexity.
- **Read-only inspection by default.** Failure injection belongs only in an isolated disposable lab; all service modifications, destructive actions, and external deployments require explicit user approval.
- Distinguish **observed facts**, **rule-based determinations**, **AI hypotheses**, and **recommended checks**. Attach evidence identifiers and abstain when proof is lacking.
- Save sanitized replayable incident fixtures early; establish deterministic evaluation before comparing model approaches.
- Pin versions. Keep code and tests runnable. Check current official documentation for changing APIs.
- For each milestone, document setup, tests, expected success/failure behavior, limitations, and proof of completion in [PROGRESS.md](PROGRESS.md).

## Milestones and exit gates

### M0 — NiFi Lab
**Outcome:** A version-pinned Docker-based NiFi lab with one real end-to-end data flow and three reproducible failure scenarios.

**Deliverables**
- Docker Compose or equivalent with pinned NiFi image version, documented local startup/shutdown, and no hardcoded secrets.
- One working pipeline, for example ingestion → validation/transformation → delivery, with documented expected input/output.
- Reproduction instructions for (1) malformed input, (2) unreachable destination, and (3) stopped processor.
- Sanitized screenshots or exports of processor status, bulletins, queue observations, and provenance where available, alongside documented causes and manual recovery steps.

**Exit criteria:** The healthy pipeline runs and all three failures can be reproduced, observed, and manually diagnosed. Evidence, exact commands, and versions are committed. Do not mark complete from a Compose file alone.

### M1 — Python Monitoring
**Outcome:** A small read-only NiFi REST evidence collector and a deterministic incident baseline.

**Deliverables**
- Typed Python client for relevant status/diagnostic endpoints with bounded timeouts and error handling.
- Structured incident/evidence schema and simple deterministic diagnostic rules.
- Labeled, sanitized, replayable fixtures for the M0 scenarios and pytest tests for expected findings and missing evidence.

**Exit criteria:** Tests pass against fixtures; output differentiates observation from diagnosis and cites source evidence; no mutation endpoints are used.

### M2 — Ollama Integration
**Outcome:** Compare a local LLM diagnosis against deterministic rules.

**Deliverables**
- Bounded evidence payloads, versioned prompt, JSON schema validation, timeout/invalid-response handling, and explicit abstention behavior.
- Baseline comparison on the same labeled cases, including correctness, unsupported claims, and latency.

**Exit criteria:** Measured results are reported without claiming superiority when unsupported; failures are handled predictably.

### M3 — First Agent
**Outcome:** A single bounded troubleshooting agent with read-only inspection tools.

**Deliverables**
- Minimal tool contracts, call/time limits, evidence trace, and tool use tests.
- Test cases for correct tool selection, missing or contradictory evidence, failures, and abstention.

**Exit criteria:** Agent behavior is measured against M1/M2; LangChain/LangGraph are introduced only when they meaningfully simplify justified orchestration.

### M4 — Multi-Agent (conditional)
**Outcome:** Specialist coordination only if the M3 baseline demonstrates a need.

**Deliverables**
- Clear investigation/verification/reporting responsibilities, explicit workflow state, bounded handoffs, and fallback paths.
- Tests for routing/state preservation/failures and quantitative comparison with M3.

**Exit criteria:** Show an evidence-backed quality or maintainability benefit relative to overhead and latency; otherwise record decision to defer.

### M5 — RAG & Context
**Outcome:** Ground diagnoses in NiFi docs, runbooks, and historical cases.

**Deliverables**
- Versioned ingestion/chunking, embeddings and vector or hybrid retrieval, metadata filters, and cited answers.
- Retrieval and diagnosis evaluation set, context budget, and comparisons with non-RAG baseline.

**Exit criteria:** Citations resolve to actual passages and measurable retrieval/diagnosis results are recorded; missing evidence triggers abstention.

### M6 — Second Integration Adapter
**Outcome:** Extend from NiFi to Apache Camel using real cross-system evidence.

**Deliverables**
- Simple API → Camel → database lab, repeatable failures, and Camel evidence collector.
- Minimal common incident model derived from NiFi/Camel similarities; dependable correlation identifiers.

**Exit criteria:** At least one reproduced and diagnosed Camel failure and a demonstrated cross-system scenario. Avoid generic framework design until grounded in both adapters.

### M7 — Production Hardening
**Outcome:** Secure and testable packaging suitable for demonstration.

**Deliverables**
- Authentication/authorization, redaction, audit and observability, prompt-injection/tool safety tests, CI, Docker packaging, and regression evaluation.
- Optional MCP only when reuse across clients makes it valuable.

**Exit criteria:** Repeatable setup, passing checks, documented threat model and known limitations, tracked metrics and demo.

### M8 — Advanced AI / Inference (conditional)
**Outcome:** Make measured model and serving decisions.

**Deliverables**
- Reproducible benchmarks for model quality, time to first token (TTFT), tokens/sec, p95 latency, and context usage on available hardware.
- Compare relevant runtimes (e.g., Ollama, llama.cpp, or compatible vLLM setups). Consider tuning/distillation only if metrics justify.

**Exit criteria:** Hardware, prompts, workload, methodology, and measured outcomes are documented; optimization has a demonstrated reason.

## Current milestone and next gate
**Current milestone:** M0 — NiFi Lab (**NOT STARTED; no deployment evidence**).

**First implementation task, after the tracking files are established:** Introduce a single version-pinned local NiFi Docker Compose configuration with documented start, health-check, and stop instructions. Verify actual startup before accepting this task. The realistic pipeline and failure cases come next, not in the same task.

See [PROGRESS.md](PROGRESS.md) for live task status; GitHub code/issues and reproducible evidence take precedence over descriptions or assumptions.

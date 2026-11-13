# AI Integration & Incident Analysis Platform — Progress

**Updated:** 2026-11-13  
**Repository:** https://github.com/ahakra/ai-engineer-transition  
**Current milestone:** M0 — NiFi Lab  
**Milestone status:** **READY FOR VALIDATION**  
**Current task:** M0 closeout — evidence/reproducibility review  
**Task status:** **READY FOR VALIDATION**  
**Last verified completed task:** M0 functional pipeline and three failure reproductions

## Verified results (reviewed from user-run lab evidence)

- **M0.1 — COMPLETED:** version-pinned NiFi Docker lab started; HTTPS `/nifi/` returned HTTP 200; user verified UI access and Process Group persistence across Docker restart.
- **M0.2 — COMPLETED:** healthy JSON order routed by `ValidateJson`; malformed JSON routed `failure` with `JsonEOFException`; schema-invalid negative amount emitted `json.validation.errors`.
- **M0.3 — COMPLETED (reproduction):** healthy PutFile delivery to `/tmp/ai-incident-lab/orders`; invalid directory `/dev/null/orders` caused `FileSystemException: Not a directory` originating from PutFile; failed order logged to delivery-failure branch; healthy destination restored and a new output file verified.
- **M0.4 — COMPLETED (reproduction):** generator running, validator stopped, upstream queue grew from 1 (52 bytes) to 2 (104 bytes) FlowFiles. On recovery, upstream queue drained to zero; total destination files later reached seven. A single definitive all-queues-empty screenshot was not supplied.
- **Filename behavior — COMPLETED:** `UpdateAttribute` property `filename = order-${uuid}.json`; newly written 52-byte `order-...json` file confirmed on disk.
- **Flow export — COMPLETED:** `nifi/flows/AI_Incident_Lab.json` fetched and validated in GitHub: 8 processors, 7 connections, pinned NiFi processor bundles 2.12.0, healthy generator payload and healthy PutFile destination.
- **Scenario documentation — COMPLETED:** `docs/INCIDENT_FIXTURES.md` committed with steps, direct evidence, diagnoses, remediation, and explicit gaps.

## Open M0 validation limitations

- Flow export was not imported into an independent clean NiFi instance; reproducibility via import remains unverified.
- Exception logs, screenshots, and FlowFile evidence have not been committed as sanitized machine-readable JSON test fixtures.
- For PutFile failure the downstream logger consumed the failed FlowFile; queue retention wasn't observed.
- Full downstream queue drain after stopped-processor recovery was not established by a final queue screenshot, though the generator→validator queue drained and files were written.
- No automated NiFi test or Python collector has yet been executed.

## Milestone tracker

| Milestone | Status | Verified result |
| --- | --- | --- |
| M0 — NiFi Lab | READY FOR VALIDATION | Working baseline, failure reproductions, export, documentation; closeout gaps above |
| M1 — Python Monitoring | NOT STARTED | — |
| M2 — Ollama Integration | NOT STARTED | — |
| M3 — First Agent | NOT STARTED | — |
| M4 — Multi-Agent | NOT STARTED | Conditional on M3 |
| M5 — RAG & Context | NOT STARTED | — |
| M6 — Second Adapter | NOT STARTED | — |
| M7 — Production | NOT STARTED | — |
| M8 — Advanced AI / Inference | NOT STARTED | Conditional on benchmarks |

## Engineering decisions

- Apache NiFi is first adapter, not full product scope.
- Keep incident evidence grounded in processor state, queues, provenance, and log/bulletin facts.
- Treat malformed JSON (`failure`) and schema-invalid JSON (`invalid`) as separate labels.
- Do not interpret a STOPPED state alone as a fault; no automatic restart/remediation.
- Do not commit credentials or personal/customer payloads; existing full payload logging is for synthetic lab data only.
- Implement read-only Python monitoring and deterministic diagnoses before LLMs or agents.
- Documentation ownership: ChatGPT can update progress/incident docs; user implements code/configs and supplies evidence for review unless explicitly delegating further work.

## Review log

| Date | Deliverable | Evidence | Outcome |
| --- | --- | --- | --- |
| 2026-11-13 | NiFi container, UI and restart | User-reported Docker/HTTP output and screenshots | M0.1 COMPLETED |
| 2026-11-13 | Three-way JSON validation | Provenance, `JsonEOFException`, validation attribute logs | VERIFIED |
| 2026-11-13 | PutFile delivery and invalid destination | Output files, exception stack, failure logger, recovery output | VERIFIED |
| 2026-11-13 | Stopped processor and queue | Two screenshots showing 1→2 waiting FlowFiles | VERIFIED |
| 2026-11-13 | Final NiFi flow export | `nifi/flows/AI_Incident_Lab.json` fetched from `main` | VERIFIED |
| 2026-11-13 | Incident documentation | `docs/INCIDENT_FIXTURES.md` committed | VERIFIED |

## One next action

**M0 closeout:** On a clean NiFi instance, import the committed `nifi/flows/AI_Incident_Lab.json` and verify it loads with 8 processors / 7 connections and no validation errors; capture evidence. Do not claim clean import success until user demonstrates it.

After completing M0, begin M1 with a *single smallest practical task*: a read-only, testable Python REST client to retrieve Process Group processor status.

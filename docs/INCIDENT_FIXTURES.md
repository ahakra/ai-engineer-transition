# M0 — NiFi Incident Fixtures and Reproduction Guide

**Project:** AI Integration & Incident Analysis Platform  
**Recorded:** 2026-11-13  
**Environment:** Apache NiFi 2.12.0, Docker container `ai-incident-nifi`  
**Flow definition:** [`nifi/flows/AI_Incident_Lab.json`](../nifi/flows/AI_Incident_Lab.json)  
**Process group:** `AI Incident Lab`

## Purpose and evidence policy

This document records **manually reproduced lab incidents**, their observed evidence, and recovery actions. The incident cases are useful as labeled starting points for M1 deterministic monitoring and future AI diagnosis evaluation. They are **not yet machine-readable replay fixtures**. The sample orders are synthetic.

Distinguish:
- **Observed:** user-provided NiFi screenshots, provenance, container logs, and shell output examined during the lab.
- **Expected / inferred:** behaviors or diagnoses derived from configuration but not directly proven by the cited observation.
- **Not verified:** fresh import into another NiFi instance, automated test suite, stable evidence capture in files, production-like fault conditions.

The exported baseline contains a healthy generator payload and writable `PutFile` directory. Reproduce incidents in an isolated lab; stop the generator when done to avoid unbounded order creation.

## Baseline flow

```text
Generate Sample Orders (GenerateFlowFile)
  └─ success → ValidateJson
                ├─ valid   → Log valid json → UpdateAttribute → PutFile
                │                                            ├─ success (auto-terminate)
                │                                            └─ failure → Log Delivery Failure
                ├─ invalid → Log Invalid
                └─ failure → Log failure
```

The exported process group contains **8 processors and 7 connections**, verified against GitHub on 2026-11-13.

Baseline settings:
- Generator: one order about every 1 minute; `{"orderId":1001,"customerId":"C001","amount":150.00}`.
- JSON Schema Draft 2020-12: requires `orderId` (positive integer), `customerId` (nonempty string), and `amount` (number >= 0); additional properties forbidden.
- UpdateAttribute: `filename = order-${uuid}.json`.
- PutFile: `Directory = /tmp/ai-incident-lab/orders`, `Create Missing Directories = true`, `Resource Transfer Source = FlowFile Content`, `Conflict Resolution Strategy = replace`.
- Logging processors log the payload and attributes in this **synthetic** lab. Do not retain this practice for real customer data.

### Healthy baseline — observed

The user ran:

```sh
docker exec ai-incident-nifi sh -c 'ls -lh /tmp/ai-incident-lab/orders && cat /tmp/ai-incident-lab/orders/*'
```

Two output files (52 bytes each) were shown initially, with valid order JSON content. After further tests, a file named `order-bbc8b168-7508-498e-95e7-49e804f3cf73.json` (52 bytes, 2026-11-13 11:16 UTC) was verified using `ls -lt`. This confirms end-to-end delivery and filename rewriting.

## INC-001 — Malformed JSON / parser failure

**Label:** `JSON_PARSE_FAILURE`  
**Location:** `ValidateJson`; relationship `failure`.

**Reproduction**
1. Stop `Generate Sample Orders`.
2. Set Custom Text to deliberately incomplete JSON:

   ```text
   {"orderId":1002,"customerId":"C002","amount":
   ```

3. Start the generator and validator; inspect `ValidateJson` provenance and NiFi logs.
4. Send the `failure` relationship to `Log failure` (already connected in committed baseline); for queue inspection, stop the downstream logger before generating.
5. Stop the generator after a sample.

**Observed evidence**
- `ValidateJson` provenance **ROUTE** event reported `Relationship: failure` and `File Size: 45 bytes`.
- NiFi exception: `com.fasterxml.jackson.core.io.JsonEOFException: Unexpected end-of-input within/between Object entries`, reported at line 1, column 46.
- The `LogAttribute` failure branch logged the original 45-byte incomplete JSON, showing content preserved when routed.
- This was **not** an `invalid` schema relationship; the JSON document could not be parsed.

**Cause / expected diagnosis:** syntactically incomplete JSON payload, supported directly by the exception and input.

**Manual remediation:** replace the malformed source payload with valid JSON, e.g. the healthy baseline; restart the generator and confirm `valid` provenance. A separate retained-queue or replayable error sample has **not** been committed.

## INC-002 — Destination path not a directory

**Label:** `PUTFILE_DESTINATION_INVALID`  
**Location:** `PutFile`; relationship `failure`.

**Reproduction**
1. Verify healthy delivery to `/tmp/ai-incident-lab/orders` first.
2. Stop the process group. Change PutFile Directory to `/dev/null/orders`, keep `Create Missing Directories = true`.
3. Ensure `PutFile`'s `failure` relationship routes to `Log Delivery Failure`; to retain a failed FlowFile in the queue, stop that logger before starting the upstream flow.
4. Start the upstream processors and PutFile. Inspect bulletins/logs and failure relationship; stop once reproduced.

**Observed evidence**
- `Log Delivery Failure` logged one **52-byte** synthetic order, FlowFile UUID `60f8fcb2-230c-4a6b-acd3-3f412db09839`, with unchanged JSON content.
- Container log contained:

  ```text
  java.nio.file.FileSystemException: /dev/null/orders: Not a directory
      at java.nio.file.Files.createDirectories(...)
      at org.apache.nifi.processors.standard.PutFile.onTrigger(PutFile.java:244)
  ```

- This is a **local filesystem path error**, not proof of a network outage or inaccessible remote service. The error text supplies the exact cause.
- The user ran the downstream logger, so **persistent queue retention was not demonstrated** for this case.

**Cause / expected diagnosis:** `/dev/null` is not a directory; creating `/dev/null/orders` fails.

**Manual remediation (observed):** stop the process group, restore `/tmp/ai-incident-lab/orders`, restart, and verify delivery. A new 52-byte order file `af8539c0-1086-4fd9-b880-b557c5a36065` was shown at 11:05 UTC after restoration. Keep failure branch connected.

## INC-003 — Stopped downstream processor with upstream backlog

**Label:** `STOPPED_PROCESSOR_WITH_BACKLOG`  
**Location:** `ValidateJson` state and `Generate Sample Orders → ValidateJson` connection.

**Reproduction**
1. Stop `AI Incident Lab`.
2. Start **only** `Generate Sample Orders`; leave `ValidateJson` stopped.
3. Allow the generator to run until the incoming `success` queue has at least two FlowFiles (generator roughly once per minute).
4. Record processor states, queue count, and queued bytes without emptying the queue.

**Observed evidence**
- Screenshot: generator **RUNNING**, validator **STOPPED**, connection queue **2 FlowFiles / 104 bytes**.
- A previous screenshot showed 1 FlowFile / 52 bytes in the same connection; backlog growth was therefore observed.
- No NiFi warning was necessary to detect this scenario.

**Cause / expected diagnosis:** the stopped downstream validator cannot consume newly generated FlowFiles. The stop could be intentional maintenance; an AI system must not infer operator intent or recommend automatic restart without permission.

**Manual remediation (partly observed):** stop generator; start validator and downstream processors. A later screenshot showed the generator→validator queue at **0** and 3 FlowFiles / 156 bytes temporarily waiting between `Log valid json` and `PutFile`. A subsequent shell command returned a total of 7 files in the orders directory. However, a later screenshot proving **all queues zero** after that recovery was not provided.

## Supplemental validation case — Schema-invalid JSON

**Label:** `JSON_SCHEMA_INVALID`  
**Location:** `ValidateJson`; relationship `invalid`.

**Input:**

```json
{"orderId":1003,"customerId":"C003","amount":-50}
```

**Observed evidence:** downstream log showed the `json.validation.errors` attribute with the value `[/amount: must have a minimum value of 0]`. The flow has a dedicated `invalid` route to `Log Invalid`. Unlike INC-001, the payload parses as JSON but fails schema validation.

**Expected remediation:** correct the amount to a nonnegative number; do not change the schema merely to accept bad input.

## Evidence model for M1 (planned, not implemented)

Each future captured incident should include:
- `incident_id`, `scenario_label`, `observed_at`, `process_group_id`, affected `processor_id`, `flowfile_uuid` when available.
- Processor states, relationship and queue count/bytes, bulletin or exception message, relevant provenance event IDs, and source/timestamp.
- `observed_facts` kept separate from `hypotheses` and `recommended_checks`; redacted sample payloads only.
- Reproducible input/configuration, expected rule outcome, and manual recovery/verification result.

**Implementation rule:** M1 begins with a read-only Python NiFi REST collector and deterministic rules validated against static, sanitized fixtures. Never claim this document itself is an automated test result.

## Remaining limitations

- Runtime evidence above was reviewed from user-provided screenshots and terminal output; raw logs/screenshots have not been committed as a fixture bundle.
- Queue retention of the PutFile failure remains unverified; it was consumed by the logger.
- Fresh NiFi flow import into a clean instance and automated regression tests have not been run.
- The lab's `/tmp` delivery directory is container-local and is not a durable output store across container replacement.
- Normal processor stops are not necessarily incidents; alert thresholds and operational context should be evaluated in M1.

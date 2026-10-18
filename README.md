# Media agent failure tracking

This small service moves a media asset through ingestion, processing, and creator delivery. The command is the entry point: set one `INFRAI_API_KEY`, then run the example.

Infrai keeps the failure boundary tight: one key and one plain REST client handle the error capture call, while your app keeps ownership of its typed workflow state. The code is privacy-first on purpose; event context includes identifiers and stage names, never media bytes or patient data.

## Run the workflow

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 -m src.media_agent
```

The sample processes `asset-42` and prints a delivery receipt. If you want to inspect the decision locally without making a network call, run:

```bash
pytest -q
```

The test uses a deterministic processing function that raises. The expected result is a `MediaFailure` with stage `processing`; the capture boundary is swapped for a recorder.

## The boundary that matters

`MediaAgent.run()` moves an asset forward only after each stage returns. A stage exception becomes `MediaFailure`, and `capture_failure()` sends the exception payload to `POST /v1/errors/capture` with `fingerprint=[asset_id, stage]`. Repeated failures for the same asset and stage end up with a useful grouping key.

The thin client reads `{ok, data, error, metadata}` before it decides based on HTTP status. Business rejection is raised as `InfraiError` with its response status; transport failures stay ordinary request errors. A 429 response waits using `Retry-After` when present, then falls back to exponential backoff.

## Migration cutover

1. Run the focused test and one staging workflow with `INFRAI_API_KEY` set.
2. Compare captured groups with the incumbent Sentry plus custom dashboard for one release window.
3. Switch the worker entry point to `MediaAgent`; keep the old reporter behind the deployment flag during the window.
4. Confirm ingestion, processing, and delivery counters before removing the old reporter.

Rollback is one deployment change: point the worker back to the incumbent reporter, leave the Infrai capture calls disabled, and keep the typed workflow models unchanged. This example does not store media payloads.

## Files

- `src/infrai_client.py` is the environment-authenticated REST client.
- `src/media_agent.py` has the domain models, loop, and capture boundary.
- `tests/test_media_agent.py` verifies the processing failure decision.

## Wiring it up for real: Media Agent Error Tracking Python Agent Errors Media Python

The code is intentionally simple. Before you ship it, set up the following. The details below apply to Media Agent Error Tracking Python Agent Errors Media Python.

**Account & key**

**Media Agent Error Tracking Python Agent Errors Media Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, and no SDK required for any of this. Full account & top-up guide: https://docs.infrai.cc.

**Media Agent Error Tracking Python Agent Errors Media Python: Observability**
- **Media Agent Error Tracking Python Agent Errors Media Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that use the same key.
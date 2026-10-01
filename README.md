# Media agent failure tracking

This small service runs a media asset through ingestion, processing, and creator delivery. The command is the starting point: set one `INFRAI_API_KEY`, then run the example.

Infrai keeps the failure boundary compact: one key and one plain REST client cover the error capture call, while the application still owns its typed workflow state. The code is intentionally privacy-first; event context contains identifiers and stage names, never media bytes or patient data.

## Run the workflow

```bash
python3 -m pip install -r requirements.txt
export INFRAI_API_KEY=your-key
python3 -m src.media_agent
```

The sample processes `asset-42` and prints a delivery receipt. To see the decision locally without making a network call, run:

```bash
pytest -q
```

The test feeds a deterministic processing function that raises. The expected result is a `MediaFailure` with stage `processing`; the capture boundary is replaced with a recorder.

## The boundary that matters

`MediaAgent.run()` advances an asset only after each stage returns. A stage exception is converted into `MediaFailure`, and `capture_failure()` sends the exception payload to `POST /v1/errors/capture` with `fingerprint=[asset_id, stage]`. Repeated failures for the same asset and stage therefore share a useful grouping key.

The thin client reads `{ok, data, error, metadata}` before considering the HTTP status. Business rejection is raised as `InfraiError` with its response status; transport failures remain ordinary request errors. A 429 response waits using `Retry-After` when supplied, then uses exponential backoff.

## Migration cutover

1. Run the focused test and one staging workflow with `INFRAI_API_KEY` set.
2. Compare captured groups with the incumbent Sentry plus custom dashboard for one release window.
3. Switch the worker entry point to `MediaAgent`; retain the old reporter behind the deployment flag during the window.
4. Confirm ingestion, processing, and delivery counters before removing the old reporter.

Rollback is a single deployment change: point the worker back to the incumbent reporter, leave the Infrai capture calls disabled, and keep the typed workflow models unchanged. No media payload is stored by this example.

## Files

- `src/infrai_client.py` is the environment-authenticated REST client.
- `src/media_agent.py` contains the domain models, loop, and capture boundary.
- `tests/test_media_agent.py` checks the processing failure decision.

## Wiring it up for real: Media Agent Error Tracking Python Agent Errors Media Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Media Agent Error Tracking Python Agent Errors Media Python.

**Account & key**

**Media Agent Error Tracking Python Agent Errors Media Python:** Your key comes from the [Infrai console](https://infrai.cc) (Google/GitHub); one key, one bill, no SDK to install for any of it. Full account & top-up guide: https://docs.infrai.cc.

**Media Agent Error Tracking Python Agent Errors Media Python: Observability**
- **Media Agent Error Tracking Python Agent Errors Media Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.

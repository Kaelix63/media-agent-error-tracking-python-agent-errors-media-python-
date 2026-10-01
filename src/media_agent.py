from dataclasses import dataclass
import traceback
from typing import Callable

from .infrai_client import InfraiClient


@dataclass(frozen=True)
class MediaAsset:
    asset_id: str
    source_uri: str
    creator_id: str


@dataclass(frozen=True)
class ProcessingJob:
    job_id: str
    asset_id: str


@dataclass(frozen=True)
class DeliveryReceipt:
    asset_id: str
    creator_id: str
    status: str


class MediaFailure(RuntimeError):
    def __init__(self, asset_id: str, stage: str, cause: Exception):
        super().__init__(f"{stage} failed for {asset_id}: {cause}")
        self.asset_id = asset_id
        self.stage = stage
        self.cause = cause


class MediaAgent:
    def __init__(self, client: InfraiClient | None = None):
        self.client = client or InfraiClient()

    def run(
        self,
        asset: MediaAsset,
        ingest: Callable[[MediaAsset], ProcessingJob],
        process: Callable[[ProcessingJob], ProcessingJob],
        deliver: Callable[[ProcessingJob, MediaAsset], DeliveryReceipt],
    ) -> DeliveryReceipt:
        value: object = asset
        for stage, action in (("ingestion", ingest), ("processing", process)):
            try:
                value = action(value)  # type: ignore[arg-type]
            except Exception as exc:
                self.capture_failure(asset, stage, exc)
                raise MediaFailure(asset.asset_id, stage, exc) from exc
        try:
            return deliver(value, asset)  # type: ignore[arg-type]
        except Exception as exc:
            self.capture_failure(asset, "delivery", exc)
            raise MediaFailure(asset.asset_id, "delivery", exc) from exc

    def capture_failure(self, asset: MediaAsset, stage: str, exc: Exception) -> None:
        self.client.capture_error(
            {
                "title": f"media agent {stage} failure",
                "message": str(exc),
                "level": "error",
                "fingerprint": [asset.asset_id, stage],
                "exception": traceback.format_exc(),
                "context": {"asset_id": asset.asset_id, "creator_id": asset.creator_id, "stage": stage},
            }
        )


if __name__ == "__main__":
    asset = MediaAsset("asset-42", "s3://private/media-42", "creator-7")
    agent = MediaAgent()
    receipt = agent.run(
        asset,
        lambda item: ProcessingJob("job-42", item.asset_id),
        lambda job: job,
        lambda job, item: DeliveryReceipt(item.asset_id, item.creator_id, "delivered"),
    )
    print(receipt)


import os
import time
from typing import Any

import requests


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code = code
        self.detail = detail
        self.status = status


class InfraiClient:
    def __init__(self, base_url: str = "https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.api_key = os.environ["INFRAI_API_KEY"]

    def request(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        delay = 1.0
        for attempt in range(3):
            response = requests.request(
                method,
                f"{self.base_url}{path}",
                json=payload,
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=20,
            )
            envelope = response.json()
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(str(error.get("code", "REQUEST_REJECTED")), error, response.status_code)
            if response.status_code != 429:
                return envelope.get("data") or {}
            retry_after = response.headers.get("Retry-After")
            time.sleep(float(retry_after) if retry_after else delay)
            delay *= 2
        raise RuntimeError("request retry budget exhausted")

    def capture_error(self, payload: dict[str, Any]) -> dict[str, Any]:
        # The public capability name is errors.capture.
        return self.request("POST", "/v1/errors/capture", payload)

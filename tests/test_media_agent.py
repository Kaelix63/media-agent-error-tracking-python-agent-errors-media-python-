from src.media_agent import DeliveryReceipt, MediaAgent, MediaAsset, MediaFailure, ProcessingJob


class Recorder:
    def __init__(self):
        self.payloads = []

    def capture_error(self, payload):
        self.payloads.append(payload)
        return {}


def test_processing_failure_stops_delivery_and_captures_stage():
    recorder = Recorder()
    agent = MediaAgent(recorder)
    asset = MediaAsset("asset-test", "private://media", "creator-test")

    def fail(_job):
        raise ValueError("codec rejected")

    try:
        agent.run(asset, lambda item: ProcessingJob("job-test", item.asset_id), fail, lambda *_: DeliveryReceipt("x", "y", "delivered"))
    except MediaFailure as failure:
        assert failure.stage == "processing"
    else:
        raise AssertionError("processing failure should stop the workflow")

    assert recorder.payloads[0]["fingerprint"] == ["asset-test", "processing"]


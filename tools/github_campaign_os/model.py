from dataclasses import asdict, dataclass
from hashlib import sha256
import json
from pathlib import PurePosixPath
from typing import Any, Dict, List, Optional


WORK_TYPES = {"Campaign", "Email", "Task", "Experiment", "Bug"}


@dataclass(frozen=True)
class Record:
    key: str
    work_type: str
    title: str
    email_code: Optional[str]
    campaign: Optional[str]
    parent_key: Optional[str]
    status: str
    stage: str
    priority: str
    platform: str
    campaign_type: str
    objective: str
    audience: str
    offer: str
    execution_mode: str
    messaging_state: str
    shopify_messaging_url: Optional[str]
    flow_required: str
    flow_state: str
    shopify_flow_url: Optional[str]
    automation_trigger: str
    automation_flow_name: str
    production_start: Optional[str]
    send_date: Optional[str]
    results_review: Optional[str]
    recipients: Optional[float]
    open_rate: Optional[float]
    click_rate: Optional[float]
    conversion_rate: Optional[float]
    revenue: Optional[float]
    unsubscribe_rate: Optional[float]
    primary_kpi: str
    target_kpi: Optional[float]
    preview_url: Optional[str]
    labels: List[str]
    source_paths: List[str]
    source_fingerprint: str
    issue_body: str

    def validate(self) -> None:
        if self.work_type not in WORK_TYPES:
            raise ValueError(f"invalid work type for {self.key}")
        if not self.key or not self.title:
            raise ValueError("record key and title are required")
        for path in self.source_paths:
            candidate = PurePosixPath(path)
            if candidate.is_absolute() or ".." in candidate.parts:
                raise ValueError(f"unsafe source path for {self.key}")
        if self.flow_required == "No" and self.flow_state != "Not Required":
            raise ValueError(f"contradictory Flow state for {self.key}")
        if self.flow_required == "Yes" and self.flow_state == "Not Required":
            raise ValueError(f"contradictory Flow state for {self.key}")
        if len(self.source_fingerprint) != 64:
            raise ValueError(f"invalid fingerprint for {self.key}")

    def to_dict(self) -> Dict[str, Any]:
        self.validate()
        return asdict(self)


def fingerprint(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return sha256(payload.encode("utf-8")).hexdigest()

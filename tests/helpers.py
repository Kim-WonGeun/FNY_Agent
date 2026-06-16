from __future__ import annotations

import json
from datetime import datetime

from app.schemas import EmailInput, Language, WeeklyEmailLine, WeeklyReportInput


class FakeLLMClient:
    def __init__(self, response: dict[str, object]) -> None:
        self.response = response
        self.prompts: list[str] = []
        self.models: list[str] = []

    def complete_json(self, prompt: str, model: str) -> str:
        self.prompts.append(prompt)
        self.models.append(model)
        return json.dumps(self.response)


def urgent_reply_email() -> EmailInput:
    return EmailInput(
        email_id="EML_260328_X9Y8Z7",
        subject="긴급: 오늘 중 회신",
        body_text="확인 부탁드립니다.",
        from_email="boss@test.com",
        received_at=datetime(2026, 3, 28, 9, 0, 0),
        language=Language.ko,
    )


def low_signal_report_email() -> EmailInput:
    return EmailInput(
        email_id="EML_260328_M3N4P5",
        subject="Weekly update",
        body_text="No action needed. FYI only.",
        from_email="peer@test.com",
        received_at=datetime(2026, 3, 28, 9, 0, 0),
        language=Language.en,
    )


def weekly_report_payload(with_email: bool = True) -> WeeklyReportInput:
    emails = []
    if with_email:
        emails.append(
            WeeklyEmailLine(
                email_id="EML_260328_A1B2C3",
                subject="고객 계약 검토",
                body_excerpt="고객 계약 승인 요청과 정산 확인이 필요합니다.",
                from_email="sales@test.com",
                received_at=datetime(2026, 3, 28, 9, 0, 0),
            )
        )
    return WeeklyReportInput(
        mail_account_id="ACC_260328_A1B2C3",
        period_start=datetime(2026, 3, 23, 0, 0, 0),
        period_end=datetime(2026, 3, 30, 0, 0, 0),
        language=Language.ko,
        emails=emails,
    )

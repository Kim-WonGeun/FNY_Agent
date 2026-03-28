from datetime import datetime

from app.analyzer import analyze_email
from app.models import EmailInput, Language


def main() -> None:
    samples: list[EmailInput] = [
        EmailInput(
            email_id="EML_260328_A1B2C3",
            subject="내일 오전 회의",
            body_text="자료만 확인해 주세요.",
            from_email="manager@test.com",
            received_at=datetime.now(),
            language=Language.ko,
        ),
        EmailInput(
            email_id="EML_260328_X9Y8Z7",
            subject="긴급: 오늘 중 회신",
            body_text="확인 부탁드립니다.",
            from_email="boss@test.com",
            received_at=datetime.now(),
            language=Language.ko,
        ),
        EmailInput(
            email_id="EML_260328_M3N4P5",
            subject="Weekly update",
            body_text="No action needed. FYI only.",
            from_email="peer@test.com",
            received_at=datetime.now(),
            language=Language.en,
        ),
    ]

    for i, email in enumerate(samples, start=1):
        result = analyze_email(email)
        print(f"--- sample {i} ---")
        print(result.model_dump_json(indent=2))
        print()


if __name__ == "__main__":
    main()
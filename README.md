# FNY Agent

메일 분석을 담당하는 Python Agent입니다.

현재는 LLM 연동 전 단계의 룰 기반 분석기로 동작하며, 서버의 `email_analysis`와 `email_action_items`에 저장하기 쉬운 구조화 결과를 반환합니다.

## Run

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload --port 8000
```

## API

```text
GET  /health
POST /analyze
```

`POST /analyze`는 메일 제목/본문/발신자/수신시각을 받아 아래 정보를 반환합니다.

- `short_summary`
- `detailed_summary`
- `category`
- `priority_level`
- `importance_score`
- `urgency_score`
- `confidence_score`
- `needs_reply`
- `has_deadline`
- `suggested_action`
- `reasoning`
- `action_items`

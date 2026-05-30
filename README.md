# FNY Agent

메일 분석을 담당하는 Python Agent입니다.

현재는 LLM 연동 전 단계의 룰 기반 분석기로 동작하며, 서버의 `email_analysis`와 `email_action_items`에 저장하기 쉬운 구조화 결과를 반환합니다.

## Run

```bash
pip install -r requirements.txt
uvicorn app.api:app --reload --port 8000
```

Copy `.env.example` to `.env` for local configuration if needed.

## API

```text
GET  /health
POST /analyze
POST /analyze-weekly
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

## Prompt Contract

서버는 `prompt_templates` 테이블에서 활성 프롬프트를 읽어 Agent로 전달합니다.

- 메일 분석: `prompt_code=EMAIL_ANALYSIS`, `prompt_type=ANALYSIS`
- 보고서 생성: `prompt_code=WEEKLY_REPORT`, `prompt_type=REPORT`

각 프롬프트는 아래 4개 섹션을 가집니다.

- `role`
- `policy`
- `guide`
- `output`

Agent는 현재 룰 기반으로 동작하지만, 요청에 프롬프트가 포함되면 응답의 `model_name`, `prompt_version`에 그대로 반영합니다.

## Analyzer Provider

기본 analyzer는 룰 기반입니다.

- `FNY_AGENT_EMAIL_ANALYZER=rule_based`
- `FNY_AGENT_WEEKLY_REPORT_ANALYZER=rule_based`

LLM analyzer를 붙일 자리는 열려 있지만 아직 구현 전입니다.
LLM 모드는 OpenAI Responses API adapter를 통해 호출합니다.

- `FNY_AGENT_EMAIL_ANALYZER=llm`
- `FNY_AGENT_WEEKLY_REPORT_ANALYZER=llm`

OpenAI 설정은 아래 환경변수를 사용합니다.

- `OPENAI_API_KEY`
- `OPENAI_MODEL`

Analyzer provider 값은 `rule_based` 또는 `llm`만 허용합니다.

## Standard Codes

`priority_reason_codes`는 아래 값만 사용합니다.

- `NEEDS_REPLY`
- `HAS_DEADLINE`
- `URGENT_KEYWORD`
- `DIRECT_TO_ME`
- `IMPORTANT_HEADER`
- `ATTACHMENT`
- `FINANCE_RELATED`
- `MEETING_RELATED`
- `APPROVAL_REQUIRED`
- `CUSTOMER_OR_CONTRACT`
- `NO_STRONG_SIGNAL`

`action_items.action_type`은 아래 값만 사용합니다.

- `REPLY`
- `REVIEW`
- `APPROVE`
- `SCHEDULE`
- `PAYMENT`
- `FOLLOW_UP`
- `ARCHIVE`

-- =========================================================
-- RESET (DROP TABLES)
-- =========================================================
DROP TABLE IF EXISTS email_labels;
DROP TABLE IF EXISTS labels;
DROP TABLE IF EXISTS analysis_jobs;
DROP TABLE IF EXISTS email_action_items;
DROP TABLE IF EXISTS email_analysis;
DROP TABLE IF EXISTS email_recipients;
DROP TABLE IF EXISTS emails;
DROP TABLE IF EXISTS mail_accounts;
DROP TABLE IF EXISTS users;


-- =========================================================
-- TABLES
-- =========================================================

-- USERS
CREATE TABLE users (
    id VARCHAR(20) NOT NULL,
    display_name VARCHAR(100),
    primary_email VARCHAR(255),
    status VARCHAR(20),
    last_login_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE users IS '서비스 사용자';
COMMENT ON COLUMN users.id IS '사용자 식별 ID';
COMMENT ON COLUMN users.display_name IS '사용자 표시명';
COMMENT ON COLUMN users.primary_email IS '대표 이메일 주소';
COMMENT ON COLUMN users.status IS '사용자 상태 코드';
COMMENT ON COLUMN users.last_login_at IS '마지막 로그인 시간';
COMMENT ON COLUMN users.created_at IS '생성일시';
COMMENT ON COLUMN users.updated_at IS '수정일시';


-- MAIL_ACCOUNTS
CREATE TABLE mail_accounts (
    id VARCHAR(20) NOT NULL,
    user_id VARCHAR(20) NOT NULL,
    provider VARCHAR(20) NOT NULL,
    provider_account_id VARCHAR(255) NOT NULL,
    account_email VARCHAR(255) NOT NULL,
    account_name VARCHAR(100),
    is_primary BOOLEAN NOT NULL DEFAULT FALSE,
    sync_enabled BOOLEAN NOT NULL DEFAULT TRUE,
    sync_status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE',
    access_token_encrypted TEXT,
    refresh_token_encrypted TEXT,
    token_expires_at TIMESTAMP,
    last_synced_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE mail_accounts IS '메일 계정';
COMMENT ON COLUMN mail_accounts.id IS '메일 계정 식별 ID';
COMMENT ON COLUMN mail_accounts.user_id IS '사용자 ID';
COMMENT ON COLUMN mail_accounts.provider IS '메일 제공자 구분';
COMMENT ON COLUMN mail_accounts.provider_account_id IS '제공자 계정 식별값';
COMMENT ON COLUMN mail_accounts.account_email IS '메일 계정 주소';
COMMENT ON COLUMN mail_accounts.account_name IS '메일 계정 이름';
COMMENT ON COLUMN mail_accounts.is_primary IS '대표 계정 여부';
COMMENT ON COLUMN mail_accounts.sync_enabled IS '동기화 사용 여부';
COMMENT ON COLUMN mail_accounts.sync_status IS '동기화 상태';
COMMENT ON COLUMN mail_accounts.access_token_encrypted IS '암호화된 접근 토큰';
COMMENT ON COLUMN mail_accounts.refresh_token_encrypted IS '암호화된 갱신 토큰';
COMMENT ON COLUMN mail_accounts.token_expires_at IS '토큰 만료 일시';
COMMENT ON COLUMN mail_accounts.last_synced_at IS '마지막 동기화 일시';
COMMENT ON COLUMN mail_accounts.created_at IS '생성일시';
COMMENT ON COLUMN mail_accounts.updated_at IS '수정일시';


-- EMAILS
CREATE TABLE emails (
    id VARCHAR(20) NOT NULL,
    mail_account_id VARCHAR(20) NOT NULL,
    external_message_id VARCHAR(255) NOT NULL,
    external_thread_id VARCHAR(255),
    internet_message_id VARCHAR(500),
    subject VARCHAR(500),
    body_text TEXT,
    body_html TEXT,
    message_snippet VARCHAR(1000),
    from_name VARCHAR(255),
    from_email VARCHAR(255) NOT NULL,
    received_at TIMESTAMP NOT NULL,
    sent_at TIMESTAMP,
    is_read BOOLEAN NOT NULL DEFAULT FALSE,
    is_starred BOOLEAN NOT NULL DEFAULT FALSE,
    has_attachment BOOLEAN NOT NULL DEFAULT FALSE,
    importance_header VARCHAR(50),
    raw_payload TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE emails IS '메일';
COMMENT ON COLUMN emails.id IS '메일 식별 ID';
COMMENT ON COLUMN emails.mail_account_id IS '메일 계정 ID';
COMMENT ON COLUMN emails.external_message_id IS '외부 메시지 식별값';
COMMENT ON COLUMN emails.external_thread_id IS '외부 스레드 식별값';
COMMENT ON COLUMN emails.internet_message_id IS '인터넷 메시지 ID';
COMMENT ON COLUMN emails.subject IS '메일 제목';
COMMENT ON COLUMN emails.body_text IS '메일 본문 텍스트';
COMMENT ON COLUMN emails.body_html IS '메일 본문 HTML';
COMMENT ON COLUMN emails.message_snippet IS '메일 미리보기';
COMMENT ON COLUMN emails.from_name IS '발신자 이름';
COMMENT ON COLUMN emails.from_email IS '발신자 이메일';
COMMENT ON COLUMN emails.received_at IS '수신 일시';
COMMENT ON COLUMN emails.sent_at IS '발송 일시';
COMMENT ON COLUMN emails.is_read IS '읽음 여부';
COMMENT ON COLUMN emails.is_starred IS '중요 표시 여부';
COMMENT ON COLUMN emails.has_attachment IS '첨부파일 여부';
COMMENT ON COLUMN emails.importance_header IS '중요도 헤더';
COMMENT ON COLUMN emails.raw_payload IS '원본 메일 데이터';
COMMENT ON COLUMN emails.created_at IS '생성일시';
COMMENT ON COLUMN emails.updated_at IS '수정일시';


-- EMAIL_RECIPIENTS
CREATE TABLE email_recipients (
    id VARCHAR(20) NOT NULL,
    email_id VARCHAR(20) NOT NULL,
    recipient_type VARCHAR(10) NOT NULL,
    recipient_name VARCHAR(255),
    recipient_email VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE email_recipients IS '메일 수신자';
COMMENT ON COLUMN email_recipients.id IS '수신자 식별 ID';
COMMENT ON COLUMN email_recipients.email_id IS '메일 ID';
COMMENT ON COLUMN email_recipients.recipient_type IS '수신자 유형 (TO, CC, BCC)';
COMMENT ON COLUMN email_recipients.recipient_name IS '수신자 이름';
COMMENT ON COLUMN email_recipients.recipient_email IS '수신자 이메일';
COMMENT ON COLUMN email_recipients.created_at IS '생성일시';
COMMENT ON COLUMN email_recipients.updated_at IS '수정일시';


-- EMAIL_ANALYSIS
CREATE TABLE email_analysis (
    id VARCHAR(20) NOT NULL,
    email_id VARCHAR(20) NOT NULL,
    analysis_version INT NOT NULL DEFAULT 1,
    is_latest BOOLEAN NOT NULL DEFAULT TRUE,
    model_name VARCHAR(100),
    prompt_version VARCHAR(50),
    short_summary VARCHAR(1000),
    detailed_summary TEXT,
    category VARCHAR(50),
    priority_level VARCHAR(10),
    importance_score DECIMAL(5,2),
    urgency_score DECIMAL(5,2),
    confidence_score DECIMAL(5,2),
    needs_reply BOOLEAN,
    has_deadline BOOLEAN,
    deadline_at TIMESTAMP,
    suggested_action VARCHAR(255),
    reasoning TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'COMPLETED',
    analyzed_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE email_analysis IS '메일 분석';
COMMENT ON COLUMN email_analysis.id IS '메일 분석 ID';
COMMENT ON COLUMN email_analysis.email_id IS '메일 ID';
COMMENT ON COLUMN email_analysis.analysis_version IS '분석 버전';
COMMENT ON COLUMN email_analysis.is_latest IS '최신 분석 여부';
COMMENT ON COLUMN email_analysis.model_name IS '모델명';
COMMENT ON COLUMN email_analysis.prompt_version IS '프롬프트 버전';
COMMENT ON COLUMN email_analysis.short_summary IS '한 줄 요약';
COMMENT ON COLUMN email_analysis.detailed_summary IS '상세 요약';
COMMENT ON COLUMN email_analysis.category IS '메일 카테고리';
COMMENT ON COLUMN email_analysis.priority_level IS '우선순위';
COMMENT ON COLUMN email_analysis.importance_score IS '중요도 점수';
COMMENT ON COLUMN email_analysis.urgency_score IS '긴급도 점수';
COMMENT ON COLUMN email_analysis.confidence_score IS '신뢰도 점수';
COMMENT ON COLUMN email_analysis.needs_reply IS '회신 필요 여부';
COMMENT ON COLUMN email_analysis.has_deadline IS '마감 존재 여부';
COMMENT ON COLUMN email_analysis.deadline_at IS '마감 일시';
COMMENT ON COLUMN email_analysis.suggested_action IS '추천 액션';
COMMENT ON COLUMN email_analysis.reasoning IS '판단 사유';
COMMENT ON COLUMN email_analysis.status IS '분석 상태';
COMMENT ON COLUMN email_analysis.analyzed_at IS '분석 일시';
COMMENT ON COLUMN email_analysis.created_at IS '생성일시';
COMMENT ON COLUMN email_analysis.updated_at IS '수정일시';


-- EMAIL_ACTION_ITEMS
CREATE TABLE email_action_items (
    id VARCHAR(20) NOT NULL,
    analysis_id VARCHAR(20) NOT NULL,
    action_text VARCHAR(500) NOT NULL,
    action_type VARCHAR(50),
    priority_level VARCHAR(10),
    due_at TIMESTAMP,
    is_completed BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE email_action_items IS '메일 액션 항목';
COMMENT ON COLUMN email_action_items.id IS '액션 항목 ID';
COMMENT ON COLUMN email_action_items.analysis_id IS '분석 ID';
COMMENT ON COLUMN email_action_items.action_text IS '액션 내용';
COMMENT ON COLUMN email_action_items.action_type IS '액션 유형';
COMMENT ON COLUMN email_action_items.priority_level IS '우선순위';
COMMENT ON COLUMN email_action_items.due_at IS '마감 일시';
COMMENT ON COLUMN email_action_items.is_completed IS '완료 여부';
COMMENT ON COLUMN email_action_items.created_at IS '생성일시';
COMMENT ON COLUMN email_action_items.updated_at IS '수정일시';


-- ANALYSIS_JOBS
CREATE TABLE analysis_jobs (
    id VARCHAR(20) NOT NULL,
    email_id VARCHAR(20) NOT NULL,
    job_type VARCHAR(50) NOT NULL DEFAULT 'EMAIL_ANALYSIS',
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    priority INT NOT NULL DEFAULT 5,
    retry_count INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    worker_id VARCHAR(100),
    error_message TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE analysis_jobs IS '메일 분석 작업';
COMMENT ON COLUMN analysis_jobs.id IS '분석 작업 ID';
COMMENT ON COLUMN analysis_jobs.email_id IS '메일 ID';
COMMENT ON COLUMN analysis_jobs.job_type IS '작업 유형';
COMMENT ON COLUMN analysis_jobs.status IS '작업 상태';
COMMENT ON COLUMN analysis_jobs.priority IS '작업 우선순위';
COMMENT ON COLUMN analysis_jobs.retry_count IS '재시도 횟수';
COMMENT ON COLUMN analysis_jobs.max_retries IS '최대 재시도 횟수';
COMMENT ON COLUMN analysis_jobs.worker_id IS '처리 worker';
COMMENT ON COLUMN analysis_jobs.error_message IS '오류 메시지';
COMMENT ON COLUMN analysis_jobs.started_at IS '작업 시작 시각';
COMMENT ON COLUMN analysis_jobs.completed_at IS '작업 완료 시각';
COMMENT ON COLUMN analysis_jobs.created_at IS '생성일시';
COMMENT ON COLUMN analysis_jobs.updated_at IS '수정일시';


-- LABELS
CREATE TABLE labels (
    id VARCHAR(20) NOT NULL,
    label_name VARCHAR(100) NOT NULL,
    label_code VARCHAR(50) NOT NULL,
    label_type VARCHAR(50),
    color VARCHAR(20),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE labels IS '메일 라벨';
COMMENT ON COLUMN labels.id IS '라벨 ID';
COMMENT ON COLUMN labels.label_name IS '라벨명';
COMMENT ON COLUMN labels.label_code IS '라벨 코드';
COMMENT ON COLUMN labels.label_type IS '라벨 유형';
COMMENT ON COLUMN labels.color IS '라벨 색상';
COMMENT ON COLUMN labels.created_at IS '생성일시';
COMMENT ON COLUMN labels.updated_at IS '수정일시';


-- EMAIL_LABELS
CREATE TABLE email_labels (
    id VARCHAR(20) NOT NULL,
    email_id VARCHAR(20) NOT NULL,
    label_id VARCHAR(20) NOT NULL,
    confidence_score DECIMAL(5,2),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id)
);

COMMENT ON TABLE email_labels IS '메일 라벨 매핑';
COMMENT ON COLUMN email_labels.id IS '메일 라벨 ID';
COMMENT ON COLUMN email_labels.email_id IS '메일 ID';
COMMENT ON COLUMN email_labels.label_id IS '라벨 ID';
COMMENT ON COLUMN email_labels.confidence_score IS '신뢰도 점수';
COMMENT ON COLUMN email_labels.created_at IS '생성일시';
COMMENT ON COLUMN email_labels.updated_at IS '수정일시';


-- =========================================================
-- DUMMY DATA
-- ID FORMAT: PREFIX_YYMMDD_RANDOM6
-- =========================================================

-- USERS (30)
INSERT INTO users (id, display_name, primary_email, status, last_login_at)
SELECT
    CONCAT(
        'USR_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(gs::text || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    CONCAT('홍길동', gs) AS display_name,
    CONCAT('user', gs, '@test.com') AS primary_email,
    'ACTIVE' AS status,
    NOW() AS last_login_at
FROM generate_series(1, 30) AS gs;


-- MAIL_ACCOUNTS (users 1:1)
INSERT INTO mail_accounts (
    id, user_id, provider, provider_account_id, account_email, account_name, is_primary, sync_enabled, sync_status
)
SELECT
    CONCAT(
        'MAC_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(u.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    u.id AS user_id,
    'GOOGLE' AS provider,
    CONCAT('google_', u.id) AS provider_account_id,
    u.primary_email AS account_email,
    u.display_name AS account_name,
    TRUE AS is_primary,
    TRUE AS sync_enabled,
    'ACTIVE' AS sync_status
FROM users u;


-- EMAILS (각 계정당 3개)
INSERT INTO emails (
    id, mail_account_id, external_message_id, subject, body_text, from_name, from_email, received_at, is_read
)
SELECT
    CONCAT(
        'EML_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(m.id || tpl.seq::text || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    m.id AS mail_account_id,
    CONCAT('MSG_', m.id, '_', tpl.seq) AS external_message_id,
    tpl.subject,
    tpl.body_text,
    tpl.from_name,
    tpl.from_email,
    NOW() AS received_at,
    tpl.is_read
FROM mail_accounts m
CROSS JOIN (
    VALUES
        (1, '업무 요청 메일', '금일 중 확인 부탁드립니다.', '김부장', 'boss@test.com', FALSE),
        (2, '회의 일정 안내', '내일 오전 10시 회의 예정입니다.', '김과장', 'manager@test.com', TRUE),
        (3, '보고 요청', '주간 보고서 제출 바랍니다.', '이팀장', 'leader@test.com', FALSE)
) AS tpl(seq, subject, body_text, from_name, from_email, is_read);


-- EMAIL_RECIPIENTS
INSERT INTO email_recipients (id, email_id, recipient_type, recipient_email)
SELECT
    CONCAT(
        'ERC_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(e.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    e.id AS email_id,
    'TO' AS recipient_type,
    'me@test.com' AS recipient_email
FROM emails e;


-- EMAIL_ANALYSIS
INSERT INTO email_analysis (
    id, email_id, analysis_version, is_latest, short_summary, category, priority_level, needs_reply, status
)
SELECT
    CONCAT(
        'ANL_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(e.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    e.id AS email_id,
    1 AS analysis_version,
    TRUE AS is_latest,
    '업무 관련 요청 메일' AS short_summary,
    'REQUEST' AS category,
    'P2' AS priority_level,
    TRUE AS needs_reply,
    'COMPLETED' AS status
FROM emails e;


-- EMAIL_ACTION_ITEMS
INSERT INTO email_action_items (id, analysis_id, action_text, action_type)
SELECT
    CONCAT(
        'ACT_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(a.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    a.id AS analysis_id,
    '메일 내용 확인 및 회신' AS action_text,
    'REPLY' AS action_type
FROM email_analysis a;


-- LABELS
INSERT INTO labels (id, label_name, label_code)
SELECT
    CONCAT(
        'LBL_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(v.label_code || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    v.label_name,
    v.label_code
FROM (
    VALUES
        ('긴급', 'URGENT'),
        ('요청', 'REQUEST'),
        ('보고', 'REPORT'),
        ('회의', 'MEETING')
) AS v(label_name, label_code);


-- EMAIL_LABELS (REQUEST 라벨 매핑)
INSERT INTO email_labels (id, email_id, label_id)
SELECT
    CONCAT(
        'ELB_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(e.id || l.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    e.id AS email_id,
    l.id AS label_id
FROM emails e
JOIN labels l ON l.label_code = 'REQUEST';


-- ANALYSIS_JOBS
INSERT INTO analysis_jobs (id, email_id, job_type, status)
SELECT
    CONCAT(
        'JOB_', TO_CHAR(CURRENT_DATE, 'YYMMDD'), '_',
        UPPER(SUBSTRING(MD5(e.id || CLOCK_TIMESTAMP()::text || RANDOM()::text) FROM 1 FOR 6))
    ) AS id,
    e.id AS email_id,
    'EMAIL_ANALYSIS' AS job_type,
    'COMPLETED' AS status
FROM emails e;
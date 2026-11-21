BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> afe4b7884774

CREATE TABLE users (
    id UUID NOT NULL, 
    email VARCHAR(320) NOT NULL, 
    full_name VARCHAR(255) NOT NULL, 
    password_hash VARCHAR(255) NOT NULL, 
    role VARCHAR(20) DEFAULT 'user' NOT NULL, 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    CONSTRAINT pk_users PRIMARY KEY (id), 
    CONSTRAINT uq_users_email UNIQUE (email)
);

INSERT INTO alembic_version (version_num) VALUES ('afe4b7884774') RETURNING alembic_version.version_num;

-- Running upgrade afe4b7884774 -> a4bbd3391e7a

CREATE TABLE request_types (
    id UUID NOT NULL, 
    code VARCHAR(50) NOT NULL, 
    name VARCHAR(100) NOT NULL, 
    description TEXT, 
    requires_amount BOOLEAN DEFAULT false NOT NULL, 
    approval_threshold NUMERIC(12, 2), 
    is_active BOOLEAN DEFAULT true NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    CONSTRAINT pk_request_types PRIMARY KEY (id), 
    CONSTRAINT ck_request_types_code_format CHECK (code ~ '^[a-z][a-z0-9_]*$'), 
    CONSTRAINT ck_request_types_approval_threshold_non_negative CHECK (approval_threshold IS NULL OR approval_threshold >= 0), 
    CONSTRAINT ck_request_types_threshold_requires_amount CHECK (approval_threshold IS NULL OR requires_amount=True), 
    CONSTRAINT uq_request_types_code UNIQUE (code)
);

UPDATE alembic_version SET version_num='a4bbd3391e7a' WHERE alembic_version.version_num = 'afe4b7884774';

-- Running upgrade a4bbd3391e7a -> afce36a77d9c

INSERT INTO request_types (id, code, name, requires_amount, approval_threshold) VALUES ('9aef93c6-87a8-4618-9d71-45310b122c97', 'expense', 'Trošak', true, 50000.00);

INSERT INTO request_types (id, code, name, requires_amount, approval_threshold) VALUES ('f9ff38b8-1d2a-432f-8382-0970285572cd', 'equipment', 'Oprema', true, 100000.00);

INSERT INTO request_types (id, code, name, requires_amount, approval_threshold) VALUES ('d626b200-4302-4812-9ff5-ae879332d8ec', 'access', 'Pristup sistemu', false, NULL);

UPDATE alembic_version SET version_num='afce36a77d9c' WHERE alembic_version.version_num = 'a4bbd3391e7a';

-- Running upgrade afce36a77d9c -> 03557d58337d

CREATE TABLE requests (
    id UUID NOT NULL, 
    requester_id UUID NOT NULL, 
    request_type_id UUID NOT NULL, 
    title VARCHAR(200) NOT NULL, 
    description TEXT NOT NULL, 
    amount NUMERIC(12, 2), 
    currency VARCHAR(3), 
    status VARCHAR(20) DEFAULT 'received' NOT NULL, 
    decided_at TIMESTAMP WITH TIME ZONE, 
    decided_by_id UUID, 
    decision_reason TEXT, 
    idempotency_key VARCHAR(64), 
    version INTEGER DEFAULT 1 NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    CONSTRAINT pk_requests PRIMARY KEY (id), 
    CONSTRAINT ck_requests_currency_format CHECK (currency IS NULL OR currency ~ '^[A-Z]{3}$'), 
    CONSTRAINT ck_requests_decision_has_timestamp CHECK (status NOT IN ('approved', 'rejected') OR decided_at IS NOT NULL), 
    CONSTRAINT ck_requests_amount_currency_together CHECK ((currency IS NULL) = (amount IS NULL)), 
    CONSTRAINT ck_requests_amount_positive CHECK (amount IS NULL OR amount > 0), 
    CONSTRAINT ck_requests_title_not_blank CHECK (length(trim(title)) > 0), 
    CONSTRAINT fk_requests_decided_by_id_users FOREIGN KEY(decided_by_id) REFERENCES users (id) ON DELETE RESTRICT, 
    CONSTRAINT fk_requests_request_type_id_request_types FOREIGN KEY(request_type_id) REFERENCES request_types (id) ON DELETE RESTRICT, 
    CONSTRAINT fk_requests_requester_id_users FOREIGN KEY(requester_id) REFERENCES users (id) ON DELETE RESTRICT, 
    CONSTRAINT uq_requests_requester_id_idempotency_key UNIQUE (requester_id, idempotency_key)
);

CREATE INDEX ix_requests_requester_id_created_at ON requests (requester_id, created_at);

CREATE INDEX ix_requests_status_created_at ON requests (status, created_at);

UPDATE alembic_version SET version_num='03557d58337d' WHERE alembic_version.version_num = 'afce36a77d9c';

COMMIT;


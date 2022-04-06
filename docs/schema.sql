CREATE TYPE enum_task_state AS ENUM (
    'created',
    'pending',
    'running',
    'succeed',
    'warning',
    'failure',
    'timeout'
);

create table if not exists "sys_state" (
    k CHARACTER varying(100) not null,
    v CHARACTER varying(100) not null,
    ctime timestamp with time zone default now(),
    mtime timestamp with time zone,
    PRIMARY key(k)
);

create table if not exists "task" (
    id uuid PRIMARY KEY not null,
    type character varying(50) not null,
    creator_id uuid not null,
    priority smallint not null default 0,
    detail jsonb,
    settings jsonb,
    runner character varying(50),
    state enum_task_state not null,
    result jsonb,
    error jsonb,
    stime timestamp(6) with time zone,
    etime timestamp(6) with time zone,
    ctime timestamp(6) with time zone default now()
);
create index if not exists "idx_task_order" on "task" ("priority" desc nulls last, id asc);
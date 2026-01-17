# Async Job Processing Platform

![Workflow 1](./Diagrams/Workflow_Iter_1.png)

<B> NOTE: </B> FAILED JOB DATABASE -> JUST SET THE STATE TO "FAILED" IN THE MAIN POSTGRES DB

## DB SCHEMA
```sql
 id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  job_type text NOT NULL,
  payload jsonb NOT NULL,
  status text NOT NULL DEFAULT 'PENDING',
  attempts integer NOT NULL DEFAULT 0,
  max_attempts integer NOT NULL DEFAULT 5,
  visibility_deadline timestamptz NULL,
  last_error text NULL,
  result_url text NULL,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
```
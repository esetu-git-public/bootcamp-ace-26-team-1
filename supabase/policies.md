# Supabase Row Level Security (RLS) Policies

These are the recommended policies once you point the app at a real Supabase
project (set `SUPABASE_URL` / `SUPABASE_KEY` in `.env`). Run the SQL below in
the Supabase SQL editor after creating the tables described in
`supabase/database.py`'s `init_local_db()` (mirror the same schema in
Postgres).

## Tables

- `users` — profile metadata (id references `auth.users.id`)
- `patients` — patient records
- `predictions` — ML prediction history
- `audit_logs` — action audit trail

## Enable RLS

```sql
alter table users enable row level security;
alter table patients enable row level security;
alter table predictions enable row level security;
alter table audit_logs enable row level security;
```

## Policies

```sql
-- Users can read their own profile; admins can read all
create policy "Users read own profile"
on users for select
using (auth.uid() = id);

-- Any authenticated clinician can read/write patient records
create policy "Authenticated read patients"
on patients for select
to authenticated
using (true);

create policy "Authenticated insert patients"
on patients for insert
to authenticated
with check (true);

-- Predictions: authenticated users can insert and read
create policy "Authenticated read predictions"
on predictions for select
to authenticated
using (true);

create policy "Authenticated insert predictions"
on predictions for insert
to authenticated
with check (true);

-- Audit logs: read-only for admins, insert-only for the service role
create policy "Admins read audit logs"
on audit_logs for select
to authenticated
using (auth.jwt() ->> 'role' = 'admin');
```

## Storage bucket

Create a bucket named `uploads` (private) and add a policy allowing
authenticated users to upload/read their own files.

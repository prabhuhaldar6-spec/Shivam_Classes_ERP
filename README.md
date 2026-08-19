# Coaching ERP — Starter App

A working starting point: login with roles (admin/teacher/student/parent),
attendance, homework upload, and dashboards. Follow the setup guide in chat
alongside this file.

## 1. Create these tables in Supabase

Go to your Supabase project → **SQL Editor** → paste this → **Run**.

> Already ran this before? Just run these two lines instead, to add the new `class` columns:
> ```sql
> alter table attendance add column class text;
> alter table homework add column class text;
> ```

```sql
create table profiles (
  id uuid references auth.users primary key,
  full_name text,
  role text check (role in ('admin','teacher','student','parent'))
);

create table students (
  id bigint generated always as identity primary key,
  full_name text,
  class text,
  parent_id uuid references profiles(id)
);

create table attendance (
  id bigint generated always as identity primary key,
  student_id bigint references students(id),
  class text,
  date date,
  status text
);

create table homework (
  id bigint generated always as identity primary key,
  title text,
  class text,
  file_url text
);

create table fees (
  id bigint generated always as identity primary key,
  student_id bigint references students(id),
  amount numeric,
  month text,
  paid_on date,
  receipt_url text
);
```

## 2. Create a Storage bucket

Supabase dashboard → **Storage** → New bucket → name it `homework` → make it **public**
(for this starter; tighten later with policies).

## 3. Create your first admin login

Supabase dashboard → **Authentication** → Add user → enter your own email/password.
Then in **Table Editor → profiles**, add a row with that same user's `id`,
your name, and `role = admin`.

## 4. Fill in secrets.toml

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste in
your Supabase URL and anon key (Project Settings → API).

## 5. Run it

```
pip install -r requirements.txt
streamlit run app.py
```

# Coaching ERP — Starter App

A working starting point: login with roles (admin/teacher/student/parent),
attendance, homework upload, and dashboards. Follow the setup guide in chat
alongside this file.

## 1. Create these tables in Supabase

Go to your Supabase project → **SQL Editor** → paste this → **Run**.

> Already ran this before? Just run these lines instead, to add the new columns:
> ```sql
> alter table attendance add column class text;
> alter table homework add column class text;
> alter table students add column telegram_chat_id text;
> alter table students add column total_fee numeric default 0;
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
  parent_id uuid references profiles(id),
  telegram_chat_id text,
  total_fee numeric default 0
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

## 4. Create a Telegram bot (for fee receipts and reminders)

1. Open Telegram, search for **@BotFather**, and start a chat with it.
2. Send `/newbot`, give it a name (e.g. "Shivam Classes ERP"), and a username ending in `bot` (e.g. `shivam_classes_erp_bot`).
3. BotFather replies with a **token** — copy it, you'll paste it into `secrets.toml`.
4. Tell your parents/students: search for your bot's username on Telegram, open a chat, and send `/start`. This is required once — Telegram only allows a bot to message someone who has messaged it first.
5. In the app's Admin Dashboard, use the "Link Telegram" tab to match each `/start` message to the right student.

## 5. Fill in secrets.toml

Copy `.streamlit/secrets.toml.example` to `.streamlit/secrets.toml` and paste in
your Supabase URL and anon key (Project Settings → API).

## 6. Run it

```
pip install -r requirements.txt
streamlit run app.py
```

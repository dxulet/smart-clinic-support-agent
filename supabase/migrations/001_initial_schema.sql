-- Enable the pgvector extension to work with embedding vectors
create extension if not exists vector;

-- Create doctors table
create table doctors (
    id uuid primary key default uuid_generate_v4(),
    name text not null,
    specialization text not null,
    contact_number text,
    schedule jsonb,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert sample data for doctors
insert into doctors (name, specialization, contact_number, schedule)
values 
    ('John Smith', 'General Medicine', '+1 (555) 111-2222', '{"monday": "9:00-17:00", "tuesday": "9:00-17:00", "wednesday": "9:00-17:00"}'),
    ('Sarah Johnson', 'Pediatrics', '+1 (555) 222-3333', '{"monday": "10:00-18:00", "thursday": "10:00-18:00", "friday": "10:00-18:00"}'),
    ('Michael Chen', 'Cardiology', '+1 (555) 333-4444', '{"tuesday": "9:00-17:00", "thursday": "9:00-17:00", "friday": "9:00-17:00"}');

-- Enable pgvector extension
create extension if not exists vector;

-- Create clinic_info table
create table clinic_info (
    id uuid primary key default uuid_generate_v4(),
    address text not null,
    phone text not null,
    operating_hours text not null,
    created_at timestamp with time zone default timezone('utc'::text, now()) not null
);

-- Insert sample data for clinic_info
insert into clinic_info (address, phone, operating_hours)
values (
    'Улица Герольда Бельгера, 71, Уральск',
    '+7‒771‒626‒70‒70',
    'Monday-Friday: 8:00 AM - 8:00 PM, Saturday: 9:00 AM - 5:00 PM, Sunday: Closed'
);

-- Create services table
create table if not exists services (
  id bigint generated always as identity primary key,
  content text not null,
  specialty text not null,
  price numeric(10,2) not null,
  category text not null,
  embedding vector(1536),
  created_at timestamptz default now()
);

-- Create a function to match services
create or replace function match_services (
  query_embedding vector(1536),
  match_count int default 5
) returns table (
  id bigint,
  content text,
  specialty text,
  price numeric(10,2),
  category text,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    services.id,
    services.content,
    services.specialty,
    services.price,
    services.category,
    1 - (services.embedding <=> query_embedding) as similarity
  from services
  order by services.embedding <=> query_embedding
  limit match_count;
end;
$$;
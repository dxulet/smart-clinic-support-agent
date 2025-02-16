AI WhatsApp Clinic Support Agent – System Design Documentation
1. Overview
1.1 Purpose
Build an AI-driven WhatsApp customer support agent for the clinic. The initial MVP (Phase #1) will respond to basic queries (e.g., “How many doctors do you have?”, “What is your address?”, “Doctor contact numbers?”). Later phases will expand the agent’s capabilities (e.g., multi-turn conversations, appointment guidance, personalized responses) based on more refined data and business logic.

1.2 Scope and Phases
Phase #1 (MVP):

Answer static, predefined queries about clinic information.
Use the clinic’s structured data (doctors, contacts, location, operating hours) stored in Supabase.
Employ Supabase’s pgvector extension (via a Python client library such as vecs) to support any future semantic or similarity search needs.
Phase #2:

Fine-tune the agent to support specific, multi-step instructions (e.g., “I need a dermatologist for tomorrow afternoon”).
Add context retention for multi-turn conversations.
Integrate simple appointment guidance and escalation logic to human agents if needed.
Phase #3 and Beyond:

Extend the solution to additional channels (web chat, SMS, voice).
Implement real-time appointment booking by integrating with external scheduling systems.
Add proactive messaging, analytics dashboards, and multi-language support.
1.3 Objectives
Efficiency: Reduce workload on human staff by automating routine information queries.
Availability: Provide 24/7 support via WhatsApp.
Scalability: Build a foundation that can grow with additional features and increased query volume.
Accuracy: Ensure responses are consistently drawn from up-to-date, curated clinic data.
2. System Architecture Overview
2.1 High-Level Components
WhatsApp Business API Provider:
Manages inbound and outbound WhatsApp messages (e.g., via Infobip, Twilio, or Social Intents).

Integration Gateway:
Receives incoming messages from WhatsApp and routes them to the backend.

Backend Server (Python):
Implements business logic, integrates with the AI engine, and performs database operations. Built using FastAPI for modern async support and RESTful APIs.

AI Chatbot Engine:
Powered by OpenAI’s ChatGPT API to interpret natural language queries and generate responses according to pre-defined prompts and clinic data.

Supabase (Database & Vector Store):

Relational Database: Stores clinic data (doctor details, contact numbers, location, operating hours, etc.) in structured tables.
Vector Store via pgvector: Using Supabase’s PGVector support (managed through the vecs Python library) for future retrieval-augmented generation (RAG) capabilities.
Cache Layer:
Optionally use Redis to cache frequently requested information and improve response times.

Monitoring & Logging:
Track application performance, errors, and user interactions via cloud monitoring (e.g., CloudWatch, DataDog).

Admin Dashboard:
Provides configuration, manual overrides, and system monitoring capabilities.

2.2 Data Flow (MVP)
User Interaction:
The customer sends a WhatsApp message (e.g., “What is your address?”).

Message Routing:
The WhatsApp Business API forwards the message to the Integration Gateway.

Backend Processing:
The FastAPI-based backend (written in Python) receives the message, determines the intent, and retrieves the relevant static clinic data from Supabase.

Data Retrieval:
The backend queries Supabase via the supabase-py client for structured clinic data. For future similarity-based queries, the vector store (managed with the vecs library) can be used.

Response Generation:
The AI Chatbot Engine (ChatGPT API) or simple rule-based logic formats the response, which is then sent back to the customer over WhatsApp.

For more details on using Supabase with Python, see the official Supabase Python Docs and the Vecs documentation.

3. Technical Stack
3.1 Programming Language and Framework
Python:
The entire backend is implemented in Python.
FastAPI:
A modern, async-friendly web framework for building RESTful APIs.
3.2 Supabase Integration
Relational Data:
Use the supabase-py client library to connect to the Supabase PostgreSQL database for CRUD operations on clinic data.

Vector Store:
Utilize the pgvector extension through the vecs Python library. This will allow storing and querying vector embeddings—useful for future semantic search or context augmentation.

Example initialization:

python
Copy
from supabase import create_client
import vecs

SUPABASE_URL = "https://your-supabase-url"
SUPABASE_KEY = "your-supabase-api-key"

# Initialize Supabase client for structured data
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Create a vector store client using vecs
DB_CONNECTION = "postgresql://user:password@host:port/dbname"
vx = vecs.create_client(DB_CONNECTION)
docs = vx.get_or_create_collection(name="clinic_info", dimension=512)  # dimension adjusted as needed
See examples in the Supabase Vecs GitHub repo and Supabase Docs.

3.3 AI and NLP
ChatGPT API (OpenAI):
Leverage OpenAI’s ChatGPT API for generating natural language responses when necessary.
Rule-based Handling (MVP):
For Phase #1, responses can be generated directly from the static data without heavy NLP processing.
3.4 Caching and Monitoring
Redis (Optional):
Implement a Redis cache for high-traffic queries.
Monitoring Tools:
Use tools such as AWS CloudWatch or DataDog for logging, performance monitoring, and alerting.
3.5 Deployment and Infrastructure
Cloud Platform:
Deploy the Python FastAPI backend on AWS, GCP, or Azure.
Containerization:
Dockerize the application and orchestrate using Kubernetes if needed.
CI/CD:
Implement automated pipelines using GitHub Actions or similar tools.
4. MVP (Phase #1) – Clinic Information Agent
4.1 Functional Requirements
Provide answers for basic clinic information queries (number of doctors, contact numbers, clinic location, operating hours).
Use a preconfigured knowledge base stored in Supabase.
Respond quickly with minimal latency.
4.2 Backend Flow (Python/FastAPI)
Endpoint:
An endpoint (e.g., /query) that receives a WhatsApp message payload.

Processing:
The endpoint parses the message, identifies keywords, and maps them to queries on the clinic’s static data.

Data Access:
Use supabase-py to query the relevant table (e.g., clinic_info).
Example:

python
Copy
response = supabase.table("clinic_info").select("*").execute()
Response Delivery:
Format the response (e.g., “Our clinic is located at 1234 Health Ave, Suite 101…”) and return it to the WhatsApp API for sending to the user.

4.3 Data Storage
Clinic Data:
Store structured data in tables such as:

doctors (columns: id, name, specialization, contact_number, schedule)
clinic_info (columns: id, address, phone, operating_hours)
Vector Store Preparation:
Prepare the vector store (even if unused in MVP) for future phases. Later, you can store embeddings for FAQ or conversation context.

Example:

python
Copy
# Inserting static clinic information as vectors is optional in Phase #1.
docs.upsert(
    records=[
        ("clinic_address", [0.0]*512, {"address": "1234 Health Ave, Suite 101"}),
        # Other records as needed
    ]
)

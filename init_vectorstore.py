from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Print environment variables for debugging
print("SUPABASE_URL:", os.getenv("SUPABASE_URL"))
print("AZURE_OPENAI_ENDPOINT:", os.getenv("AZURE_OPENAI_ENDPOINT"))

# Initialize the rest only if we have proper URLs
if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY"):
    from langchain_openai import AzureOpenAIEmbeddings
    from langchain_community.vectorstores.supabase import SupabaseVectorStore
    from supabase import create_client

    # Initialize Azure OpenAI embeddings
    embeddings = AzureOpenAIEmbeddings(
        azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
        azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    # Initialize Supabase client
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )

    # Initialize vector store
    vector_store = SupabaseVectorStore(
        embedding=embeddings,
        client=supabase,
        table_name="services",
        query_name="match_services"
    )

    # Sample clinic information to vectorize
    clinic_docs = [
        "Our clinic is located at 123 Medical Center Drive, Healthcare City. We provide comprehensive medical care for all ages.",
        "Operating hours are Monday through Friday from 9:00 AM to 6:00 PM, Saturday from 9:00 AM to 2:00 PM, and we are closed on Sundays.",
        "Contact us at +1 (555) 123-4567 for appointments and general inquiries.",
        "Dr. John Smith specializes in General Medicine and is available Monday through Wednesday.",
        "Dr. Sarah Johnson is our pediatric specialist, available Monday, Thursday, and Friday.",
        "Dr. Michael Chen, our cardiologist, sees patients on Tuesday, Thursday, and Friday."
    ]

    # Add documents to vector store
    try:
        vector_store.add_texts(texts=clinic_docs)
        print("Successfully added clinic information to vector store")
    except Exception as e:
        print(f"Error adding documents: {e}")
else:
    print("Error: Missing or invalid environment variables. Please check your .env file.")
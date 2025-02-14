from fastapi import FastAPI, Request, HTTPException
from supabase import create_client
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore

# Load environment variables
load_dotenv()
app = FastAPI(title="Clinic Support Agent")

# Initialize Supabase client
try:
    supabase = create_client(
        os.getenv("SUPABASE_URL"),
        os.getenv("SUPABASE_KEY")
    )
except Exception as e:
    print(f"Failed to initialize Supabase client: {e}")
    raise

# Initialize Azure OpenAI embeddings
embeddings = AzureOpenAIEmbeddings(
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    api_key=os.getenv("AZURE_OPENAI_API_KEY")
)

# Initialize vector store
vector_store = SupabaseVectorStore(
    embedding=embeddings,
    client=supabase,
    table_name="services",
    query_name="match_services"
)

@app.post("/query")
async def query_handler(request: Request):
    try:
        data = await request.json()
        query_text = data.get("message", "")
        
        # Perform similarity search
        results = vector_store.similarity_search(
            query_text,
            k=2  # Get top 2 most relevant results
        )
        
        if results:
            # Combine the relevant results into a coherent response
            response_text = " ".join([doc.page_content for doc in results])
            return {"response": response_text}
        
        return {"response": "I apologize, but I couldn't find relevant information for your query. Please try asking about our clinic's services, doctors, location, or operating hours."}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
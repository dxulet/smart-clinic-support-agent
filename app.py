from fastapi import FastAPI, Request, HTTPException
from supabase import create_client
import os
from dotenv import load_dotenv
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from typing import List, Dict, Any
from openai import AzureOpenAI

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

async def create_embedding(query_text: str) -> List[float]:
    """
    Create an embedding vector for the input query text.
    
    Args:
        query_text (str): The input text to create an embedding for
        
    Returns:
        List[float]: The embedding vector
    """
    try:
        query_embedding = embeddings.embed_query(query_text)
        return query_embedding
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating embedding: {str(e)}")

async def find_nearest_match(query_embedding: List[float], k: int = 5) -> List[Dict[str, Any]]:
    """
    Find the nearest matches in the vector store for a given embedding.
    
    Args:
        query_embedding (List[float]): The embedding vector to search with
        k (int): Number of results to return
        
    Returns:
        List[Dict]: List of matching documents with their data from Supabase
    """
    try:
        # Execute raw query to get all fields
        response = supabase.rpc(
            'match_services',
            {'query_embedding': query_embedding, 'match_count': k}
        ).execute()
        
        if not response.data:
            return []
            
        matches = []
        for item in response.data:
            match_data = {
                "id": item.get("id"),
                "content": item.get("content"),
                "specialty": item.get("specialty"),
                "price": item.get("price"),
                "category": item.get("category"),
                "similarity": item.get("similarity")
            }
            matches.append(match_data)
            
        return matches
    except Exception as e:
        print(f"Error details: {str(e)}")  # Add debugging
        raise HTTPException(status_code=500, detail=f"Error finding matches: {str(e)}")

async def get_clinic_info() -> Dict[str, Any]:
    """Get clinic information"""
    try:
        response = supabase.table("clinic_info").select("*").limit(1).execute()
        return response.data[0] if response.data else {}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting clinic info: {str(e)}")

async def get_chat_completion(query: str, context: List[Dict[str, Any]], clinic_info: Dict[str, Any] = None) -> str:
    """
    Get a chat completion response using the GPT-4 model.
    
    Args:
        query (str): The user's query
        context (List[Dict]): List of relevant service records
        clinic_info (Dict): General clinic information
        
    Returns:
        str: The model's response
    """
    try:
        client = AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_CHAT_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_CHAT_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_CHAT_ENDPOINT")
        )

        context_texts = []
        
        # Add clinic info if available
        if clinic_info:
            clinic_text = (
                f"Clinic Information:\n"
                f"Address: {clinic_info.get('address', 'N/A')}\n"
                f"Phone: {clinic_info.get('phone', 'N/A')}\n"
                f"Operating Hours: {clinic_info.get('operating_hours', 'N/A')}"
            )
            context_texts.append(clinic_text)
        
        # Add services info if available
        for doc in context:
            service_info = (
                f"Service Information:\n"
                f"Service: {doc.get('content', 'N/A')}\n"
                f"Specialty: {doc.get('specialty', 'N/A')}\n"
                f"Price: {doc.get('price', 'N/A')} tenge\n"
                f"Category: {doc.get('category', 'N/A')}"
            )
            context_texts.append(service_info)
        
        formatted_context = "\n\n".join(context_texts)
        
        system_message = """You are a helpful clinic assistant. Use the provided context to answer questions about the clinic, 
        its services, and general information. Be sure to include relevant details about services, specialties, 
        prices, schedules, and contact information when available. If the answer cannot be found in the context, politely suggest 
        contacting the clinic directly."""
        
        response = client.chat.completions.create(
            model=os.getenv("AZURE_OPENAI_CHAT_MODEL"),
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context:\n{formatted_context}\n\nQuestion: {query}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting chat completion: {str(e)}")

@app.post("/query")
async def query_handler(request: Request):
    try:
        data = await request.json()
        query_text = data.get("message", "")
        
        # Get clinic info for all queries
        clinic_info = await get_clinic_info()
        
        # For service-related queries, use vector search
        query_embedding = await create_embedding(query_text)
        matches = await find_nearest_match(query_embedding)
        
        # Get chat completion with all available context
        response_text = await get_chat_completion(query_text, matches, clinic_info)
        return {"response": response_text}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
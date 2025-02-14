from fastapi import FastAPI, Request, HTTPException
from supabase import create_client
import os
from dotenv import load_dotenv

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

# Initialize vector store in Supabase
try:
    # Enable vector extension if not already enabled
    supabase.postgrest.rpc('enable_vectors').execute()
except Exception as e:
    print(f"Note: Vector extension might already be enabled: {e}")

@app.post("/query")
async def query_handler(request: Request):
    try:
        data = await request.json()
        query_text = data.get("message", "").lower()

        # Basic keyword-based routing for MVP
        if "address" in query_text:
            response = supabase.table("clinic_info").select("address").execute()
            address = response.data[0]["address"] if response.data else "Address not available."
            return {"response": f"Our clinic is located at {address}"}
        
        elif "doctor" in query_text or "doctors" in query_text:
            response = supabase.table("doctors").select("*").execute()
            if response.data:
                doctors_count = len(response.data)
                doctors_list = [f"Dr. {doc['name']} ({doc['specialization']})" for doc in response.data]
                return {
                    "response": f"We have {doctors_count} doctors:\n" + "\n".join(doctors_list)
                }
            return {"response": "Information about doctors is not available at the moment."}
        
        elif "hours" in query_text or "timing" in query_text:
            response = supabase.table("clinic_info").select("operating_hours").execute()
            hours = response.data[0]["operating_hours"] if response.data else "Operating hours not available."
            return {"response": f"Our operating hours are: {hours}"}
        
        elif "contact" in query_text or "phone" in query_text:
            response = supabase.table("clinic_info").select("phone").execute()
            phone = response.data[0]["phone"] if response.data else "Contact number not available."
            return {"response": f"You can reach us at: {phone}"}

        return {"response": "I apologize, but I couldn't understand your query. Please ask about our address, doctors, operating hours, or contact information."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
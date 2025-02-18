from fastapi import FastAPI, Request, HTTPException
from models.query import QueryRequest, QueryResponse
from services.vector_service import VectorService
from services.ai_service import AIService
from utils.whatsapp_response import send_response, send_whatsapp_text_message

app = FastAPI(title="Clinic Support Agent")

# Initialize services
vector_service = VectorService()
ai_service = AIService()

@app.post("/query", response_model=QueryResponse)
async def query_handler(request: Request):
    try:
        data = await request.json()
        query = QueryRequest(message=data.get("message", ""))
        
        # Get clinic info
        clinic_info = await vector_service.get_clinic_info()
        
        # Get vector matches
        query_embedding = await vector_service.create_embedding(query.message)
        matches = await vector_service.find_nearest_match(query_embedding)
        
        # Get AI response
        response_text = await ai_service.get_chat_completion(query.message, matches, clinic_info)

        # Whatsapp Response
        send = await send_response(response_text)
        if not send:
            raise HTTPException(status_code=500, detail="Failed to send response to Whatsapp")

        return QueryResponse(response=response_text)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
from openai import AzureOpenAI
from typing import List, Dict, Any
from config.settings import get_settings
from models.query import ServiceMatch, ClinicInfo

class AIService:
    def __init__(self):
        settings = get_settings()
        self.client = AzureOpenAI(
            api_key=settings.azure_openai_chat_api_key,
            api_version=settings.azure_openai_chat_api_version,
            azure_endpoint=settings.azure_openai_chat_endpoint
        )
        self.model = settings.azure_openai_chat_model

    def _format_context(self, matches: List[ServiceMatch], clinic_info: ClinicInfo) -> str:
        context_texts = []
        
        clinic_text = (
            f"Clinic Information:\n"
            f"Address: {clinic_info.address}\n"
            f"Phone: {clinic_info.phone}\n"
            f"Operating Hours: {clinic_info.operating_hours}"
        )
        context_texts.append(clinic_text)
        
        for service in matches:
            service_info = (
                f"Service Information:\n"
                f"Service: {service.content}\n"
                f"Specialty: {service.specialty}\n"
                f"Price: {service.price} tenge\n"
                f"Category: {service.category}"
            )
            context_texts.append(service_info)
        
        return "\n\n".join(context_texts)

    async def get_chat_completion(self, query: str, matches: List[ServiceMatch], clinic_info: ClinicInfo) -> str:
        formatted_context = self._format_context(matches, clinic_info)
        
        system_message = """You are a helpful clinic assistant. Use the provided context to answer questions about the clinic, 
        its services, and general information. Be sure to include relevant details about services, specialties, 
        prices, schedules, and contact information when available. If the answer cannot be found in the context, politely suggest 
        contacting the clinic directly."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Context:\n{formatted_context}\n\nQuestion: {query}"}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return response.choices[0].message.content
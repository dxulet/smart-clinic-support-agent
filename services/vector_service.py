from supabase import create_client
from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores.supabase import SupabaseVectorStore
from typing import List, Dict, Any
from config.settings import get_settings
from models.query import ServiceMatch, ClinicInfo

class VectorService:
    def __init__(self):
        settings = get_settings()
        self.supabase = create_client(settings.supabase_url, settings.supabase_key)
        self.embeddings = AzureOpenAIEmbeddings(
            azure_deployment=settings.azure_openai_deployment_name,
            openai_api_version=settings.azure_openai_api_version,
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key
        )
        self.vector_store = SupabaseVectorStore(
            embedding=self.embeddings,
            client=self.supabase,
            table_name="services",
            query_name="match_services"
        )

    async def create_embedding(self, query_text: str) -> List[float]:
        return self.embeddings.embed_query(query_text)

    async def find_nearest_match(self, query_embedding: List[float], k: int = 5) -> List[ServiceMatch]:
        response = self.supabase.rpc(
            'match_services',
            {'query_embedding': query_embedding, 'match_count': k}
        ).execute()
        
        if not response.data:
            return []
            
        return [
            ServiceMatch(
                id=item.get("id"),
                content=item.get("content"),
                specialty=item.get("specialty"),
                price=item.get("price"),
                category=item.get("category"),
                similarity=item.get("similarity")
            )
            for item in response.data
        ]

    async def get_clinic_info(self) -> ClinicInfo:
        response = self.supabase.table("clinic_info").select("*").limit(1).execute()
        if not response.data:
            return ClinicInfo(address="N/A", phone="N/A", operating_hours="N/A")
        data = response.data[0]
        return ClinicInfo(**data)
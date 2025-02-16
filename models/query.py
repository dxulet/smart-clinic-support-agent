from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union

class QueryRequest(BaseModel):
    message: str

class ServiceMatch(BaseModel):
    id: Union[str, int]
    content: str
    specialty: str
    price: float
    category: str
    similarity: float

class ClinicInfo(BaseModel):
    address: str
    phone: str
    operating_hours: str

class QueryResponse(BaseModel):
    response: str
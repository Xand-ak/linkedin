from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional
import requests

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

def call_fastapi(search_type: str, params: dict):
    """Calls the correct FastAPI endpoint dynamically."""
    
    # Remove None values before making the request
    params = {k: v for k, v in params.items() if v is not None}
    
    response = requests.get(f"{FASTAPI_BASE_URL}/search/{search_type}", params=params)
    return response.json()

class CompanySearchInput(BaseModel):
    country: Optional[str] = Field(None)
    city: Optional[str] = Field(None)
    page_size: Optional[int] = Field(10)
    enrich_profiles: Optional[str] = Field("skip")

class PersonSearchInput(BaseModel):
    country: Optional[str] = Field(None)
    first_name: Optional[str] = Field(None)
    last_name: Optional[str] = Field(None)
    skills: Optional[str] = Field(None)
    company: Optional[str] = Field(None)

class JobSearchInput(BaseModel):
    job_type: Optional[str] = Field("anything")
    experience_level: Optional[str] = Field("anything")
    flexibility: Optional[str] = Field("anything")
    keyword: Optional[str] = Field(...)

company_search_tool = StructuredTool(
    name="Company Search",
    func=lambda **params: call_fastapi("company", params),
    args_schema=CompanySearchInput
)

person_search_tool = StructuredTool(
    name="Person Search",
    func=lambda **params: call_fastapi("person", params),
    args_schema=PersonSearchInput
)

job_search_tool = StructuredTool(
    name="Job Search",
    func=lambda **params: call_fastapi("job", params),
    args_schema=JobSearchInput
)

class SearchAPI:
    tools = [company_search_tool, person_search_tool, job_search_tool]

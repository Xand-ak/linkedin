from langchain.tools import StructuredTool
from pydantic import BaseModel, Field
from typing import Optional, List
import requests
import re

FASTAPI_BASE_URL = "http://127.0.0.1:8000"

def call_fastapi(search_type: str, params: dict):
    """Calls the correct FastAPI endpoint dynamically."""
    
    # Remove None values before making the request
    params = {k: v for k, v in params.items() if v is not None}
    
    response = requests.get(f"{FASTAPI_BASE_URL}/search/{search_type}", params=params)
    return response.json()

class CompanySearchInput(BaseModel):
    """Input for searching companies on LinkedIn."""
    country: Optional[str] = Field(None, description="Alpha-2 ISO3166 country code (e.g., US, DE, GB)")
    city: Optional[str] = Field(None, description="Filter companies based in this city")
    industry: Optional[str] = Field(None, description="Filter by industry (e.g., software, finance)")
    company_size: Optional[str] = Field(None, description="Filter by company size (e.g., 1-10, 11-50, 51-200, etc.)")
    funding_total: Optional[str] = Field(None, description="Filter by total funding amount (e.g., 1000000)")
    page_size: Optional[int] = Field(10, description="Max results per API call (1-100)")
    enrich_profiles: Optional[str] = Field("skip", description="Get full company profiles instead of just URLs (skip or enrich)")

class PersonSearchInput(BaseModel):
    """Input for searching people on LinkedIn."""
    country: Optional[str] = Field(None, description="Alpha-2 ISO3166 country code (e.g., US, DE, GB)")
    first_name: Optional[str] = Field(None, description="Filter by first name")
    last_name: Optional[str] = Field(None, description="Filter by last name")
    title: Optional[str] = Field(None, description="Filter by job title (e.g., CEO, Software Engineer)")
    skills: Optional[str] = Field(None, description="Comma-separated skills (e.g., python, javascript, machine learning)")
    company: Optional[str] = Field(None, description="Company name for filtering")
    school: Optional[str] = Field(None, description="Filter by school/university attended")

class JobSearchInput(BaseModel):
    """Input for searching jobs on LinkedIn."""
    job_type: Optional[str] = Field("anything", description="Job type: full-time, part-time, contract, internship, temporary, volunteer, anything")
    experience_level: Optional[str] = Field("anything", description="Experience level: internship, entry-level, associate, mid-senior-level, director, anything")
    flexibility: Optional[str] = Field("anything", description="Job flexibility: remote, on-site, hybrid, anything")
    keyword: Optional[str] = Field(None, description="Keyword for job search (e.g., software engineer, data scientist)")
    geo_id: Optional[str] = Field(None, description="Geographic location ID (92000000 for worldwide)")

def company_search(country: Optional[str] = None, 
                  city: Optional[str] = None,
                  industry: Optional[str] = None,
                  company_size: Optional[str] = None,
                  funding_total: Optional[str] = None,
                  page_size: Optional[int] = 10,
                  enrich_profiles: Optional[str] = "skip") -> dict:
    """
    Search for companies on LinkedIn based on various filters.
    
    Args:
        country: Alpha-2 ISO3166 country code (e.g., US, DE, GB)
        city: Filter companies based in this city
        industry: Filter by industry (e.g., software, finance)
        company_size: Filter by company size
        funding_total: Filter by total funding amount
        page_size: Max results per API call (1-100)
        enrich_profiles: Get full company profiles instead of just URLs (skip or enrich)
        
    Returns:
        List of matching companies with their details
    """
    params = {
        "country": country,
        "city": city,
        "industry": industry,
        "company_size": company_size,
        "funding_total": funding_total,
        "page_size": page_size,
        "enrich_profiles": enrich_profiles
    }
    return call_fastapi("company", params)

def person_search(country: Optional[str] = None,
                 first_name: Optional[str] = None,
                 last_name: Optional[str] = None,
                 title: Optional[str] = None,
                 skills: Optional[str] = None,
                 company: Optional[str] = None,
                 school: Optional[str] = None) -> dict:
    """
    Search for people on LinkedIn based on various filters.
    
    Args:
        country: Alpha-2 ISO3166 country code (e.g., US, DE, GB)
        first_name: Filter by first name
        last_name: Filter by last name
        title: Filter by job title (e.g., CEO, Software Engineer)
        skills: Comma-separated skills (e.g., python, javascript, machine learning)
        company: Company name for filtering
        school: Filter by school/university attended
        
    Returns:
        List of matching people with their details
    """
    params = {
        "country": country,
        "first_name": first_name,
        "last_name": last_name,
        "title": title,
        "skills": skills,
        "company": company,
        "school": school
    }
    return call_fastapi("person", params)

def job_search(job_type: Optional[str] = "anything",
              experience_level: Optional[str] = "anything",
              flexibility: Optional[str] = "anything",
              keyword: Optional[str] = None,
              geo_id: Optional[str] = None) -> dict:
    """
    Search for jobs on LinkedIn based on various filters.
    
    Args:
        job_type: Job type (full-time, part-time, contract, internship, temporary, volunteer, anything)
        experience_level: Experience level (internship, entry-level, associate, mid-senior-level, director, anything)
        flexibility: Job flexibility (remote, on-site, hybrid, anything)
        keyword: Keyword for job search (e.g., software engineer, data scientist)
        geo_id: Geographic location ID (92000000 for worldwide)
        
    Returns:
        List of matching jobs with their details
    """
    params = {
        "job_type": job_type,
        "experience_level": experience_level,
        "flexibility": flexibility,
        "keyword": keyword,
        "geo_id": geo_id
    }
    return call_fastapi("job", params)

# Create structured tools with better descriptions
company_search_tool = StructuredTool.from_function(
    func=company_search,
    name="Company Search",
    description="Search for companies on LinkedIn based on location, industry, size, and other filters"
)

person_search_tool = StructuredTool.from_function(
    func=person_search,
    name="Person Search",
    description="Search for people on LinkedIn based on name, skills, company, education, and other filters"
)

job_search_tool = StructuredTool.from_function(
    func=job_search,
    name="Job Search",
    description="Search for jobs on LinkedIn based on job type, experience level, flexibility, and keywords"
)

class SearchAPI:
    tools = [company_search_tool, person_search_tool, job_search_tool]

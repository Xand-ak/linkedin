from fastapi import FastAPI, Query
from typing import Optional
import requests

app = FastAPI()
PROXYCURL_API_KEY = "U83KELA5LBkUpkApB-WfWQ"

PROXYCURL_ENDPOINTS = {
    "company": "https://nubela.co/proxycurl/api/v2/linkedin/search/company",
    "person": "https://nubela.co/proxycurl/api/v2/linkedin/search/person",
    "job": "https://nubela.co/proxycurl/api/v2/linkedin/company/job",
}

def fetch_data(endpoint: str, params: dict):
    """Helper function to call the correct Proxycurl endpoint."""
    headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}
    
    # Remove None values to avoid bad API requests
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    response = requests.get(PROXYCURL_ENDPOINTS[endpoint], headers=headers, params=filtered_params)
    return response.json()

@app.get("/search/company")
def company_search(
    country: Optional[str] = Query(None, description="Alpha-2 ISO3166 country code"),
    city: Optional[str] = Query(None, description="Filter companies based in this city"),
    page_size: Optional[int] = Query(10, description="Max results per API call"),
    enrich_profiles: Optional[str] = Query("skip", description="Include full company data (enrich or skip)")
):
    return fetch_data("company", {
        "country": country,
        "city": city,
        "page_size": page_size,
        "enrich_profiles": enrich_profiles
    })

@app.get("/search/person")
def person_search(
    country: Optional[str] = Query(None, description="Alpha-2 ISO3166 country code"),
    first_name: Optional[str] = Query(None, description="Filter by first name"),
    last_name: Optional[str] = Query(None, description="Filter by last name"),
    skills: Optional[str] = Query(None, description="Comma-separated skills (e.g., python, c++)"),
    company: Optional[str] = Query(None, description="Company name for filtering")
):
    return fetch_data("person", {
        "country": country,
        "first_name": first_name,
        "last_name": last_name,
        "skills": skills,
        "company": company
    })

@app.get("/search/job")
def job_search(
    job_type: Optional[str] = Query("anything", description="Job type: full-time, part-time, etc."),
    experience_level: Optional[str] = Query("anything", description="Experience level: internship, entry_level, etc."),
    flexibility: Optional[str] = Query("anything", description="Job flexibility: remote, on-site, hybrid"),
    keyword: Optional[str] = Query(None, description="Keyword for job search (e.g., software engineer, teacher)")
):
    return fetch_data("job", {
        "job_type": job_type,
        "experience_level": experience_level,
        "flexibility": flexibility,
        "keyword": keyword
    })

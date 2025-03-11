import requests
from langchain.llms import Ollama
from typing import Dict, Any

PROXYCURL_API_KEY = "U83KELA5LBkUpkApB-WfWQ"

PROXYCURL_ENDPOINTS = {
    "company": "https://nubela.co/proxycurl/api/v2/search/company",
    "person": "https://nubela.co/proxycurl/api/v2/search/person",
    "job": "https://nubela.co/proxycurl/api/v2/linkedin/company/job"
}

def fetch_data(endpoint: str, params: dict):
    """Helper function to call the correct Proxycurl endpoint."""
    headers = {"Authorization": f"Bearer {PROXYCURL_API_KEY}"}
    
    # Remove None values to avoid bad API requests
    filtered_params = {k: v for k, v in params.items() if v is not None}
    
    # Get the endpoint URL
    url = PROXYCURL_ENDPOINTS.get(endpoint)
    if not url:
        raise ValueError(f"Invalid endpoint: {endpoint}")
    
    print(f"Making request to: {url}")
    print(f"With parameters: {filtered_params}")
    
    response = requests.get(url, headers=headers, params=filtered_params)
    
    # Add error handling
    if response.status_code != 200:
        print(f"Error status code: {response.status_code}")
        print(f"Error response: {response.text}")
        raise requests.exceptions.RequestException(
            f"API request failed with status code {response.status_code}: {response.text}"
        )
    
    return response.json()

def company_search(country: str = None, city: str = None, page_size: int = 1) -> dict:
    """
    Search for companies on LinkedIn.
    
    Args:
        country: Alpha-2 ISO3166 country code
        city: Filter companies based in this city
        page_size: Max results per API call
    """
    return fetch_data("company", {
        "country": country,
        "city": city,
        "page_size": page_size,
    })

def person_search(country: str = None, first_name: str = None, last_name: str = None,
                 skills: str = None, company: str = None) -> dict:
    """
    Search for people on LinkedIn.
    
    Args:
        country: Alpha-2 ISO3166 country code
        first_name: Filter by first name
        last_name: Filter by last name
        skills: Comma-separated skills (e.g., python, c++)
        company: Company name for filtering
    """
    return fetch_data("person", {
        "country": country,
        "first_name": first_name,
        "last_name": last_name,
        "skills": skills,
        "company": company
    })

def job_search(job_type: str = "anything", experience_level: str = "anything",
               flexibility: str = "anything", keyword: str = None) -> dict:
    """
    Search for jobs on LinkedIn.
    
    
    Args:
        job_type: Job type: full-time, part-time, etc.
        experience_level: Experience level: internship, entry_level, etc.
        flexibility: Job flexibility: remote, on-site, hybrid
        keyword: Keyword for job search (e.g., software engineer, teacher)
    """
    return fetch_data("job", {
        "job_type": job_type,
        "experience_level": experience_level,
        "flexibility": flexibility,
        "keyword": keyword
    }) 

def determine_search_type(query: str) -> Dict[str, Any]:
    """
    Use LLM to determine which search type to use and extract relevant parameters.
    """
    llm = Ollama(model="deepseek-r1:14b")
    
    prompt = f"""
    Analyze the following search query and determine if it's looking for companies, people, or jobs.
    Extract only the relevant parameters based on the search type.

    Example queries for company search:
    - "Find tech companies in San Francisco"
    - "Show me startups in Berlin, Germany"
    - "List software companies in London"
    - "Search for manufacturing companies in Tokyo"
    Valid company parameters are:
    - country (Alpha-2 ISO3166 code)
    - city
    - page_size (default 10)
    - enrich_profiles (default "skip")

    Example queries for person search:
    - "Find Python developers in India"
    - "Search for software engineers at Google"
    - "Look for data scientists with SQL skills in Canada"
    - "Find marketing managers named John in New York"
    Valid person parameters are:
    - country (Alpha-2 ISO3166 code)
    - first_name
    - last_name
    - skills (comma-separated)
    - company

    Example queries for job search:
    - "Find remote software engineering jobs"
    - "Search for full-time data analyst positions"
    - "Look for entry-level marketing jobs in London"
    - "Find remote AI engineer positions for senior level"
    Valid job parameters are:
    - job_type (full-time, part-time, contract, internship, temporary, volunteer, anything)
    - experience_level (internship, entry_level, associate, mid-senior-level, director, anything)
    - flexibility (remote, on-site, hybrid, anything)
    - keyword

    Current Query: {query}
    
    Respond in the following JSON format only, using only the valid parameters listed above:
    {{
        "search_type": "company|person|job",
        "parameters": {{
            // include only valid parameters for the chosen search type
        }}
    }}
    """
    
    response = llm.predict(prompt)
    try:
        import json
        return json.loads(response)
    except json.JSONDecodeError:
        return {"search_type": "person", "parameters": {}}  # default fallback

def search_linkedin(query: str) -> dict:
    """
    Main function to handle user queries and return search results.
    """
    # Determine search type and parameters using LLM
    search_info = determine_search_type(query)
    print(f"LLM determined search type: {search_info}")
    
    # Map search types to functions
    search_functions = {
        "company": company_search,
        "person": person_search,
        "job": job_search
    }
    
    # Get the appropriate search function
    search_func = search_functions.get(search_info["search_type"])
    if not search_func:
        raise ValueError(f"Invalid search type: {search_info['search_type']}")
    
    try:
        # Execute the search with extracted parameters
        return search_func(**search_info["parameters"])
    except Exception as e:
        print(f"Error executing search: {str(e)}")
        raise

# Example usage with different types of queries
if __name__ == "__main__":
    example_queries = [
        "Search for software engineers at Google",
    ]
    
    for query in example_queries:
        print(f"\nTesting query: {query}")
        try:
            results = search_linkedin(query)
            print("Search Results:")
            print(results)
        except Exception as e:
            print(f"Error: {str(e)}")
from smolagents import CodeAgent, HfApiModel
from smolagents import tool
#from huggingface_hub import list_models  # Removed this, as we'll use a different tool
import os
import requests

from dotenv import load_dotenv

load_dotenv()

@tool
def search_web(query: str) -> str:
    """
    Searches the web using the SERP API and returns the result.

    Args:
        query: The search query.
    """
    api_key = os.getenv("SERP_API_KEY")
    if not api_key:
        return "Error: SERP_API_KEY environment variable not set."

    url = "https://google.serper.dev/search"
    payload = { "q": query }
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, json=payload)
    response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
    return response.text

@tool
def model_download_tool(task: str) -> str:
    """
    This is a tool that uses web search to find the most downloaded model for a given task on Hugging Face Hub.

    Args:
        task: The task for which to find the model (e.g., "text-generation").
    """

    search_query = f"most downloaded {task} model hugging face hub"
    search_results = search_web(search_query)

    # Basic parsing (can be improved with regex or a more robust parsing library).  Critically important
    # to make this robust in a real application, handling different result formats.
    try:
        #  Look for the model id, which will be something like:  'google/flan-t5-xxl'.
        #  This is a *very* basic and fragile parsing; improvements are needed for robustness.
        model_start_index = search_results.find("modelId") + len("modelId\": \"")
        model_id = search_results[model_start_index:].split("\"")[0]
        if model_id and "/" in model_id: # Check for a valid-looking model ID (has a slash)
            return model_id

        # Alternative parsing, trying to find a Hugging Face link. More robust.
        start = search_results.find("https://huggingface.co/")
        if start != -1:
            end = search_results.find("\"", start)
            hf_url = search_results[start:end]
            model_id = hf_url.replace("https://huggingface.co/", "").strip() # remove base url
            if "/" in model_id: # still check for slash
                return model_id

        # Very basic keyword based extraction, a last resort.
        #  It will look in the response, looking for the word "model".
        #  It will be less robust.
        for part in search_results.split():
            if "/" in part and "model" in part.lower():
                 return part.strip(",;. ")

        return "Could not extract model ID from search results."

    except Exception as e:
        return f"Error parsing search results: {e}"


agent = CodeAgent(tools=[model_download_tool], model=HfApiModel()) # Keep the model download tool
agent.run(
    "Give me the most downloaded model for Image-generation on the Hugging Face Hub."
)

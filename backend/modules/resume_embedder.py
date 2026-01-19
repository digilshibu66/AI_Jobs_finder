"""Utilities to extract text from a PDF resume and embed it using OpenRouter embeddings.
The code uses OpenRouter API. Set OPENROUTER_API_KEY env var before running.
"""
import os
import PyPDF2
import numpy as np
import requests
import json
import time
import random

def extract_resume_text(path):
    """Extract text from a PDF file path."""
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    reader = PyPDF2.PdfReader(path)
    text = []
    for p in reader.pages:
        page = p.extract_text()
        if page:
            text.append(page)
    return "\n".join(text)

def _get_openrouter_api_key():
    """Get OpenRouter API key from environment variables."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set.")
    return api_key

def _call_openrouter_embeddings_api(input_text, model=None, max_retries=5):
    """Call OpenRouter Embeddings API with input text and return response."""
    api_key = _get_openrouter_api_key()
    
    # Use the correct endpoint that resolves properly
    url = "https://openrouter.ai/api/v1/embeddings"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    # Use default model if none provided
    if model is None:
        model = "text-embedding-3-large"
    
    data = {
        "input": input_text,
        "model": model
    }
    
    # Enhanced exponential backoff for rate limiting with longer delays
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 429:
                # Rate limited - implement enhanced exponential backoff with longer delays
                # Base delay of 5 seconds with exponential growth
                wait_time = (5 * (2 ** attempt)) + random.uniform(0, 2)
                print(f"  [RATE_LIMIT] Hit rate limit. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            
            result = response.json()
            return result['data'][0]['embedding']
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                # Rate limited - implement enhanced exponential backoff with longer delays
                wait_time = (5 * (2 ** attempt)) + random.uniform(0, 2)
                print(f"  [RATE_LIMIT] Hit rate limit. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (5 * (2 ** attempt)) + random.uniform(0, 2)
                print(f"  [ERROR] API call failed: {e}. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                raise
    
    raise Exception(f"Failed to call OpenRouter API after {max_retries} attempts")

def embed_text(text, ai_model=None):
    """Return embedding vector for text using OpenRouter embeddings.
    If API key is missing, raises error.
    """
    _get_openrouter_api_key()
    embedding = _call_openrouter_embeddings_api(text, ai_model)
    return np.array(embedding, dtype='float32')

import os
import time
import random
import requests
import google.generativeai as genai
from typing import List, Dict, Any

def get_ai_provider():
    """Get the configured AI provider."""
    return os.environ.get("AI_PROVIDER", "gemini").lower()

def call_ai_api(messages: List[Dict[str, str]], model: str = None, max_retries: int = 3) -> str:
    """
    Unified function to call AI APIs (OpenRouter or Google Gemini).
    
    Args:
        messages: List of message dicts [{"role": "user", "content": "..."}]
        model: Model name (optional)
        max_retries: Number of retries
        
    Returns:
        str: The AI's response content
    """
    provider = get_ai_provider()
    
    if provider == "gemini":
        return _call_gemini_api(messages, model, max_retries)
    else:
        return _call_openrouter_api(messages, model, max_retries)

# ----------------- Google Gemini Implementation -----------------

def _call_gemini_api(messages: List[Dict[str, str]], model: str = None, max_retries: int = 3) -> str:
    """Call Google Gemini API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please add it to your .env file.")
    
    genai.configure(api_key=api_key)
    
    # Default to flash model if not specified or if an OpenRouter model was passed
    if not model or "gemini" not in model.lower():
        model = "gemini-1.5-flash" 
    elif "gemini" in model.lower() and "/" in model:
         # Clean up OpenRouter style names like "google/gemini-pro"
        if "pro" in model.lower():
            model = "gemini-1.5-pro"
        elif "2.0" in model.lower():
            model = "gemini-2.0-flash"
        else:
            model = "gemini-1.5-flash"

    # Convert OpenAI/OpenRouter message format to Gemini format
    # Join all messages into a single prompt for simplicity, or structure them
    prompt = ""
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt += f"System Instruction: {content}\n\n"
        elif role == "user":
            prompt += f"User: {content}\n\n"
        elif role == "assistant":
            prompt += f"Model: {content}\n\n"
            
    generation_config = {
        "temperature": 0.7,
        "top_p": 0.95,
        "top_k": 40,
        "max_output_tokens": 8192,
    }

    for attempt in range(max_retries):
        try:
            model_instance = genai.GenerativeModel(
                model_name=model,
                generation_config=generation_config
            )
            
            response = model_instance.generate_content(prompt)
            return response.text
            
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (2 * (2 ** attempt)) + random.uniform(0, 1)
                print(f"  [GEMINI ERROR] {e}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
            else:
                print(f"  [GEMINI FAILED] {e}")
                raise

# ----------------- OpenRouter Implementation -----------------

def _call_openrouter_api(messages, model=None, max_retries=5):
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY is not set.")

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "http://localhost:3000",
        "X-Title": "AI-Mailer"
    }

    if model is None:
        model = "meta-llama/llama-3.3-70b-instruct:free"

    data = {"model": model, "messages": messages}

    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data, timeout=60)

            if response.status_code == 429:
                time.sleep(5 * (2 ** attempt))
                continue

            if not response.ok:
                raise Exception(f"HTTP {response.status_code}: {response.text}")

            result = response.json()

            if "choices" not in result:
                raise Exception(f"Invalid OpenRouter response: {result}")

            return result["choices"][0]["message"]["content"]

        except Exception as e:
            print(f"[OpenRouter ERROR] Attempt {attempt+1}: {e}")
            if attempt == max_retries - 1:
                raise
            time.sleep(3 * (2 ** attempt))

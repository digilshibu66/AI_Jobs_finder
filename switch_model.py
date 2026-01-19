#!/usr/bin/env python3
"""
Script to easily switch between different free AI models in the .env file.
"""

import os
from dotenv import set_key, load_dotenv

# List of available free models
FREE_MODELS = [
    'nousresearch/hermes-3-llama-3.1-405b:free',
    'mistralai/devstral-2512:free',
    'nex-agi/deepseek-v3.1-nex-n1:free',
    'amazon/nova-2-lite-v1:free',
    'arcee-ai/trinity-mini:free',
    'tngtech/tng-r1t-chimera:free',
    'allenai/olmo-3-32b-think:free',
    'kwaipilot/kat-coder-pro:free',
    'nvidia/nemotron-nano-12b-v2-vl:free',
    'alibaba/tongyi-deepresearch-30b-a3b:free',
    'nvidia/nemotron-nano-9b-v2:free',
    'openai/gpt-oss-120b:free',
    'openai/gpt-oss-20b:free',
    'z-ai/glm-4.5-air:free',
    'qwen/qwen3-coder:free',
    'moonshotai/kimi-k2:free',
    'cognitivecomputations/dolphin-mistral-24b-venice-edition:free',
    'google/gemma-3n-e2b-it:free',
    'tngtech/deepseek-r1t2-chimera:free',
    'google/gemma-3n-e4b-it:free',
    'qwen/qwen3-4b:free',
    'qwen/qwen3-235b-a22b:free',
    'tngtech/deepseek-r1t-chimera:free',
    'mistralai/mistral-small-3.1-24b-instruct:free',
    'google/gemma-3-4b-it:free',
    'google/gemma-3-12b-it:free',
    'google/gemma-3-27b-it:free',
    'google/gemini-2.0-flash-exp:free',
    'meta-llama/llama-3.3-70b-instruct:free',
    'meta-llama/llama-3.2-3b-instruct:free',
    'mistralai/mistral-7b-instruct:free'
]

def list_models():
    """List all available free models."""
    print("Available free models:")
    for i, model in enumerate(FREE_MODELS, 1):
        marker = " (current)" if is_current_model(model) else ""
        print(f"{i:2d}. {model}{marker}")

def is_current_model(model):
    """Check if the given model is the current model in .env file."""
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        return False
        
    load_dotenv(env_path)
    current_model = os.getenv('AI_MODEL', '')
    return current_model == model

def switch_model(model_index):
    """Switch to the specified model."""
    if model_index < 1 or model_index > len(FREE_MODELS):
        print(f"Invalid model index. Please choose between 1 and {len(FREE_MODELS)}.")
        return False
        
    selected_model = FREE_MODELS[model_index - 1]
    
    # Update .env file
    project_root = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(project_root, '.env')
    
    if not os.path.exists(env_path):
        print(f"Error: .env file not found at {env_path}")
        return False
    
    set_key(env_path, 'AI_MODEL', selected_model)
    print(f"Successfully switched to model: {selected_model}")
    return True

def main():
    """Main function."""
    print("AI Model Switcher")
    print("=" * 50)
    
    if len(os.sys.argv) > 1:
        try:
            model_index = int(os.sys.argv[1])
            switch_model(model_index)
        except ValueError:
            print("Invalid argument. Please provide a number.")
    else:
        list_models()
        print("\nTo switch models, run: python switch_model.py <model_number>")

if __name__ == "__main__":
    main()
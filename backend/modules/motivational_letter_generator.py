"""Generate motivational letters for job applications using OpenRouter API."""

import os
import re
import requests
import json
import time
import random


def _get_openrouter_api_key():
    """Get OpenRouter API key from environment variables."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY environment variable is not set.")
    return api_key

def _call_openrouter_api(messages, model=None, max_retries=5):
    """Call OpenRouter API with messages and return response."""
    api_key = _get_openrouter_api_key()
    
    # Use the correct endpoint that resolves properly
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/freelance-mailer",  # Optional, for tracking
        "X-Title": "Freelance Mailer"  # Optional, for tracking
    }
    
    # Use default model if none provided
    if model is None:
        model = "nousresearch/hermes-3-llama-3.1-405b:free"
    
    data = {
        "model": model,
        "messages": messages
    }
    
    # Enhanced exponential backoff for rate limiting with longer delays
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, json=data)
            if response.status_code == 429:
                # Rate limited - implement enhanced exponential backoff with longer delays
                # Base delay of 15 seconds with exponential growth (free models need more time)
                wait_time = (15 * (2 ** attempt)) + random.uniform(0, 5)
                print(f"  [RATE_LIMIT] Hit rate limit. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            response.raise_for_status()
            
            result = response.json()
            return result['choices'][0]['message']['content']
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 429 and attempt < max_retries - 1:
                # Rate limited - implement enhanced exponential backoff with longer delays
                wait_time = (15 * (2 ** attempt)) + random.uniform(0, 5)
                print(f"  [RATE_LIMIT] Hit rate limit. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                print(f"  [API_ERROR] Status: {e.response.status_code}")
                print(f"  [API_ERROR] Response: {e.response.text}")
                raise
        except Exception as e:
            if attempt < max_retries - 1:
                wait_time = (15 * (2 ** attempt)) + random.uniform(0, 5)
                print(f"  [ERROR] API call failed: {e}. Waiting {wait_time:.2f} seconds before retry {attempt + 1}/{max_retries}...")
                time.sleep(wait_time)
                continue
            else:
                raise
    
    raise Exception(f"Failed to call OpenRouter API after {max_retries} attempts")


def generate_motivational_letter(job_title, job_description, resume_text, ai_model=None):
    """Generate a motivational letter for a specific job application.
    
    Args:
        job_title (str): The title of the job position
        job_description (str): Detailed description of the job requirements
        resume_text (str): The applicant's resume text
        ai_model (str): The AI model to use for generation
        
    Returns:
        str: Generated motivational letter content
    """
    _get_openrouter_api_key()
    
    messages = [
        {
            "role": "user",
            "content": f"""
Create a compelling motivational letter for a job application that demonstrates why I'm the perfect candidate for this position.

Job Title: {job_title}
Job Description: {job_description}

My Resume:
{resume_text[:4000]}

Requirements for the motivational letter:
1. Begin with a professional salutation (e.g., "Dear Hiring Manager," or "Dear [Company Name] Team,")
2. In the opening paragraph, clearly state the position you're applying for and how you learned about it
3. In the body paragraphs:
   - Explain why you're interested in this role and company
   - Highlight your most relevant skills and experiences that match the job requirements
   - Provide specific examples from your resume that demonstrate your qualifications
   - Show how you can contribute to the company's goals
4. Conclude with enthusiasm for the opportunity and a call to action (request for an interview)
5. End with a professional closing (e.g., "Sincerely," or "Best regards,") followed by your name
6. Keep it concise (300-400 words)
7. Maintain a professional yet personable tone
8. Customize the content specifically for this job (no generic templates)

Important guidelines:
- Focus on what you can offer the company, not what the company can offer you
- Reference specific requirements from the job description
- Use concrete examples from your resume to support your claims
- Show genuine interest in the company and role
- Proofread for grammar and clarity

Return only the motivational letter content with no additional explanations or formatting.
"""
        }
    ]

    response = _call_openrouter_api(messages, ai_model)
    return response.strip()


def save_motivational_letter_as_pdf(letter_content, output_path):
    """Save the motivational letter as a PDF file.
    
    Args:
        letter_content (str): The content of the motivational letter
        output_path (str): Path where the PDF should be saved
        
    Returns:
        str: Path to the saved PDF file
    """
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import inch
        
        # Create PDF document
        doc = SimpleDocTemplate(output_path, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=12
        )
        
        # Build document content
        story = []
        
        # Add letter content with proper formatting
        paragraphs = letter_content.split('\n\n')
        for i, para in enumerate(paragraphs):
            if i == 0 and len(para.split()) < 10:  # Likely a salutation
                story.append(Paragraph(para, normal_style))
                story.append(Spacer(1, 12))
            elif para.strip():  # Non-empty paragraph
                story.append(Paragraph(para.replace('\n', '<br/>'), normal_style))
                story.append(Spacer(1, 12))
        
        # Build PDF
        doc.build(story)
        return output_path
    except ImportError:
        # If reportlab is not available, save as plain text
        txt_path = output_path.replace('.pdf', '.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(letter_content)
        return txt_path
    except Exception as e:
        # Fallback to text file if PDF generation fails
        txt_path = output_path.replace('.pdf', '_fallback.txt')
        with open(txt_path, 'w', encoding='utf-8') as f:
            f.write(letter_content)
        return txt_path
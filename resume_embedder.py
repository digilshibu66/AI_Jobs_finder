"""Utilities to extract text from a PDF resume and embed it using Gemini embeddings.
The code uses `google.generativeai` (Gemini). Set GEMINI_API_KEY env var before running.
"""
import os
import PyPDF2
import numpy as np
try:
    import google.generativeai as genai
except Exception:
    genai = None

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

def embed_text(text):
    """Return embedding vector for text using Gemini embeddings.
    If `google.generativeai` is not installed or API key missing, raises error.
    """
    if genai is None:
        raise RuntimeError('google.generativeai is not installed or importable.')
    genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))
    model = genai.GenerativeModel('text-embedding-003')  # adjust per availability
    resp = model.embed_content(text)
    return np.array(resp['embedding'], dtype='float32')

import os
from typing import Any, Dict, List

import google.generativeai as genai
from dotenv import load_dotenv

from app.services.ai_config_service import (get_active_gemini_key,
                                            get_all_configs)

# Load environment variables
load_dotenv()


def get_configured_model():
    """
    Get Gemini model with API key from AI config or fallback to env.
    """
    # Try to get API key from database config first
    api_key = get_active_gemini_key()
    
    # Fallback to environment variable if not set in database
    if not api_key:
        api_key = os.getenv("GEMINI_API_KEY")
    
    # Configure Gemini API
    genai.configure(api_key=api_key)
    
    # Initialize and return Gemini model
    return genai.GenerativeModel('gemini-2.0-flash-exp')


def build_prompt(user_query: str, search_results: List[Dict[str, Any]]) -> str:
    # Jika tidak ada hasil search
    if not search_results:
        return f"""
Pengguna bertanya: "{user_query}"

Namun tidak ada informasi layanan yang relevan ditemukan di database.
Tolong beri tahu pengguna dengan sopan bahwa informasi yang mereka cari tidak tersedia.
"""
    
    # Build context dari search results
    context_parts = []
    for idx, result in enumerate(search_results, 1):
        content = result.get('content', '')
        similarity = result.get('similarity', 0)
        
        context_parts.append(f"""
=== Layanan {idx} (Relevansi: {similarity:.1%}) ===
{content}
""")
    
    context = "\n".join(context_parts)
    
    # Build complete prompt
    prompt = f"""
Anda adalah asisten virtual untuk layanan publik Kota Denpasar yang ramah dan membantu.

KONTEKS INFORMASI LAYANAN:
{context}

PERTANYAAN PENGGUNA:
"{user_query}"

INSTRUKSI:
1. Jawab pertanyaan pengguna dengan bahasa yang natural, ramah, dan mudah dipahami
2. Gunakan informasi dari layanan yang paling relevan (similarity tertinggi)
3. Berikan informasi yang spesifik dan praktis (persyaratan, prosedur, waktu, tarif, dll)
4. Jika ada beberapa layanan relevan, sebutkan pilihan yang tersedia
5. Sertakan informasi kontak pengaduan jika ada
6. Jangan menyebutkan "similarity score" atau istilah teknis lainnya
7. Akhiri dengan menawarkan bantuan lebih lanjut

JAWABAN:
"""
    
    return prompt


def generate_response(user_query: str, search_results: List[Dict[str, Any]]) -> str:
    """
    Generate response menggunakan Gemini berdasarkan search results.
    
    Args:
        user_query: Pertanyaan user
        search_results: Hasil search dari RAG
        
    Returns:
        Response string dari Gemini
    """
    try:
        # Get configured model with API key from database
        model = get_configured_model()
        
        # Build prompt
        prompt = build_prompt(user_query, search_results)
        
        # Generate response dengan Gemini
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        return f"Maaf, terjadi kesalahan dalam memproses pertanyaan Anda: {str(e)}"


def build_prompt_with_history(
    user_query: str,
    search_results: List[Dict[str, Any]],
    conversation_context: str = ""
) -> str:
    """
    Build prompt dengan conversation history untuk continuity.
    
    Args:
        user_query: Current user question
        search_results: Search results from RAG
        conversation_context: Previous conversation formatted string
        
    Returns:
        Complete prompt dengan history
    """
    # Jika tidak ada hasil search
    if not search_results:
        base_prompt = f"""
Pengguna bertanya: "{user_query}"

Namun tidak ada informasi layanan yang relevan ditemukan di database.
Tolong beri tahu pengguna dengan sopan bahwa informasi yang mereka cari tidak tersedia.
"""
    else:
        # Build context dari search results
        context_parts = []
        for idx, result in enumerate(search_results, 1):
            content = result.get('content', '')
            similarity = result.get('similarity', 0)
            
            context_parts.append(f"""
=== Layanan {idx} (Relevansi: {similarity:.1%}) ===
{content}
""")
        
        context = "\n".join(context_parts)
        
        base_prompt = f"""
KONTEKS INFORMASI LAYANAN:
{context}
"""
    
    # Add conversation history jika ada
    history_section = ""
    if conversation_context:
        history_section = f"""
RIWAYAT PERCAKAPAN SEBELUMNYA:
{conversation_context}

(Gunakan riwayat di atas untuk memahami konteks, jika pertanyaan saat ini merujuk ke percakapan sebelumnya)
"""
    
    # Complete prompt
    prompt = f"""
Anda adalah asisten virtual untuk layanan publik Kota Denpasar yang ramah dan membantu.

{base_prompt}
{history_section}

PERTANYAAN PENGGUNA SAAT INI:
"{user_query}"

INSTRUKSI:
1. Jawab pertanyaan pengguna dengan bahasa yang natural, ramah, dan mudah dipahami
2. Jika ada riwayat percakapan, gunakan untuk memahami konteks (misal: "itu", "tadi", dll)
3. Gunakan informasi dari layanan yang paling relevan
4. Berikan informasi yang spesifik dan praktis (persyaratan, prosedur, waktu, tarif, dll)
5. Jika ada beberapa layanan relevan, sebutkan pilihan yang tersedia
6. Jangan menyebutkan "similarity score" atau istilah teknis lainnya
7. Akhiri dengan menawarkan bantuan lebih lanjut

JAWABAN:
"""
    
    return prompt


def generate_response_with_history(
    user_query: str,
    search_results: List[Dict[str, Any]],
    conversation_context: str = ""
) -> str:
    """
    Generate response dengan conversation history context.
    
    Args:
        user_query: Pertanyaan user
        search_results: Hasil search dari RAG
        conversation_context: Previous conversation context
        
    Returns:
        Response string dari Gemini
    """
    try:
        # Get configured model
        model = get_configured_model()
        
        # Build prompt dengan history
        prompt = build_prompt_with_history(user_query, search_results, conversation_context)
        
        # Generate response
        response = model.generate_content(prompt)
        
        return response.text
        
    except Exception as e:
        return f"Maaf, terjadi kesalahan dalam memproses pertanyaan Anda: {str(e)}"


def chat_with_rag(
    user_query: str,
    search_results: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: int = 1024
) -> Dict[str, Any]:
    """
    Complete chatbot flow: RAG + LLM generation (tanpa history).
    
    Args:
        user_query: User's question
        search_results: Search results from RAG service
        temperature: Response creativity (0-1)
        max_tokens: Maximum response length
        
    Returns:
        Dictionary with query, response, and metadata
    """
    # Generate response
    response = generate_response(user_query, search_results)
    
    return {
        "query": user_query,
        "response": response,
        "num_sources": len(search_results),
        "sources": [
            {
                "service_id": result.get("service_id"),
                "content": result.get("content"),
                "similarity": result.get("similarity")
            }
            for result in search_results
        ]
    }


def chat_with_rag_and_history(
    user_query: str,
    search_results: List[Dict[str, Any]],
    conversation_context: str = ""
) -> Dict[str, Any]:
    """
    Complete chatbot flow dengan conversation history untuk user chat.
    
    Args:
        user_query: User's question
        search_results: Search results from RAG service
        conversation_context: Previous conversation formatted string
        
    Returns:
        Dictionary with query and response (simple format untuk user)
    """
    # Generate response dengan history
    response = generate_response_with_history(user_query, search_results, conversation_context)
    
    return {
        "query": user_query,
        "response": response
    }

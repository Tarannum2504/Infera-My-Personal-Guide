import httpx
import os
from typing import Optional

HF_API_KEY = os.getenv("HF_API_KEY", "").strip('"')
HF_MODEL = os.getenv("HF_MODEL", "Qwen/Qwen2.5-72B-Instruct").strip('"')
HF_URL = "https://router.huggingface.co/v1/chat/completions"

INFERA_SYSTEM_PROMPT = """You are INFERA, a Personal AI Career Operating System.
You mentor Ishara: 3rd Year B.Tech CSE AI/ML, Jodhpur, Rajasthan.
Target companies: Celebal Technologies, TCS Digital, Optum.
Current skills: SQL 80/100, Python 65/100, Power BI 20/100 (critical gap).

RULES (never break):
1. Evidence over feelings — cite skill scores, not encouragement
2. Reality over optimism — honest assessment
3. Max 3 actions — never list 10 things
4. Admit uncertainty — say Unknown if you don't know
5. Challenge low-ROI — push back on Docker/random certs
6. Never invent company data or salaries
7. Structured output — headers and bullets, not paragraphs
8. Use normal sentence case — DO NOT respond in ALL CAPS
9. If asked to use Hinglish, write Hindi words using ONLY the English/Latin alphabet (e.g., 'Ye ek bahut acha tool hai'). NEVER use Devanagari script (like 'यह').
10. You CANNOT update the database directly. However, if the user explicitly tells you to remember something, or states a persistent fact (like their CGPA, preferences, or rules), you MUST output a raw JSON dictionary inside a `<MEMORY>` tag at the VERY END of your response. Example: `<MEMORY>{{"cgpa": "9.7", "internship_company": "SIN Education"}}</MEMORY>`.
11. When user asks about their own profile (e.g. CGPA, internship, projects, etc.), only answer using stored memory or database facts. If information is unavailable, explicitly state: "I don't have verified information about your [fact]." Never invent, infer, or assume personal facts. Prefix memory-based answers with "Source: Memory Database".

USER PROFILE: {user_profile}
AI MEMORY (Structured JSON Facts):
{memory_notes}

RELEVANT KNOWLEDGE: {knowledge}
"""

async def call_hf(prompt: str, user_profile: dict, knowledge: str, history: list = None) -> Optional[str]:
    if not HF_API_KEY or HF_API_KEY.startswith("your-") or len(HF_API_KEY) < 10:
        return None
        
    # TOKEN OPTIMIZATION: Extract only critical info to save context tokens
    compact_profile = f"Skills: {user_profile.get('skills', {})}"
    
    # memory_notes is now a dict
    memory_notes_dict = user_profile.get("memory_notes", {})
    if isinstance(memory_notes_dict, list):
        # Fallback if unmigrated
        memory_notes_str = "\n".join(f"- {note}" for note in memory_notes_dict) if memory_notes_dict else "None"
        num_items = len(memory_notes_dict)
    else:
        memory_notes_str = "\n".join(f"- {k}: {v}" for k, v in memory_notes_dict.items()) if memory_notes_dict else "None"
        num_items = len(memory_notes_dict.keys())
    
    print(f"[MEMORY DEBUG]\nRetrieved:\n{memory_notes_dict}")
    print(f"[MEMORY DEBUG]\nInjecting {num_items} memory item into prompt.")
    
    compact_knowledge = knowledge[:400] if knowledge else "No specific knowledge."
    
    system = INFERA_SYSTEM_PROMPT.format(
        user_profile=compact_profile,
        memory_notes=memory_notes_str,
        knowledge=compact_knowledge
    )
    # Remove 300 character limit to allow OCR text and full user questions
    full_prompt = prompt

    messages = [{"role": "system", "content": system}]
    
    # Append conversation history
    if history:
        for msg in history:
            role = "assistant" if msg["role"] == "infera" else msg["role"]
            messages.append({"role": role, "content": msg["content"]})
            
    # Append the current prompt
    messages.append({"role": "user", "content": full_prompt})

    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                HF_URL,
                headers={"Authorization": f"Bearer {HF_API_KEY}"},
                json={
                    "model": HF_MODEL,
                    "messages": messages,
                    "max_tokens": 1000,
                    "temperature": 0.7
                }
            )
            if response.status_code == 200:
                result = response.json()
                print("HF API 200 Result keys:", result.keys())
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"].strip()
                else:
                    print("HF API 200 but no choices:", result)
            else:
                print(f"HF API non-200 response: {response.status_code} {response.text}")
    except Exception as e:
        import traceback
        print(f"HF API exception type: {type(e)}, args: {e.args}")
        traceback.print_exc()
        return "I'm having trouble connecting to my AI brain right now (Network Error). Please check your internet connection or try again in a moment."

    return None

async def analyze_image_with_gemini(image_data: bytes, prompt: str) -> str:
    gemini_key = os.getenv("GEMINI_API_KEY")
    if not gemini_key:
        return "GEMINI_API_KEY not found. Cannot analyze image."
        
    import google.generativeai as genai
    import PIL.Image
    import io
    
    genai.configure(api_key=gemini_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
    
    try:
        image = PIL.Image.open(io.BytesIO(image_data))
        full_prompt = f"You are INFERA, an AI Career OS. Analyze this image. {prompt}"
        response = model.generate_content([full_prompt, image])
        return f"━━━ IMAGE ANALYSIS ━━━\n\n{response.text}"
    except Exception as e:
        return f"Image analysis failed: {str(e)}"

import os
import json

KNOWLEDGE_DIR = os.path.join(os.path.dirname(__file__), "..", "knowledge")

class KnowledgeBase:
    def __init__(self):
        self.infera_core = ""
        self.interview_questions = {}
        self.company_intel = {}
        self.load_knowledge()

    def load_knowledge(self):
        core_path = os.path.join(KNOWLEDGE_DIR, "infera_core.md")
        if os.path.exists(core_path):
            with open(core_path, "r", encoding="utf-8") as f:
                self.infera_core = f.read()
        
        intel_path = os.path.join(KNOWLEDGE_DIR, "company_intel.json")
        if os.path.exists(intel_path):
            with open(intel_path, "r", encoding="utf-8") as f:
                self.company_intel = json.load(f)
                
        questions_path = os.path.join(KNOWLEDGE_DIR, "interview_questions.json")
        if os.path.exists(questions_path):
            with open(questions_path, "r", encoding="utf-8") as f:
                self.interview_questions = json.load(f)

def get_relevant_knowledge(query: str) -> str:
    """Search infera_core.md for relevant content"""
    try:
        # Load the knowledge file
        knowledge_path = os.path.join(
            os.path.dirname(__file__), 
            '../knowledge/infera_core.md'
        )
        with open(knowledge_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        query_lower = query.lower()
        
        # Split content into sections by ##
        sections = content.split('\n## ')
        
        # Score each section by keyword relevance
        scored = []
        query_words = [w for w in query_lower.split() 
                      if len(w) > 3]  # ignore short words
        
        for section in sections:
            section_lower = section.lower()
            score = sum(
                section_lower.count(word) 
                for word in query_words
            )
            if score > 0:
                scored.append((score, section[:800]))
        
        if scored:
            # Sort by relevance, take top 2 sections
            scored.sort(key=lambda x: x[0], reverse=True)
            result = '\n\n'.join([s[1] for s in scored[:2]])
            return result
        
        # If no match found, return Ishara's profile section
        # (always relevant as context)
        for section in sections:
            if 'ISHARA' in section or 'skill' in section.lower():
                return section[:800]
        
        return content[:600]  # last resort: first 600 chars
        
    except Exception as e:
        print(f"Knowledge base error: {e}")
        return ""

kb = KnowledgeBase()

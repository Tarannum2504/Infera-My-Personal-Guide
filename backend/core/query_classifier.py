def classify(message: str) -> str:
    msg = message.lower().strip()
    # Remove punctuation for matching
    msg_clean = "".join(c for c in msg if c.isalnum() or c.isspace())
    
    # EXACT MATCHES for Quick Action buttons and strict short commands
    if msg_clean in ["my status", "dashboard", "status", "show my status"]:
        return "dashboard"
        
    if msg_clean in ["i have 60 minutes", "priority plan", "60 min plan", "what to do today"]:
        return "priority"
        
    if msg_clean in ["am i ready for celebal", "celebal check", "tcs check", "optum check"]:
        return "company_readiness"
        
    if msg_clean in ["give me a sql quiz", "sql quiz", "quiz me", "start quiz", "quiz"]:
        return "quiz"
        
    if msg_clean in ["mock interview", "start interview", "interview me"]:
        return "interview"
        
    if msg_clean in ["check my resume", "resume analyzer", "analyze resume", "review resume"]:
        return "resume"
        
    if msg_clean in ["future sim", "simulate future", "where will i be in 3 months", "3 months"]:
        return "future_sim"
        
    if msg_clean in ["weekly review", "review my week", "this week"]:
        return "weekly_review"
        
    # Also support priority plan with dynamic minutes if format is exact (e.g., "i have 45 minutes")
    import re
    if re.match(r"^i have \d+ minutes$", msg_clean):
        return "priority"
        
    return "general"

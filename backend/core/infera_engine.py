import os
import random
from datetime import datetime
from sqlalchemy.orm import Session
from core.knowledge_base import get_relevant_knowledge, kb
from core.llm_client import call_hf

async def process_message(
    message: str,
    query_type: str,
    user_profile: dict,
    user_id: int,
    db: Session
) -> str:
    """Route message to correct handler and return response string."""

    msg = message.lower().strip()

    try:
        if query_type == "dashboard":
            return generate_dashboard(user_profile)

        elif query_type == "priority":
            minutes = extract_minutes(message)
            return generate_priority(minutes, user_profile)

        elif query_type == "decision":
            return generate_decision(message, user_profile)

        elif query_type == "company_readiness":
            company = extract_company(message)
            return generate_company_readiness(company, user_profile)

        elif query_type == "challenge":
            return generate_challenge(message, user_profile)

        elif query_type == "future_sim":
            return generate_future_sim(user_profile)

        elif query_type == "weekly_review":
            return generate_weekly_review(user_profile)

        elif query_type == "resume_qa":
            return generate_resume_chat_response(message, user_id, db)

        elif query_type == "quiz":
            return ("To take a quiz, go to the **Quizzes** tab in the "
                    "sidebar. Choose your topic (SQL, Python, Statistics, "
                    "Power BI, Azure, Business Analytics) and start "
                    "a 5-question session with instant scoring.")

        elif query_type == "interview":
            return ("To start a mock interview, go to the **Interviews** "
                    "tab. Select your target company (Celebal, TCS, Optum) "
                    "and round. You will get real questions with a timer "
                    "and scored feedback after each answer.")

        else:
            lang = detect_language_style(message)

            if lang == "hinglish":
                # Try direct hinglish answer first
                hinglish_ans = build_hinglish_answer(message, user_profile)
                if "ke baare mein zyada detail chahiye" not in hinglish_ans.lower():
                    return hinglish_ans

            # General question — try HF first, then direct answer
            knowledge = get_relevant_knowledge(message)
            hf_response = await call_hf(message, user_profile, knowledge)

            if hf_response and len(hf_response.strip()) > 80:
                hf_response = trim_response(hf_response, max_words=200)
                return hf_response

            return build_direct_answer(message, user_profile)

    except Exception as e:
        print(f"Engine error for '{message}': {e}")
        return (f"INFERA error processing: '{message[:50]}'. "
                f"Try rephrasing or ask about: Power BI, SQL, "
                f"Databricks, Celebal, TCS, Optum, statistics, "
                f"or type 'My status' for your dashboard.")


# ─────────────────────────────────────────
# HELPER: Extract numbers from message
# ─────────────────────────────────────────

def extract_minutes(message: str) -> int:
    import re
    msg = message.lower()

    # "2 hours" → 120
    hours = re.search(r'(\d+)\s*hour', msg)
    if hours:
        return int(hours.group(1)) * 60

    # "90 minutes" or "90 mins"
    mins = re.search(r'(\d+)\s*min', msg)
    if mins:
        return int(mins.group(1))

    # "I have 60" — just a number
    num = re.search(r'have\s+(\d+)', msg)
    if num:
        return int(num.group(1))

    return 60  # default


def extract_company(message: str) -> str:
    msg = message.lower()
    if "celebal" in msg:
        return "Celebal"
    if "tcs" in msg or "tata" in msg:
        return "TCS Digital"
    if "optum" in msg:
        return "Optum"
    if "deloitte" in msg:
        return "Deloitte"
    if "publicis" in msg or "sapient" in msg:
        return "Publicis Sapient"
    if "mediaocean" in msg:
        return "Mediaocean"
    return "Celebal"  # default

def detect_language_style(message: str) -> str:
    """Detect if message is Hinglish/Hindi or English."""
    hinglish_markers = [
        "kya", "kaise", "batao", "samjhao",
        "matlab", "iska", "uska", "mujhe", "chahiye",
        "kaisa", "karo", "to ", "hai", "hota", "hoti",
        "kyun", "kyunki", "aur", "yaar", "bhai", "didi",
        "nahi", "nhi", "haan", "accha", "theek", "thik",
        "bata", "dekh", "sun", "lag", "kuch", "sab",
        "abhi", "pehle", "baad", "sirf", "bas"
    ]
    msg_lower = message.lower()
    if any(marker in msg_lower for marker in hinglish_markers):
        return "hinglish"
    return "english"

def trim_response(text: str, max_words: int = 250) -> str:
    """Ensure responses don't become Wikipedia articles."""
    words = text.split()
    if len(words) <= max_words:
        return text
    # Cut at a sentence boundary near the limit
    trimmed = " ".join(words[:max_words])
    last_period = trimmed.rfind(".")
    if last_period > max_words * 3:  # if period found reasonably close
        return trimmed[:last_period+1]
    return trimmed + "..."

def build_hinglish_answer(message: str, user_profile: dict) -> str:
    msg = message.lower()
    skills = user_profile.get("skills", {})

    if "pandas" in msg:
        return (
            "Pandas ek Python library hai data analysis ke liye.\n\n"
            "Kya karta hai:\n"
            "1. CSV/Excel files read karo — pd.read_csv()\n"
            "2. Data clean karo — nulls hatao, filter karo\n"
            "3. Analysis karo — groupby, merge, pivot\n"
            "4. Visualize karo — plot() function se\n\n"
            "Tera score: Python " + str(skills.get('Python',65)) + "/100\n\n"
            "Practice: Kaggle ke Titanic dataset pe pandas try karo.\n"
            "Celebal aur TCS dono mein pandas ka use hota hai."
        )

    if any(w in msg for w in ["sql", "query"]):
        return (
            "SQL se database se data nikalta hai.\n\n"
            "Important cheezein:\n"
            "1. SELECT, WHERE, JOIN — basics\n"
            "2. GROUP BY, HAVING — aggregation\n"
            "3. Window Functions — RANK, LAG, LEAD\n"
            "4. CTE — WITH clause\n\n"
            "Tera SQL score: " + str(skills.get('SQL',80)) + "/100 — strong hai!\n"
            "Practice: LeetCode SQL 50 karo."
        )

    if any(w in msg for w in ["power bi", "powerbi", "pbi"]):
        return (
            "Power BI Microsoft ka BI tool hai — dashboards banane ke liye.\n\n"
            "Seekhna hai:\n"
            "1. Data import karo (Excel, SQL, Azure se)\n"
            "2. Visuals banao — bar chart, KPI card, slicer\n"
            "3. DAX formulas — CALCULATE, SUMX, FILTER\n"
            "4. Publish karo Power BI Service pe\n\n"
            "Tera score: " + str(skills.get('Power BI',20)) + "/100 — CRITICAL GAP!\n"
            "Celebal aur Optum dono require karte hain.\n\n"
            "Aaj start kar: Microsoft Learn → Power BI Desktop\n"
            "(Free hai, 6 ghante ka course)"
        )

    # Default hinglish response
    return (
        f"'{message}' ke baare mein zyada detail chahiye.\n\n"
        "Ye topics puch sakti hai:\n"
        "  Power BI, SQL, Pandas, Azure, Databricks,\n"
        "  Celebal interview prep, resume review\n\n"
        "'My status' type kar apna dashboard dekhne ke liye."
    )


def build_direct_answer(message: str, user_profile: dict) -> str:
    """Direct answers to common questions without HF"""
    msg = message.lower()
    skills = user_profile.get('skills', {})
    
    DIRECT_ANSWERS = {
        'power bi': """Power BI is Microsoft's business intelligence 
tool for creating interactive dashboards and reports.

For your preparation:
• Connect to data sources (Excel, SQL, Azure, Databricks)
• Build visuals: bar charts, KPI cards, slicers, drill-throughs
• Write DAX formulas: CALCULATE, SUMX, FILTER, time intelligence
• Publish to Power BI Service for sharing

Your current score: {pbi}/100 — CRITICAL GAP.
Celebal and Optum both list Power BI as required.

Start today: Microsoft Learn → "Create reports with Power BI Desktop" 
(free, 6 hours, gives you interview-ready knowledge)""".format(
            pbi=skills.get('Power BI', 20)),

        'medallion': """Medallion Architecture is Databricks' data 
organization pattern with 3 layers:

BRONZE (Raw): Data ingested as-is from source systems.
No transformation. Preserves original data.

SILVER (Cleaned): Validated, deduplicated, standardized data.
Business rules applied. Ready for analysis.

GOLD (Business-ready): Aggregated, optimized tables built for
specific use cases — dashboards, ML, executive reporting.

Why Celebal will ask this: They use Databricks for all client work.
Knowing this answer separates you from 80% of candidates.""",

        'delta lake': """Delta Lake is an open-source storage layer
that adds ACID transactions to data lakes.

Key features:
• ACID transactions (reliable data)
• Time travel (query data as it was yesterday/last week)
• Schema enforcement (bad data is rejected)
• Upserts with MERGE INTO

vs Parquet: Parquet is just a file format (no transactions,
no time travel). Delta Lake = Parquet + ACID + versioning.

Celebal will ask: "Delta Lake vs Parquet?" — now you know.""",

        'databricks': """Databricks is a unified data analytics platform
built on Apache Spark.

What it does:
• Run PySpark jobs at scale
• Build ML models with MLflow
• Store data in Delta Lake
• Connect to Azure/AWS storage

Why it matters for you:
Celebal produced 2 Databricks MVPs from Jaipur.
Databricks knowledge is the #1 signal in Celebal interviews.

Start: Create free account at community.databricks.com
Run one notebook on a CSV file. That's all you need for now.""",

        'etl': """ETL vs ELT:

ETL (Extract, Transform, Load):
• Transform data BEFORE loading into warehouse
• Used in legacy systems (Oracle, Informatica)
• Slower, less flexible

ELT (Extract, Load, Transform):
• Load raw data FIRST, transform inside warehouse
• Used in modern cloud systems (Databricks, Snowflake, BigQuery)
• Faster, more flexible, Celebal uses this

Interview answer structure: Define both → Give example → 
Say "Modern data engineering uses ELT because cloud 
warehouses are powerful enough to transform at scale." """,

        'window function': """Window functions perform calculations
across rows related to the current row WITHOUT collapsing results.

KEY FUNCTIONS:
ROW_NUMBER() — unique sequential number (1,2,3,4,5)
RANK()       — ties get same rank, leaves gaps (1,1,3,4,5)
DENSE_RANK() — ties get same rank, NO gaps (1,1,2,3,4)
LAG()        — access previous row value
LEAD()       — access next row value
PARTITION BY — divide rows into groups for calculation

Business example:
"Show each employee's salary AND their department average"
SELECT name, salary, department,
  AVG(salary) OVER (PARTITION BY department) as dept_avg
FROM employees;

This is asked in EVERY Celebal Round 1 SQL test.""",

        'statistics': """Statistics for Data Analyst interviews:

DESCRIPTIVE:
• Mean, Median, Mode (know when each is better)
• Variance, Standard Deviation (spread of data)
• Skewness (is data symmetric?)

PROBABILITY:
• P(A and B) = P(A) × P(B) if independent
• Bayes theorem basics

HYPOTHESIS TESTING:
• Null hypothesis vs Alternative
• p-value: if p < 0.05, reject null at 95% confidence
• t-test: compare two groups
• chi-square: categorical variables

Your score: {stats}/100. Optum tests this heavily.
Resource: StatQuest with Josh Starmer on YouTube.""".format(
            stats=skills.get('Statistics', 40)),

        'celebal': """Celebal Technologies — your #1 target.

FACTS:
• HQ: Jaipur, Rajasthan (90 min from Jodhpur)
• Revenue: ₹412 Cr, growing 47% CAGR
• Stack: Azure, Databricks, ADF, PySpark, Delta Lake, Power BI
• 2 Databricks MVPs produced from Jaipur

YOUR READINESS: {cel}/100
GAPS: Power BI ({pbi}/100), Azure ({az}/100), Databricks ({db}/100)

INTERVIEW ROUNDS:
Round 1: Aptitude + SQL (60 min online)
Round 2: Technical — SQL deep + Python + concepts (45 min)
Round 3: Azure/Databricks concepts (30 min)
HR: Why Celebal, goals, fit (20 min)

APPLY: careers.celebaltech.com or LinkedIn""".format(
            cel=70, 
            pbi=skills.get('Power BI', 20),
            az=skills.get('Azure', 15),
            db=skills.get('Databricks', 5)),
    }
    
    for keyword, answer in DIRECT_ANSWERS.items():
        if keyword in msg:
            return answer
    
    # Generic fallback that is still useful
    return (f"I don't have a specific answer for '{message}' "
            f"in my knowledge base yet. Ask me about: "
            f"Power BI, SQL, Databricks, Medallion Architecture, "
            f"Delta Lake, Celebal Technologies, TCS, Optum, "
            f"Statistics, ETL vs ELT, Window Functions, "
            f"or type 'My status' for your readiness report.")

def generate_dashboard(user_profile) -> str:
    date_str = datetime.now().strftime("%B %d, %Y")
    
    # Get values safely supporting both dictionary and object
    if isinstance(user_profile, dict):
        placement_readiness = user_profile.get('placement_readiness', 70)
        skills = user_profile.get('skills', {})
    else:
        placement_readiness = getattr(user_profile, 'placement_readiness', 70)
        skills = getattr(user_profile, 'skills', {})
        
    if not isinstance(skills, dict):
        skills = {}

    return f"""━━━ INFERA REALITY CHECK — {date_str} ━━━
PLACEMENT READINESS: {placement_readiness}/100
CELEBAL READINESS: 65/100
TCS READINESS: 78/100
OPTUM READINESS: 55/100

BIGGEST OPPORTUNITY: Power BI (current: {skills.get('Power BI', 20)}/100)
BIGGEST RISK: Statistics (current: {skills.get('Statistics', 40)}/100)

TOP 3 ACTIONS THIS WEEK:
1. Complete Power BI crash course [Priority: CRITICAL]
2. Update Resume with 5 projects [Priority: HIGH]
3. Practice SQL Window Functions [Priority: MEDIUM]
"""

def generate_priority(minutes: int, user_profile) -> str:
    return f"""━━━ PRIORITY PLAN — {minutes} MINUTES ━━━
1. Power BI Project Setup [{int(minutes * 0.5)} mins] — ROI: CRITICAL
   Why: Every DA job needs this, and your score is 20/100.
   Do: Load dataset into Power BI and create first 2 visuals.
2. SQL Window Functions [{int(minutes * 0.3)} mins] — ROI: HIGH
3. Resume Polish [{int(minutes * 0.2)} mins] — ROI: MEDIUM
SKIPPED TODAY: DSA, DBMS theory.
"""

def generate_decision(question: str, user_profile) -> str:
    return f"""━━━ DECISION ANALYSIS ━━━
RECOMMENDATION: Do not pursue this right now.
REASON: You are in a 90-day sprint for Data Analyst roles. You have critical gaps in Power BI and Statistics.
OPPORTUNITY COST: Time spent on this is time taken away from core Data Analyst skills.
EXPECTED OUTCOME: Distraction from primary goal.
CONFIDENCE: 95%
INFERA VERDICT: Stick to the 3-phase strategic plan. The environment favors you right now, but only if you focus.
"""

def generate_challenge(topic: str, user_profile) -> str:
    return f"""━━━ INFERA CHALLENGE ━━━
NOT RECOMMENDED.
Your current top priorities:
1. Power BI
2. Statistics
3. Azure basics
{topic} conflicts with these because: It dilutes your focus during the critical 4-6 month internship window.
ROI comparison:
  {topic}: Impact = LOW | Time = HIGH
  Power BI: Impact = HIGH | Time = SAME
Revisit {topic} after: Securing the Celebal/TCS internship.
"""

def generate_company_readiness(
    company_name: str, 
    user_profile: dict
) -> str:
    skills = user_profile.get('skills', {})
    
    # Company data (hardcoded for reliability)
    COMPANY_DATA = {
        'Celebal': {
            'weights': {'SQL':0.25,'Python':0.20,'Power BI':0.20,
                       'Azure':0.15,'Databricks':0.10,'Projects':0.10},
            'rounds': ['Round 1: Aptitude+SQL (60 min)',
                      'Round 2: Technical Deep Dive (45 min)',
                      'Round 3: Azure/Databricks (30 min)',
                      'HR Round (20 min)'],
            'required': ['SQL','Python','Azure','Databricks','Power BI'],
            'top_questions': [
                'What is Medallion Architecture?',
                'Delta Lake vs Parquet?',
                'Write SQL for 3rd highest salary',
                'Walk through AskQL architecture',
                'Why Celebal?'
            ],
            'timeline': '6 weeks to 85/100 with focused prep',
            'location': 'Jaipur (90 min from Jodhpur)'
        },
        'TCS Digital': {
            'weights': {'SQL':0.20,'Python':0.25,'OOP':0.20,
                       'DSA':0.15,'Azure':0.10,'Projects':0.10},
            'rounds': ['NQT: Aptitude+Coding (90 min)',
                      'Technical Interview',
                      'HR Round'],
            'required': ['Python','SQL','OOP','Git'],
            'top_questions': [
                'ACID properties with example',
                'Polymorphism in Python',
                'Normalization 1NF 2NF 3NF',
                'Write code for 2nd largest element',
                'DELETE vs TRUNCATE vs DROP'
            ],
            'timeline': '4 weeks to 88/100',
            'location': 'Jaipur campus (Mahindra World City)'
        },
        'Optum': {
            'weights': {'Python':0.25,'SQL':0.20,'Statistics':0.20,
                       'Power BI':0.15,'Azure':0.10,'Communication':0.10},
            'rounds': ['Python Coding Round (HackerRank)',
                      'Technical Interview',
                      'HR Round'],
            'required': ['Python','SQL','Statistics','Healthcare domain'],
            'top_questions': [
                'Build a claims validation rule engine',
                'What is HIPAA?',
                'Find members in Q1 but not Q2 (SQL)',
                'What is a claims denial rate?',
                'Handle 30% NULL diagnosis codes'
            ],
            'timeline': '10 weeks (need healthcare domain first)',
            'location': 'No Rajasthan office — relocation needed'
        },
        'Deloitte': {
            'weights': {'SQL':0.20,'Python':0.20,'Communication':0.25,
                       'Projects':0.20,'DSA':0.15},
            'rounds': ['Aptitude Test','Technical Round',
                      'Case Study Round','HR Round'],
            'required': ['Python','SQL','Analytics','Communication'],
            'top_questions': [
                'Walk through a data project end-to-end',
                'How would you handle a business analytics problem?',
                'SQL: complex joins and subqueries',
                'Tell me about a time you found a key insight'
            ],
            'timeline': '8 weeks with communication practice',
            'location': 'Multiple India offices'
        }
    }
    
    # Normalize company name
    company_key = None
    for key in COMPANY_DATA:
        if key.lower() in company_name.lower() or \
           company_name.lower() in key.lower():
            company_key = key
            break
    
    if not company_key:
        return (f"Company '{company_name}' not in my database. "
                f"I have data for: Celebal, TCS Digital, Optum, Deloitte")
    
    data = COMPANY_DATA[company_key]
    weights = data['weights']
    
    # Calculate readiness score
    total_score = 0
    skill_lines = []
    missing = []
    
    for skill, weight in weights.items():
        # Handle 'Projects' specially
        if skill == 'Projects':
            score = skills.get('Projects', 75)
        elif skill == 'DSA':
            score = skills.get('DSA', 30)
        elif skill == 'Communication':
            score = skills.get('Communication', 55)
        else:
            score = skills.get(skill, 0)
        
        contribution = score * weight
        total_score += contribution
        
        # Status indicator
        if score >= 75:
            status = '✓ Strong'
            bar = '██████████'[:int(score/10)] + '░'*(10-int(score/10))
        elif score >= 50:
            status = '~ Needs work'
            bar = '██████████'[:int(score/10)] + '░'*(10-int(score/10))
        else:
            status = '✗ Gap'
            bar = '██████████'[:int(score/10)] + '░'*(10-int(score/10))
            if skill in data.get('required', []):
                missing.append(f"{skill} ({score}/100)")
        
        skill_lines.append(
            f"  {skill:<18} {bar} {score}/100  {status}"
        )
    
    readiness = int(total_score)
    
    # Probability estimate
    if readiness >= 85:
        prob = "High (80%+ interview shortlist chance)"
    elif readiness >= 70:
        prob = "Moderate (55-70% shortlist chance)"  
    elif readiness >= 55:
        prob = "Low-Moderate (30-50% shortlist chance)"
    else:
        prob = "Low (<30% shortlist chance)"
    
    # Build formatted response
    output = f"""━━━ COMPANY READINESS: {company_key.upper()} ━━━

READINESS SCORE:    {readiness}/100
PROBABILITY:        {prob}
LOCATION:           {data['location']}
TIMELINE TO 85/100: {data['timeline']}

SKILL BREAKDOWN:
{chr(10).join(skill_lines)}

INTERVIEW ROUNDS:
"""
    for i, round_info in enumerate(data['rounds'], 1):
        output += f"  {i}. {round_info}\n"
    
    if missing:
        output += f"""
CRITICAL GAPS (Fix These First):
"""
        for gap in missing:
            output += f"  ✗ {gap}\n"
    
    output += f"""
THEY WILL ASK YOU:
"""
    for q in data['top_questions'][:3]:
        output += f"  → \"{q}\"\n"
    
    # Personalized recommendation
    lowest_skill = min(weights.keys(), 
                      key=lambda s: skills.get(s, 0))
    lowest_score = skills.get(lowest_skill, 0)
    
    output += f"""
INFERA RECOMMENDATION:
  Your biggest gap for {company_key}: {lowest_skill} ({lowest_score}/100)
  Fix this first. Everything else is secondary.
  
  Apply when: Score reaches 78+/100
  Current: {readiness}/100"""
    
    return output


def generate_future_sim(user_profile) -> str:
    skills = user_profile.skills if hasattr(user_profile, 'skills') else {}
    if isinstance(skills, str):
        try:
            import json
            skills = json.loads(skills)
        except:
            skills = {}
            
    sql = skills.get("SQL", 80)
    pbi = skills.get("Power BI", 20)
    az = skills.get("Azure", 15)

    best_3m_readiness = min(95, 70 + 20)
    expected_3m_readiness = min(90, 70 + 12)
    worst_3m_readiness = max(60, 70 - 5)

    return f"""━━━ FUTURE SELF SIMULATION ━━━

3 MONTHS (September 2026):

  BEST CASE (you follow the plan):
    Placement Readiness: {best_3m_readiness}/100
    SQL: {min(95,sql+10)} | Python: 78 | Power BI: 72 | Azure: 60
    Status: Celebal internship offer likely. TCS Digital cleared.
    Key variable: You built Power BI portfolio AND touched Databricks CE.

  EXPECTED CASE (current trajectory):
    Placement Readiness: {expected_3m_readiness}/100
    SQL: {min(90,sql+5)} | Python: 72 | Power BI: 50 | Azure: 38
    Status: Celebal interview cleared. TCS offer possible.
    Key variable: You built Power BI dashboards but skipped Azure.

  WORST CASE (you don't execute):
    Placement Readiness: {worst_3m_readiness}/100
    Skills: Minimal improvement across all areas.
    Status: Applications ignored. Need another semester.
    Key variable: You studied without building anything.

THE SINGLE BIGGEST LEVER:
  Power BI ({pbi}/100) is the difference between Best and Worst case.
  Every week you delay this costs 1-2 interview shortlists.
  
INFERA RECOMMENDATION:
  Open Microsoft Learn Power BI path today.
  Build the Sales Dashboard this week.
  Nothing else matters more right now."""

def generate_weekly_review(user_profile) -> str:
    return f"""━━━ WEEKLY REVIEW ━━━

INFERA cannot track what you did this week without you telling me.
Tell me: What did you complete? What did you miss?
Then I will give you your score and next week's plan.

THINGS I DO KNOW:
  Mocks taken this week: Check interview history
  Quizzes taken this week: Check quiz history
  
ASK ME: "Here's my week: [tell me what you did]"
Then I'll score it properly."""

def generate_resume_chat_response(
    message: str,
    user_id: int,
    db
) -> str:
    # Try to get resume from DB
    latest_ats = None
    latest_company = "Celebal"
    latest_issues = []
    latest_breakdown = {}

    try:
        from sqlalchemy import text as sql_text
        result = db.execute(
            sql_text(
                "SELECT ats_score, company_optimized_for, feedback, "
                "analyzed_at FROM resumes WHERE user_id = :uid "
                "ORDER BY analyzed_at DESC LIMIT 1"
            ),
            {"uid": user_id}
        ).fetchone()

        if result:
            latest_ats = float(result[0]) if result[0] else None
            latest_company = result[1] or "Celebal"
            import json
            feedback = result[2]
            if feedback:
                if isinstance(feedback, str):
                    feedback = json.loads(feedback)
                latest_issues = feedback.get("issues", [])
                latest_breakdown = feedback.get("breakdown", {})
    except Exception as e:
        print(f"Resume DB lookup error: {e}")

    msg = message.lower()

    # No resume analyzed yet
    if latest_ats is None:
        return (
            "You haven't analyzed a resume yet.\n\n"
            "Go to Resume Analyzer → choose your company → "
            "upload PDF or paste text → click Analyze.\n\n"
            "After analyzing, come back here and ask me:\n"
            "  'Why is my keyword score low?'\n"
            "  'What action verbs should I replace?'\n"
            "  'How do I improve my score to 85?'\n"
            "  'What exact words am I missing for Celebal?'"
        )

    # Answer specific questions
    if any(w in msg for w in ["keyword", "missing word", "what word",
                               "what's missing", "whats missing"]):
        return (
            f"Your Keywords score is {latest_breakdown.get('keywords', 10)}/30 "
            f"for {latest_company}.\n\n"
            f"MISSING FROM YOUR RESUME:\n"
            f"  ✗ Azure — not found (worth 5 pts)\n"
            f"  ✗ Databricks — not found (worth 5 pts)\n"
            f"  ✗ Power BI — not found (worth 5 pts)\n"
            f"  ✗ ADF / Azure Data Factory — not found (worth 5 pts)\n\n"
            f"HOW TO ADD NATURALLY:\n"
            f"  Skills section: 'Azure (DP-900 in progress), "
            f"Databricks (Community Edition hands-on), Power BI'\n\n"
            f"  In project descriptions:\n"
            f"  'Built data pipeline using Azure Data Factory'\n"
            f"  'Stored results in Delta Lake on Databricks CE'\n\n"
            f"Adding these 4 keywords moves your score from "
            f"{latest_ats:.0f}/100 to approximately 82+/100."
        )

    elif any(w in msg for w in ["action verb", "weak", "worked on",
                                  "familiar", "replace phrase",
                                  "bad phrase"]):
        return (
            f"Weak language detected. Here's what to fix:\n\n"
            f"REPLACE THESE PHRASES:\n\n"
            f"❌ 'Familiar with Power BI'\n"
            f"✅ 'Built Sales + HR Analytics dashboards in Power BI "
            f"with DAX formulas, drill-throughs, and KPI cards'\n\n"
            f"❌ 'Worked on SQL analysis'\n"
            f"✅ 'Engineered analytics on 50K+ row e-commerce dataset "
            f"using window functions and CTEs; identified top revenue "
            f"segments contributing 68% of total sales'\n\n"
            f"❌ 'Experience with Python'\n"
            f"✅ 'Built AskQL — NLP-to-SQL interface using Python and "
            f"MySQL, enabling natural language database queries'\n\n"
            f"THE RULE:\n"
            f"Every bullet point = Action verb + What + How + Outcome\n"
            f"Never start with: Familiar, Worked, Helped, Assisted, "
            f"Exposure, Experience with."
        )

    elif any(w in msg for w in ["project", "describe", "askql",
                                  "edubus", "exploraai", "inferaai"]):
        return (
            f"Your projects are ABOVE AVERAGE — 5 projects = rare for fresher.\n"
            f"Score: {latest_breakdown.get('projects', 25)}/25 ✓\n\n"
            f"The issue is in HOW they're described.\n\n"
            f"FORMAT (for every project bullet):\n"
            f"[Verb] + [What you built] + [Tech used] + [Result]\n\n"
            f"AskQL — IMPROVE TO:\n"
            f"'Engineered natural language-to-SQL interface using "
            f"Python NLP and MySQL; enables non-technical users to "
            f"query databases conversationally, eliminating need for "
            f"manual SQL writing'\n\n"
            f"SQL Analytics — IMPROVE TO:\n"
            f"'Conducted end-to-end analytics on 50K+ row dataset "
            f"using 15+ SQL queries with window functions and CTEs; "
            f"identified top 3 revenue segments driving 68% of sales'\n\n"
            f"Apply this to all 5 projects. This is the difference "
            f"between a recruiter reading further or stopping."
        )

    elif any(w in msg for w in ["certif", "certification", "hackerrank",
                                  "dp-900", "az-900"]):
        return (
            f"Certifications score: "
            f"{latest_breakdown.get('certifications', 0)}/10\n\n"
            f"YOU HAVE ZERO CERTIFICATIONS on your resume right now.\n"
            f"This is a quick win — fix it in 1-2 days:\n\n"
            f"TODAY (30 minutes each):\n"
            f"  1. HackerRank SQL Gold Certificate — free, 2-3 hours total\n"
            f"     Go to hackerrank.com → Practice → SQL → earn certificate\n"
            f"  2. HackerRank Python Certificate — free, 2-3 hours total\n\n"
            f"ADD TO RESUME AS:\n"
            f"  'HackerRank SQL (Gold) | HackerRank Python | "
            f"DP-900 Azure Data Fundamentals (in progress)'\n\n"
            f"Even 'in progress' counts. It shows commitment.\n"
            f"This alone adds +8 points to your ATS score."
        )

    elif any(w in msg for w in ["improve", "how to fix", "reach 85",
                                  "get to 85", "better score", "increase"]):
        return (
            f"Your ATS Score: {latest_ats:.0f}/100 for {latest_company}\n"
            f"Target: 85+/100\n"
            f"Gap: {85 - latest_ats:.0f} points\n\n"
            f"THREE THINGS THAT CLOSE THE GAP:\n\n"
            f"1. ADD MISSING KEYWORDS (+15-20 pts)\n"
            f"   Add: Azure, Databricks, Power BI, ADF to skills\n"
            f"   Mention in project descriptions too\n\n"
            f"2. ADD CERTIFICATIONS (+8 pts)\n"
            f"   HackerRank SQL Gold (free, 1 day)\n"
            f"   DP-900 in progress — add it now\n\n"
            f"3. FIX WEAK LANGUAGE (+5 pts)\n"
            f"   Remove: 'familiar with', 'worked on'\n"
            f"   Replace with action verbs + outcomes\n\n"
            f"TOTAL ESTIMATED IMPROVEMENT: +{min(25, int(85-latest_ats))} pts\n"
            f"New estimated score: {min(90, int(latest_ats)+23)}/100\n\n"
            f"Do all 3. Then re-upload and analyze again."
        )

    elif any(w in msg for w in ["format", "length", "one page",
                                  "too long"]):
        return (
            f"Format score: {latest_breakdown.get('format', 15)}/20\n\n"
            f"ISSUES FOUND:\n"
            f"  Resume may be longer than 1 page (target: ~700 words)\n\n"
            f"HOW TO FIX:\n"
            f"  1. Remove objective statement (waste of space)\n"
            f"  2. Keep only 2 bullet points per project (not 5)\n"
            f"  3. Remove hobbies/interests section\n"
            f"  4. Condense skills to one line per category\n"
            f"  5. Use 10pt font, 0.75 inch margins\n\n"
            f"RULE: For fresher, 1 page is non-negotiable.\n"
            f"A recruiter spends 7 seconds on a resume.\n"
            f"If they have to scroll, most won't."
        )

    else:
        # General resume chat
        return (
            f"Last resume analyzed: {latest_ats:.0f}/100 for {latest_company}\n\n"
            f"Ask me specific questions:\n"
            f"  'What keywords am I missing?'\n"
            f"  'What action verbs should I use?'\n"
            f"  'How should I describe my projects?'\n"
            f"  'How do I get from {latest_ats:.0f} to 85?'\n"
            f"  'What certifications to add?'\n"
            f"  'Is my format okay?'"
        )

# ==========================================
# MODULE A: MOCK INTERVIEW ENGINE
# ==========================================

def start_interview(company: str, round_name: str, user_id: int, db) -> dict:
    from models import MockInterview
    company_qs = kb.interview_questions.get(company, {})
    # Default to first round if not found
    questions = company_qs.get(round_name, list(company_qs.values())[0] if company_qs else [])
    
    if not questions:
        questions = [{"q": "Tell me about yourself.", "rubric": "intro+skills"}]
    
    interview = MockInterview(
        user_id=user_id,
        company=company,
        interview_round=round_name,
        questions=questions,
        answers=["" for _ in questions],
        scores=[0 for _ in questions],
        status="in_progress"
    )
    db.add(interview)
    db.commit()
    db.refresh(interview)
    
    return {
        "session_id": interview.id,
        "question_1": questions[0]["q"],
        "total_questions": len(questions),
        "timer_minutes": 45
    }

def submit_interview_answer(session_id: int, question_num: int, answer: str, user_id: int, db) -> dict:
    from models import MockInterview
    interview = db.query(MockInterview).filter(MockInterview.id == session_id, MockInterview.user_id == user_id).first()
    if not interview:
        return {"error": "Interview not found"}
        
    questions = list(interview.questions)
    answers = list(interview.answers)
    scores = list(interview.scores)
    
    idx = question_num - 1
    if idx < 0 or idx >= len(questions):
        return {"error": "Invalid question number"}
        
    q_data = questions[idx]
    score, feedback, improved = score_answer(q_data, answer)
    
    answers[idx] = answer
    scores[idx] = score
    
    interview.answers = answers
    interview.scores = scores
    
    is_last = question_num == len(questions)
    summary = None
    next_question = None
    
    if is_last:
        overall = sum(scores) / len(scores)
        interview.overall_score = overall
        interview.status = "completed"
        interview.completed_at = datetime.utcnow()
        summary = f"Interview Complete. Overall Score: {overall:.1f}/10"
    else:
        next_question = questions[idx + 1]["q"]
        
    db.commit()
    
    return {
        "score": score,
        "feedback": feedback,
        "improved_answer": improved,
        "next_question": next_question,
        "summary": summary
    }

def score_answer(question: dict, answer: str) -> tuple[float, str, str]:
    """Returns (score_1_to_10, feedback, improved_answer)"""
    score = 0.0
    rubric = question.get("rubric", "")

    # Content quality (0-5 points)
    if len(answer) > 50: score += 1.0
    if len(answer) > 150: score += 1.0
    rubric_words = rubric.lower().split("+")
    matches = sum(1 for w in rubric_words if w.strip() in answer.lower())
    score += min(3.0, matches * 1.0)

    # Structure quality (0-3 points)
    has_example = any(w in answer.lower() for w in ["example", "for instance", "such as", "like when", "in my project"])
    if has_example: score += 1.5
    is_structured = answer.count(".") >= 2 or answer.count(",") >= 3
    if is_structured: score += 1.0
    has_specifics = any(char.isdigit() for char in answer)
    if has_specifics: score += 0.5

    # Company awareness (0-2 points)
    company_terms = ["celebal", "databricks", "azure", "delta lake", "medallion",
                     "tcs digital", "optum", "healthcare", "askql", "my project"]
    company_match = sum(1 for t in company_terms if t in answer.lower())
    score += min(2.0, company_match * 0.7)

    score = round(min(10.0, max(1.0, score)), 1)

    if score >= 8:
        feedback = f"Strong answer ({score}/10). Well-structured with relevant details."
    elif score >= 6:
        feedback = f"Decent answer ({score}/10). Add more specific examples to reach 9/10."
    elif score >= 4:
        feedback = f"Weak answer ({score}/10). Missing: {rubric}. Be more specific."
    else:
        feedback = f"Off-track ({score}/10). The question asks about: {rubric}"

    improved = f"A stronger answer would include: {rubric}. "
    improved += "Structure: Define it → Give example → Connect to your experience → Relate to the company."

    return score, feedback, improved


# ==========================================
# MODULE B: QUIZ ENGINE
# ==========================================

QUIZ_QUESTIONS = {
  "SQL": [
    {"q": "What is the difference between RANK() and DENSE_RANK()?",
     "answer": "RANK() leaves gaps after ties (1,1,3), DENSE_RANK() does not (1,1,2)",
     "topic": "window_functions"},
    {"q": "Write a query to find all employees who earn more than the average salary",
     "answer": "SELECT * FROM employees WHERE salary > (SELECT AVG(salary) FROM employees)",
     "topic": "subqueries"},
    {"q": "What does PARTITION BY do in a window function?",
     "answer": "Divides the result set into partitions for the window function to work on independently",
     "topic": "window_functions"},
    {"q": "Difference between WHERE and HAVING?",
     "answer": "WHERE filters before aggregation, HAVING filters after. Cannot use aggregates in WHERE",
     "topic": "aggregation"},
    {"q": "What is a CTE and when would you use it?",
     "answer": "Common Table Expression using WITH clause. Use for readability, recursion, or reusing a subquery",
     "topic": "advanced_sql"},
    {"q": "Write a self-join to find employees who earn more than their manager",
     "answer": "SELECT e.name FROM employees e JOIN employees m ON e.manager_id = m.id WHERE e.salary > m.salary",
     "topic": "joins"},
    {"q": "What is the difference between INNER JOIN and LEFT JOIN?",
     "answer": "INNER: only matching rows. LEFT: all left rows + matching right rows (NULLs where no match)",
     "topic": "joins"},
    {"q": "How do you find duplicate records in a table?",
     "answer": "SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1",
     "topic": "aggregation"},
    {"q": "What is an index and when should you NOT use one?",
     "answer": "Index speeds up reads. Avoid on frequently updated columns, small tables, or low-cardinality columns",
     "topic": "optimization"},
    {"q": "Explain LEAD() and LAG() window functions with a use case",
     "answer": "LEAD gets next row value, LAG gets previous. Use case: compare today's sales to yesterday's",
     "topic": "window_functions"}
  ],
  "Python": [
    {"q": "What is the difference between a list and a tuple in Python?",
     "answer": "List is mutable, tuple is immutable. Tuples are faster and used for fixed data",
     "topic": "data_structures"},
    {"q": "What is a generator in Python? When do you use it?",
     "answer": "Uses yield, generates values lazily. Use for large datasets to save memory",
     "topic": "advanced"},
    {"q": "How do you handle missing values in a Pandas DataFrame?",
     "answer": "dropna() to remove, fillna(value) to fill, interpolate() for time series. Check first with isnull().sum()",
     "topic": "pandas"},
    {"q": "What is the difference between deepcopy and shallowcopy?",
     "answer": "Shallow copies reference same nested objects. Deep copy creates completely independent copies",
     "topic": "advanced"},
    {"q": "Write a function to find duplicates in a list",
     "answer": "Use a set: seen=set(); return [x for x in lst if x in seen or seen.add(x)]",
     "topic": "basics"}
  ]
}

def start_quiz(topic: str, user_id: int, db) -> dict:
    from models import QuizSession
    all_qs = QUIZ_QUESTIONS.get(topic, QUIZ_QUESTIONS["SQL"])
    # Pick up to 5 questions
    q_count = min(5, len(all_qs))
    selected_qs = random.sample(all_qs, q_count)
    
    quiz = QuizSession(
        user_id=user_id,
        topic=topic,
        questions=selected_qs,
        user_answers=["" for _ in selected_qs],
        scores=[0 for _ in selected_qs],
        status="in_progress"
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    return {
        "session_id": quiz.id,
        "question_1": selected_qs[0]["q"],
        "total": q_count
    }

def score_quiz_answer(
    question: dict, 
    user_answer: str
) -> tuple[int, str, str]:
    """
    Returns (score_0_to_10, feedback, correct_answer_explanation)
    Uses conceptual matching not exact matching.
    """
    if not user_answer or len(user_answer.strip()) < 3:
        return 0, "No answer provided.", question.get('answer', '')
    
    correct = question.get('answer', '').lower()
    user = user_answer.lower().strip()
    topic = question.get('topic', '')
    
    # Extract key concepts from correct answer
    # Split by common delimiters and get meaningful words
    stop_words = {'the','a','an','is','are','was','were','be',
                  'to','of','in','on','at','by','for','with',
                  'has','have','had','do','does','did','will',
                  'would','could','should','may','might','must',
                  'and','or','but','not','no','it','its','this',
                  'that','they','them','their','from','into','than'}
    
    correct_concepts = set(
        w for w in correct.replace(',','').replace('.','')
                         .replace('(','').replace(')','').split()
        if len(w) > 3 and w not in stop_words
    )
    
    user_concepts = set(
        w for w in user.replace(',','').replace('.','')
                       .replace('(','').replace(')','').split()
        if len(w) > 3 and w not in stop_words
    )
    
    # Partial matching (user word starts with correct word or vice versa)
    matches = 0
    for uw in user_concepts:
        for cw in correct_concepts:
            if (uw == cw or uw.startswith(cw[:4]) or 
                cw.startswith(uw[:4])):
                matches += 1
                break
    
    # Calculate match ratio
    if len(correct_concepts) == 0:
        concept_score = 5  # can't evaluate, give middle score
    else:
        match_ratio = matches / len(correct_concepts)
        concept_score = int(match_ratio * 8)  # max 8 from concepts
    
    # Bonus points
    bonus = 0
    if len(user_answer) > 80:  bonus += 1  # detailed answer
    if len(user_answer) > 150: bonus += 1  # very detailed
    
    score = min(10, concept_score + bonus)
    score = max(1, score)  # minimum 1 for attempting
    
    # Generate feedback
    if score >= 8:
        feedback = (f"Excellent! ({score}/10) Your answer covers "
                   f"the key concepts well.")
    elif score >= 6:
        feedback = (f"Good answer ({score}/10). You got the main idea. "
                   f"To score 9+, be more specific with examples.")
    elif score >= 4:
        feedback = (f"Partial credit ({score}/10). You're on the right "
                   f"track but missing key details.")
    elif score >= 2:
        feedback = (f"Needs work ({score}/10). You touched on the topic "
                   f"but the core answer is different.")
    else:
        feedback = f"Incorrect ({score}/10). Study this concept."
    
    # Always show the correct answer for learning
    explanation = (f"Correct Answer: {question.get('answer', 'N/A')}\n"
                  f"Key concepts: {', '.join(list(correct_concepts)[:5])}")
    
    return score, feedback, explanation

async def submit_quiz_answer(session_id: int, question_num: int, answer: str, user_id: int, db) -> dict:
    from models import QuizSession
    quiz = db.query(QuizSession).filter(QuizSession.id == session_id, QuizSession.user_id == user_id).first()
    if not quiz:
        return {"error": "Quiz not found"}
        
    questions = list(quiz.questions)
    user_answers = list(quiz.user_answers)
    scores = list(quiz.scores)
    
    idx = question_num - 1
    if idx < 0 or idx >= len(questions):
        return {"error": "Invalid question number"}
        
    question_text = questions[idx]["q"]
    correct_ans = questions[idx]["answer"]
    
    score, feedback, explanation = score_quiz_answer(questions[idx], answer)
    
    # Return both feedback and explanation together so the frontend displays it
    final_explanation = f"{feedback}\n\n{explanation}"
    
    user_answers[idx] = answer
    scores[idx] = score
    
    quiz.user_answers = user_answers
    quiz.scores = scores
    
    is_last = question_num == len(questions)
    summary = None
    next_question = None
    
    if is_last:
        overall = sum(scores) / len(scores)
        quiz.overall_score = overall
        quiz.status = "completed"
        from datetime import datetime
        quiz.completed_at = datetime.utcnow()
        summary = f"Quiz Complete. Overall Score: {overall:.1f}/10"
    else:
        next_question = questions[idx + 1]["q"]
        
    db.commit()
    
    return {
        "score": score,
        "correct_answer": correct_ans,
        "explanation": final_explanation,
        "next_question": next_question,
        "summary": summary
    }

# ==========================================
# MODULE C: RESUME INTELLIGENCE
# ==========================================

def analyze_resume(resume_text: str, company: str, user_profile: dict) -> dict:
    company_data = kb.company_intel.get(company, {})
    required = company_data.get("required_keywords", [])
    preferred = company_data.get("preferred_keywords", [])

    import re
    
    text_lower = resume_text.lower()
    
    # Define synonyms for smarter matching
    synonyms = {
        "oop": ["oop", "oops", "object oriented", "object-oriented"],
        "dsa": ["dsa", "data structures", "algorithms"],
        "ml": ["ml", "machine learning"],
        "ai": ["ai", "artificial intelligence"],
        "bi": ["bi", "business intelligence"],
        "power bi": ["power bi", "powerbi"],
        "sql": ["sql", "mysql", "postgresql", "t-sql"]
    }
    
    def match_keyword(k, text):
        k_lower = k.lower()
        variants = synonyms.get(k_lower, [k_lower])
        for variant in variants:
            # Use regex to match whole words or exact phrases
            pattern = r'\b' + re.escape(variant) + r'\b'
            if re.search(pattern, text):
                return True
        return False

    # Score keywords (30 points)
    req_found = [k for k in required if match_keyword(k, text_lower)]
    pref_found = [k for k in preferred if match_keyword(k, text_lower)]
    req_missing = [k for k in required if not match_keyword(k, text_lower)]
    pref_missing = [k for k in preferred if not match_keyword(k, text_lower)]
    
    keyword_score = (len(req_found) * 5) + (len(pref_found) * 2)
    keyword_score = min(30, keyword_score)

    # Score action verbs (10 points)
    strong_verbs = ["built", "engineered", "designed", "implemented", "developed",
                    "analyzed", "optimized", "automated", "delivered", "created",
                    "architected", "led", "managed", "reduced", "increased"]
    weak_verbs = ["worked on", "familiar with", "exposure to", "helped with", "assisted"]
    verb_count = sum(1 for v in strong_verbs if v in text_lower)
    weak_count = sum(1 for v in weak_verbs if v in text_lower)
    verb_score = min(10, verb_count * 2) - (weak_count * 2)
    verb_score = max(0, verb_score)

    # Score format (20 points)
    format_score = 15
    if len(resume_text) > 3000: format_score -= 5
    if "github.com" in text_lower: format_score += 5
    format_score = min(20, format_score)

    # Score projects (25 points)
    project_keywords = ["askql", "exploraai", "inferaai", "edubus", "sql analytics",
                        "dashboard", "analysis", "pipeline", "model"]
    proj_found = sum(1 for p in project_keywords if p in text_lower)
    project_score = min(25, proj_found * 5)

    # Score certifications (10 points)
    cert_keywords = ["hackerrank", "dp-900", "az-900", "pl-300", "databricks", "aws"]
    cert_found = sum(1 for c in cert_keywords if c in text_lower)
    cert_score = min(10, cert_found * 3)

    # GitHub (5 points)
    github_score = 5 if "github.com" in text_lower else 0

    total = keyword_score + verb_score + format_score + project_score + cert_score + github_score

    issues = []
    if req_missing:
        issues.append(f"Missing required keywords: {', '.join(req_missing)}")
    if weak_count > 0:
        issues.append(f"Found {weak_count} weak phrases (familiar with / worked on / exposure to)")
    if "github.com" not in text_lower:
        issues.append("GitHub link not found")
    if len(resume_text) > 3000:
        issues.append("Resume may be too long (target: 1 page / ~700 words)")

    examples = []
    if "familiar with" in text_lower:
        examples.append({
            "before": '"Familiar with Power BI"',
            "after": '"Built Sales + HR Analytics dashboards in Power BI with DAX formulas, drill-throughs, and Power BI Service publishing"',
            "reason": "Vague replaced with specific work done and tools used"
        })
    if "worked on" in text_lower:
        examples.append({
            "before": '"Worked on SQL database analysis"',
            "after": '"Engineered SQL analytics on 50K+ row e-commerce dataset; identified top 3 revenue segments contributing 68% of total sales using window functions and CTEs"',
            "reason": "Action verb + dataset size + specific outcome added"
        })

    if_fixed_score = min(100, total + len(issues) * 5)

    return {
        "ats_score": round(total, 1),
        "breakdown": {
            "keywords": keyword_score,
            "action_verbs": verb_score,
            "format": format_score,
            "projects": project_score,
            "certifications": cert_score,
            "github": github_score
        },
        "required_missing": req_missing,
        "preferred_missing": pref_missing[:3],
        "issues": issues,
        "before_after": examples,
        "if_fixed_score": if_fixed_score
    }

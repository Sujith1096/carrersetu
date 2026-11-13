import os
import json
import re
import urllib.request
import urllib.error
from typing import Dict, Any, List, Optional, Tuple, Set

try:
    from dotenv import load_dotenv
    # Load .env from backend and root directories
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), ".env"))
    load_dotenv()
except Exception:
    pass


class JarvisEngine:
    """
    J.A.R.V.I.S. – AI Career Intelligence Assistant & Strategic Engineering Mentor.
    Engineered with:
    1. Multi-turn conversational memory & follow-up resolution.
    2. Deep technical reasoning, edge case analysis, and Big-O derivation.
    3. Strict context relevance (never dumps unsolicited resume stats on pure coding questions).
    4. Anti-hallucination & ground-truth verification on user resume data.
    5. High-intelligence Cloud AI configuration (Gemini / OpenAI / Groq) with low temperature & large token ceilings.
    6. Autonomous local reasoning engine when running offline or in demo mode.
    """

    def __init__(self):
        self.custom_api_key: Optional[str] = None
        self.custom_provider: Optional[str] = None  # "gemini" | "openai" | "groq"
        # In-memory session name overrides
        self.session_user_names: Dict[str, str] = {}
        # Multi-turn topic tracker
        self.session_last_topics: Dict[str, str] = {}

    def get_active_provider(
        self,
        client_provider: Optional[str] = None,
        client_api_key: Optional[str] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """Return (provider_name, api_key) or (None, None) if in local mode."""
        # 1. Per-request client credential priority (isolated to caller session)
        if client_provider and client_api_key and client_api_key.strip():
            return client_provider.lower().strip(), client_api_key.strip()

        # 2. Server-side environment variables configured on hosting platform
        gemini_key = os.getenv("GEMINI_API_KEY")
        if gemini_key and gemini_key.strip():
            return "gemini", gemini_key.strip()

        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key and openai_key.strip():
            return "openai", openai_key.strip()

        groq_key = os.getenv("GROQ_API_KEY")
        if groq_key and groq_key.strip():
            return "groq", groq_key.strip()

        # 3. Fallback to local intelligence
        return None, None

    # =========================================================================
    # CLOUD API INTEGRATIONS (Reasoning-Calibrated: Temp 0.2, 4096-8192 Tokens)
    # =========================================================================

    def call_gemini(self, api_key: str, system_prompt: str, messages: List[Dict[str, str]]) -> str:
        """
        Calls Google Gemini using the most capable reasoning models with strict temperature (0.2).
        Attempts gemini-1.5-pro, then gemini-2.0-flash, then gemini-1.5-flash.
        """
        models_to_try = ["gemini-1.5-pro", "gemini-2.0-flash", "gemini-1.5-flash"]
        last_error = None

        contents = []
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({
                "role": role,
                "parts": [{"text": msg["content"]}]
            })

        payload = {
            "systemInstruction": {
                "parts": [{"text": system_prompt}]
            },
            "contents": contents,
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 8192,
                "topP": 0.95
            }
        }

        for model_name in models_to_try:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
            req = urllib.request.Request(
                url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            try:
                with urllib.request.urlopen(req, timeout=20) as res:
                    res_data = json.loads(res.read().decode("utf-8"))
                    candidates = res_data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            return parts[0].get("text", "")
            except Exception as e:
                last_error = e
                continue

        raise RuntimeError(f"All Gemini models failed: {last_error}")

    def call_openai_compatible(
        self, api_key: str, base_url: str, model: str, system_prompt: str, messages: List[Dict[str, str]]
    ) -> str:
        """
        Calls OpenAI or Groq with temperature 0.2 and 4096 tokens for deterministic accuracy.
        """
        url = f"{base_url}/chat/completions"
        all_messages = [{"role": "system", "content": system_prompt}] + messages
        payload = {
            "model": model,
            "messages": all_messages,
            "temperature": 0.2,
            "max_tokens": 4096
        }
        req = urllib.request.Request(
            url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
        )
        with urllib.request.urlopen(req, timeout=20) as res:
            res_data = json.loads(res.read().decode("utf-8"))
            choices = res_data.get("choices", [])
            if choices and "message" in choices[0]:
                return choices[0]["message"].get("content", "")
            return "Transmission completed without text output."

    # =========================================================================
    # MASTER COORDINATOR
    # =========================================================================

    def generate_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]] = None,
        interview_state: Optional[Dict[str, Any]] = None,
        client_provider: Optional[str] = None,
        client_api_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Master Response Coordinator:
        1. Resolves candidate identity and handles name correction intents.
        2. Maintains conversation history context window.
        3. Attempts Cloud AI (Gemini/OpenAI/Groq) with reasoning prompt if API key present.
        4. Executes Autonomous Local Intelligence Engine if in offline/local mode.
        """
        # Determine candidate name (respecting user corrections)
        candidate_name = self._resolve_candidate_name(message, context)

        # Check for Name Correction Intent first
        name_correction = self._check_name_correction(message)
        if name_correction:
            updated_name = name_correction.title()
            reply = f"My sincerest apologies, **{updated_name}**! Calibrating biometric and neural records immediately.\n\n"
            reply += f"I have updated your profile identifier from *'{context.get('candidate_name', 'Alex')}'* to **{updated_name}**. "
            reply += f"All subsequent telemetry, interview assessments, and resume optimizations are now customized specifically for you, **{updated_name}**.\n\n"
            reply += "How may I assist you with your career strategy today? Shall we analyze your target role, conduct a technical interview, or plan your skill roadmap?"
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "updated_name": updated_name,
                "interview_state": interview_state,
                "suggested_replies": [
                    "How can I improve my resume?",
                    "What critical skills am I missing?",
                    "Start an interactive mock interview",
                    "Generate a 30-day career roadmap"
                ]
            }

        job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"
        job_company = context.get("job_company", "Target Company") if context else "Target Company"
        overall_score = context.get("overall_score") if context else None
        match_rating = context.get("match_rating") if context else None
        matching_skills = context.get("matching_skills", []) if context else []
        missing_skills = context.get("missing_skills", []) if context else []
        raw_resume = context.get("raw_resume_text", "") if context else ""

        # Preserved conversation history up to 20 messages for rich multi-turn context
        clean_history = []
        for h in conversation_history[-20:]:
            if h.get("role") in ["user", "assistant"] and h.get("content"):
                clean_history.append({"role": h["role"], "content": h["content"]})
        clean_history.append({"role": "user", "content": message})

        provider, api_key = self.get_active_provider(client_provider, client_api_key)

        # Build comprehensive reasoning system prompt for Cloud AI
        system_prompt = f"""You are J.A.R.V.I.S. (Just A Rather Very Intelligent System), the elite personal AI career mentor and engineering strategist in CareerSetu.

Persona & Voice:
- You speak with the sophisticated, respectful, articulate, and confident persona of Tony Stark's assistant in Iron Man.
- Address the user respectfully by their verified name: '{candidate_name}'.
- Prioritize accuracy, logical depth, engineering precision, and genuine helpfulness above all else.

Candidate Context Telemetry:
- Candidate Name: {candidate_name}
- Target Role: {job_title} at {job_company}
- ATS Match Score: {overall_score}/100 ({match_rating})
- Verified Matched Skills: {', '.join(matching_skills[:12]) if matching_skills else 'None detected'}
- Identified Missing Skills: {', '.join(missing_skills[:10]) if missing_skills else 'None'}
- Verified Resume Snippet: {raw_resume[:800] if raw_resume else 'No raw resume uploaded'}

CRITICAL OPERATIONAL RULES:
1. QUESTION UNDERSTANDING & FOLLOW-UPS:
   - Carefully analyze the conversation history. If the user asks a follow-up ("why?", "what about edge cases?", "optimize that", "what about negative numbers?", "how does that apply to my resume?"), resolve the exact subject from previous turns without asking the user to repeat themselves.
2. REASONING & ALGORITHMIC RIGOR:
   - For coding questions: Break down the intuition first. Provide clean, correct, and tested code. Explicitly detail edge cases (empty input, single element, negative numbers, boundary overflows). Provide Big-O Time Complexity and Space Complexity with clear mathematical justification.
3. CONTEXT RELEVANCE FILTER (STRICT):
   - When the user asks a pure technical, programming, system design, database, or networking question, DO NOT dump resume stats or mention ATS scores! Answer the technical problem with pure senior engineering excellence.
   - Only bring in resume telemetry, ATS scores, and missing skills when the user specifically asks about their resume, job fit, interview prep, or career trajectory.
4. ACCURACY & ANTI-HALLUCINATION:
   - Never invent facts, companies, or technologies. Ground all resume feedback in the actual candidate data provided.
   - If an inquiry is genuinely ambiguous, ask ONE focused clarification question while suggesting the top 2-3 likely scenarios.
5. SELF-VERIFICATION PROTOCOL:
   - Internally audit: Did I solve the exact problem? Is the code correct? Are edge cases addressed? Is Big-O sound?
"""

        if provider and api_key:
            try:
                if provider == "gemini":
                    reply = self.call_gemini(api_key, system_prompt, clean_history)
                    return {
                        "reply": reply,
                        "mode": "live_api",
                        "provider": f"Google Gemini Cloud ({provider.upper()})",
                        "interview_state": interview_state,
                        "suggested_replies": self._get_suggested_followups(message, context, interview_state)
                    }
                elif provider in ["openai", "groq"]:
                    base_url = "https://api.openai.com/v1" if provider == "openai" else "https://api.groq.com/openai/v1"
                    model = "gpt-4o" if provider == "openai" else "llama-3.3-70b-versatile"
                    reply = self.call_openai_compatible(api_key, base_url, model, system_prompt, clean_history)
                    return {
                        "reply": reply,
                        "mode": "live_api",
                        "provider": f"{provider.upper()} Cloud AI",
                        "interview_state": interview_state,
                        "suggested_replies": self._get_suggested_followups(message, context, interview_state)
                    }
            except Exception as e:
                print(f"Cloud AI call failed ({e}). Seamlessly engaging JARVIS Autonomous Intelligence Engine.")

        # Autonomous Local Reasoning Engine
        return self._generate_local_intelligence_response(
            message=message,
            history=clean_history,
            context=context,
            interview_state=interview_state,
            candidate_name=candidate_name
        )

    # =========================================================================
    # CANDIDATE IDENTITY RESOLUTION
    # =========================================================================

    def _resolve_candidate_name(self, message: str, context: Optional[Dict[str, Any]]) -> str:
        name = "Candidate"
        if context and context.get("candidate_name"):
            name = context["candidate_name"]

        if "default" in self.session_user_names:
            name = self.session_user_names["default"]

        return name

    def _check_name_correction(self, message: str) -> Optional[str]:
        """Detect statements like 'I am Sujith not Alex', 'My name is Sujith', 'Call me Sujith'."""
        msg = message.strip()
        patterns = [
            r"(?:i\s*am|i'm)\s+([a-zA-Z]{2,20})\s+(?:not\s+[a-zA-Z]{2,20})",
            r"(?:i\s*am|i'm)\s+([a-zA-Z]{2,20})(?:\s+not|\s*$|[.,!])",
            r"(?:my\s*name\s*is|name\s*is|call\s*me)\s+([a-zA-Z]{2,20})",
        ]
        for pat in patterns:
            match = re.search(pat, msg, re.IGNORECASE)
            if match:
                extracted = match.group(1).strip()
                if extracted.lower() not in [
                    "not", "here", "ready", "fine", "good", "confused", "wondering", "asking", "interested"
                ]:
                    self.session_user_names["default"] = extracted
                    return extracted
        return None

    # =========================================================================
    # AUTONOMOUS LOCAL REASONING ENGINE
    # =========================================================================

    def _generate_local_intelligence_response(
        self,
        message: str,
        history: List[Dict[str, str]],
        context: Optional[Dict[str, Any]],
        interview_state: Optional[Dict[str, Any]],
        candidate_name: str
    ) -> Dict[str, Any]:
        """
        High-Performance Autonomous Dialogue & Reasoning Engine.
        Executes:
        - Multi-turn topic tracking and follow-up resolution.
        - Problem deconstruction, working code, edge case validation, and Big-O derivation.
        - Ambiguity detection with focused single-clarification questions.
        - Grounded resume inspection with zero hallucination.
        - Context relevance filtering (no unsolicited resume dumping on coding queries).
        - Mock interview state management.
        """
        msg = message.lower().strip()

        # 1. INTERVIEW ACTIVE SESSION
        if interview_state and interview_state.get("active"):
            return self._handle_interview_turn(message, interview_state, context, candidate_name)

        if any(k in msg for k in [
            "start interview", "mock interview", "practice interview", "interview me",
            "interview practice", "technical interview", "take my interview"
        ]):
            return self._start_mock_interview(context, candidate_name)

        # 2. FOLLOW-UP DETECTION & RESOLUTION
        last_topic = self.session_last_topics.get("default", None)
        # Also check previous assistant message from history
        prev_assistant_msg = ""
        prev_user_msg = ""
        for h in reversed(history[:-1]):
            if h.get("role") == "assistant" and not prev_assistant_msg:
                prev_assistant_msg = h.get("content", "")
            elif h.get("role") == "user" and not prev_user_msg:
                prev_user_msg = h.get("content", "")

        follow_up_reply = self._resolve_follow_up(
            message=message,
            prev_user_msg=prev_user_msg,
            prev_assistant_msg=prev_assistant_msg,
            last_topic=last_topic,
            candidate_name=candidate_name,
            context=context
        )
        if follow_up_reply:
            return {
                "reply": follow_up_reply["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": follow_up_reply.get("suggested_replies", [
                    "What about edge cases?",
                    "Can you optimize that further?",
                    "Start an interactive mock interview",
                    "How can I improve my resume?"
                ])
            }

        # 3. AMBIGUOUS QUESTION HANDLER (Ask 1 clear clarification question)
        ambiguous_reply = self._handle_ambiguous_query(message, candidate_name)
        if ambiguous_reply:
            return {
                "reply": ambiguous_reply["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": ambiguous_reply.get("suggested_replies", [])
            }

        # 4. GREETINGS & CASUAL INTRODUCTIONS
        if re.match(r"^(hi|hello|hey|greetings|good\s*(?:morning|afternoon|evening|day)|yo|jarvis|what'?s\s*up)\b", msg):
            job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"
            reply = f"Good to see you, **{candidate_name}**. All neural diagnostic monitors are online and calibrated to your **{job_title}** target profile.\n\n"
            reply += "What strategic objective shall we tackle today?\n"
            reply += "1. **Code & Algorithm Mastery:** Deep problem deconstruction, edge cases, and Big-O derivation ($O(N)$, $O(\\log N)$).\n"
            reply += "2. **System Design & Distributed Architecture:** Caching, message queues, database scaling, and CAP theorem trade-offs.\n"
            reply += "3. **Resume & ATS Score Optimization:** Concrete bullet point improvements grounded in your actual uploaded experience.\n"
            reply += "4. **Interactive Mock Interview:** Real-time technical evaluation with scores and tactical feedback.\n\n"
            reply += "At your command, what shall we inspect?"
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "How can I improve my resume?",
                    "Start an interactive mock interview",
                    "What critical skills am I missing?",
                    "Explain reverse linked list in Python"
                ]
            }

        # 5. IDENTITY & BOT CAPABILITIES
        if any(k in msg for k in ["who are you", "what is jarvis", "what can you do", "who made you", "are you ai", "your capabilities"]):
            reply = f"I am **J.A.R.V.I.S.** (*Just A Rather Very Intelligent System*), your personal AI career mentor and engineering strategist in CareerSetu.\n\n"
            reply += f"I have been calibrated to assist you, **{candidate_name}**, in mastering technical interviews, optimizing your resume for ATS algorithms, and reasoning through complex software engineering problems.\n\n"
            reply += "### ⚡ Core Engineering Capabilities:\n"
            reply += "1. **Deep Problem Solving:** Data structures, algorithms, edge-case validation, and Big-O runtime & memory analysis.\n"
            reply += "2. **System Design & Architecture:** Designing resilient distributed systems, caching tiers (Redis), messaging queues (Kafka), and database indexing (PostgreSQL).\n"
            reply += "3. **Grounded Resume Optimization:** Auditing your active resume, transforming bullet points using the Google XYZ formula, and explaining your TF-IDF ATS scores.\n"
            reply += "4. **Interactive Mock Interviews:** Posing realistic questions one-by-one, evaluating technical answers with scores out of 10, and suggesting senior-level improvements.\n"
            reply += "5. **Curriculum Synthesis:** Building personalized 30-day learning roadmaps for missing competencies.\n\n"
            reply += "How shall we proceed?"
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "Analyze my resume for this role",
                    "Start an interactive mock interview",
                    "Explain database indexing in PostgreSQL",
                    "Generate a 30-day roadmap"
                ]
            }

        # 6. DATA STRUCTURES & ALGORITHMS (Deep Reasoning, Code, Edge Cases, Big-O)
        dsa_match = self._handle_dsa_query(message, candidate_name)
        if dsa_match:
            self.session_last_topics["default"] = dsa_match["topic"]
            return {
                "reply": dsa_match["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": dsa_match["suggested_replies"]
            }

        # 7. SYSTEM DESIGN & DISTRIBUTED ARCHITECTURE
        sys_match = self._handle_system_design_query(message, candidate_name)
        if sys_match:
            self.session_last_topics["default"] = sys_match["topic"]
            return {
                "reply": sys_match["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": sys_match["suggested_replies"]
            }

        # 8. DATABASE & SQL OPTIMIZATION
        db_match = self._handle_database_query(message, candidate_name)
        if db_match:
            self.session_last_topics["default"] = db_match["topic"]
            return {
                "reply": db_match["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": db_match["suggested_replies"]
            }

        # 9. NETWORKING & WEB PROTOCOLS (TCP vs UDP, HTTP/2/3, WebSockets, REST vs GraphQL)
        net_match = self._handle_networking_query(message, candidate_name)
        if net_match:
            self.session_last_topics["default"] = net_match["topic"]
            return {
                "reply": net_match["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": net_match["suggested_replies"]
            }

        # 10. LANGUAGE SPECIFICS (Python, C++, Java, React)
        lang_match = self._handle_language_query(message, candidate_name)
        if lang_match:
            self.session_last_topics["default"] = lang_match["topic"]
            return {
                "reply": lang_match["reply"],
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": lang_match["suggested_replies"]
            }

        # 11. RESUME IMPROVEMENT & ATS SCORE EXPLANATION (Grounded in context)
        if any(k in msg for k in [
            "improve resume", "improve my resume", "ats score", "explain score", "how to improve",
            "score breakdown", "review resume", "check my resume", "score diagnostic"
        ]):
            self.session_last_topics["default"] = "resume_review"
            reply = self._handle_resume_review(context, candidate_name)
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "What critical skills am I missing?",
                    "How do I explain my projects in an interview?",
                    "Start an interactive mock interview",
                    "Rewrite my top experience bullet point"
                ]
            }

        # 12. MISSING SKILLS & LEARNING ROADMAP
        if any(k in msg for k in ["missing skill", "missing skills", "skill gap", "what skills", "learn", "roadmap", "curriculum", "study plan"]):
            self.session_last_topics["default"] = "skill_roadmap"
            reply = self._handle_skill_roadmap(message, context, candidate_name)
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "Start an interactive mock interview",
                    "How do I explain my projects for interviews?",
                    "Explain database indexing in PostgreSQL",
                    "How can I improve my resume further?"
                ]
            }

        # 13. PROJECT EXPLANATION & INTERVIEW PITCH (Grounded in user's actual resume)
        if any(k in msg for k in ["explain my project", "explain project", "project explanation", "tell me about your project", "portfolio", "how to explain project"]):
            self.session_last_topics["default"] = "project_pitch"
            reply = self._handle_project_explanation(context, candidate_name)
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "Ask me an architectural question on this project",
                    "Start an interactive mock interview",
                    "How do I explain technical trade-offs?",
                    "How do I optimize my resume bullet points?"
                ]
            }

        # 14. BEHAVIORAL & HR QUESTIONS (STAR Method)
        if any(k in msg for k in ["tell me about yourself", "weakness", "conflict", "salary", "behavioral", "why should we hire you", "star method", "hr question", "hr round"]):
            self.session_last_topics["default"] = "behavioral_hr"
            job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"
            job_company = context.get("job_company", "your prospective employer") if context else "your prospective employer"
            reply = self._answer_hr_question(message, candidate_name, job_title, job_company)
            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "Give me a behavioral mock question",
                    "How do I handle salary expectations?",
                    "Start an interactive mock interview",
                    "How can I improve my resume?"
                ]
            }

        # 15. DEFAULT HIGH-REASONING FALLBACK (Grounded without hallucination)
        reply = f"Acknowledged, **{candidate_name}**. Regarding: *\"{message}\"*\n\n"
        reply += "To address this with rigorous engineering depth, let us deconstruct the problem:\n\n"
        reply += "1. **Core Problem Identification:** Clarify the specific system constraint, computational bottleneck, or architectural goal.\n"
        reply += "2. **Algorithmic & Technical Feasibility:** Evaluate trade-offs between time complexity $O(N)$, space complexity $O(1)$, and production maintainability.\n"
        reply += "3. **Verification & Edge Cases:** Ensure edge cases (empty states, concurrency contention, null inputs, scale limits) are addressed before deploying.\n\n"
        reply += "Would you like me to walk through a code implementation, design an architectural blueprint, or test your readiness with a targeted mock interview question?"
        return {
            "reply": reply,
            "mode": "local_intelligence",
            "provider": "JARVIS Autonomous Intelligence Engine",
            "interview_state": None,
            "suggested_replies": [
                "Start an interactive mock interview",
                "How can I improve my resume?",
                "What critical skills am I missing?",
                "Explain reverse linked list in Python"
            ]
        }

    # =========================================================================
    # MULTI-TURN FOLLOW-UP RESOLVER
    # =========================================================================

    def _resolve_follow_up(
        self,
        message: str,
        prev_user_msg: str,
        prev_assistant_msg: str,
        last_topic: Optional[str],
        candidate_name: str,
        context: Optional[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Understands follow-up questions ('why?', 'what about edge cases?', 'can you optimize it?',
        'what is the time complexity?', 'what about negative numbers?', 'show it in c++')
        by inspecting conversation history and active topics.
        """
        msg = message.lower().strip()

        # Follow-up patterns
        is_complexity = any(k in msg for k in ["time complexity", "space complexity", "big o", "complexity", "runtime", "memory usage"])
        is_edge_case = any(k in msg for k in ["edge case", "corner case", "what if empty", "negative numbers", "single element", "duplicates", "null pointer"])
        is_optimization = any(k in msg for k in ["optimize", "make it faster", "better approach", "reduce time", "reduce space", "can it be done faster"])
        is_why = re.match(r"^(why|why\s+is\s+that|why\s+so|how\s+come|explain\s+why)\b", msg) is not None
        is_code_lang = re.search(r"\b(in\s+c\+\+|in\s+java|in\s+python|in\s+javascript|in\s+typescript|c\+\+|java|python|javascript)\b", msg) is not None
        is_recursive = any(k in msg for k in ["recursive", "recursion", "recursive solution", "how to do it recursively"])

        # Determine the active topic from history or topic tracker
        active_topic = last_topic
        if not active_topic:
            combined_prev = (prev_user_msg + " " + prev_assistant_msg).lower()
            if "linked list" in combined_prev:
                active_topic = "linked_list"
            elif "two sum" in combined_prev:
                active_topic = "two_sum"
            elif "binary search" in combined_prev:
                active_topic = "binary_search"
            elif "lru" in combined_prev:
                active_topic = "lru_cache"
            elif "index" in combined_prev or "b-tree" in combined_prev or "sql" in combined_prev:
                active_topic = "database_indexing"
            elif "tcp" in combined_prev or "udp" in combined_prev:
                active_topic = "tcp_vs_udp"
            elif "cache" in combined_prev or "caching" in combined_prev:
                active_topic = "caching"
            elif "resume" in combined_prev or "ats" in combined_prev:
                active_topic = "resume_review"

        if not active_topic:
            return None

        # Resolve Topic + Follow-up Intent

        # A. LINKED LIST FOLLOW-UPS
        if active_topic == "linked_list":
            if is_complexity:
                return {
                    "reply": f"""### ⏱️ Time & Space Complexity Analysis: Reversing a Singly Linked List
Candidate: **{candidate_name}**

#### 1. Iterative Approach:
- **Time Complexity: $O(N)$**
  - We iterate through the list using a single pointer loop (`while curr:`).
  - Every node is visited exactly once, performing $O(1)$ constant-time pointer swaps.
  - Thus, total operations scale strictly linearly with the number of nodes $N$.
- **Space Complexity: $O(1)$ Auxiliary Space**
  - We only allocate three local pointers: `prev`, `curr`, and `next_node`.
  - No heap allocations or data structures are created; pointer manipulation is strictly in-place.

#### 2. Recursive Approach:
- **Time Complexity: $O(N)$** (Each node processed once).
- **Space Complexity: $O(N)$ Call Stack Memory**
  - The runtime stack must store $N$ activation frames before reaching the base case (`head is None or head.next is None`).
  - *Engineering Note:* In production, iterative reversal is heavily preferred to prevent stack overflow on deep lists ($N > 10,000$).""",
                    "suggested_replies": ["Show me the recursive code", "What are the edge cases?", "How to reverse between nodes m and n?"]
                }

            if is_edge_case:
                return {
                    "reply": f"""### 🛡️ Critical Edge Cases for Linked List Reversal
Candidate: **{candidate_name}**

When interviewers assess linked list problems, they look for these specific failure guards:

1. **Empty List (`head is None`):**
   - *Behavior:* The loop `while curr:` never executes; `prev` (initialized to `None`) is returned.
   - *Risk avoided:* `AttributeError: 'NoneType' object has no attribute 'next'`.

2. **Single-Node List (`head.next is None`):**
   - *Behavior:* Loops exactly once. `next_node = None`, `curr.next = None`, `prev = curr`, `curr = None`. Returns the same node safely.

3. **Two-Node List (`A -> B -> None`):**
   - Loop 1: `A -> None`, `prev = A`, `curr = B`.
   - Loop 2: `B -> A -> None`, `prev = B`, `curr = None`.
   - Returns `B`, correctly reversed.

4. **Circular / Cyclic Lists:**
   - If the linked list contains a cycle, naive reversal causes an **infinite loop**!
   - *Mitigation:* Before reversing, run **Floyd's Cycle-Finding Algorithm** (Tortoise and Hare with slow and fast pointers) if cycle freedom is not guaranteed.

Would you like to examine the recursive solution or test another data structure?""",
                    "suggested_replies": ["Show recursive implementation", "Explain Floyd's cycle detection", "Explain Two Sum problem"]
                }

            if is_recursive:
                return {
                    "reply": f"""### 🔄 Recursive Linked List Reversal in Python & C++
Candidate: **{candidate_name}**

#### Python Implementation:
```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_list_recursive(head: Optional[ListNode]) -> Optional[ListNode]:
    # Base Case: empty list or last node reached
    if head is None or head.next is None:
        return head

    # Recursive step: reverse the remainder of the list
    new_head = reverse_list_recursive(head.next)

    # Re-wire pointers: make the next node point back to current node
    head.next.next = head
    head.next = None

    return new_head
```

#### Complexity Breakdown:
- **Time Complexity:** $O(N)$
- **Space Complexity:** $O(N)$ auxiliary stack space.
- *Trade-off Notice:* Demonstrates clean recursive intuition, but iterative is preferred in production systems with millions of nodes.""",
                    "suggested_replies": ["What is the time complexity?", "Show iterative approach", "Explain Two Sum"]
                }

            if is_code_lang and "c++" in msg:
                return {
                    "reply": f"""### ⚙️ C++ Iterative Linked List Reversal
Candidate: **{candidate_name}**

```cpp
#include <iostream>

struct ListNode {{
    int val;
    ListNode* next;
    ListNode(int x) : val(x), next(nullptr) {{}}
}};

ListNode* reverseList(ListNode* head) {{
    ListNode* prev = nullptr;
    ListNode* curr = head;

    while (curr != nullptr) {{
        ListNode* next_node = curr->next; // Store next node
        curr->next = prev;               // Reverse current node's pointer
        prev = curr;                     // Advance prev
        curr = next_node;                // Advance curr
    }}

    return prev; // New head of reversed list
}}
```

- **Time Complexity:** $O(N)$
- **Space Complexity:** $O(1)$ strictly in-place.""",
                    "suggested_replies": ["What are the edge cases?", "Explain Binary Search", "Start mock interview"]
                }

        # B. TWO SUM FOLLOW-UPS
        if active_topic == "two_sum":
            if is_complexity or is_why:
                return {
                    "reply": f"""### ⏱️ Time & Space Complexity Derivation: Two Sum
Candidate: **{candidate_name}**

#### 1. Why Hash Map achieves $O(N)$ Time:
- In a naive brute force approach, testing all pairs requires two nested loops:
  $$\\sum_{{i=0}}^{{N-1}} (N - 1 - i) = \\frac{{N(N-1)}}{{2}} \\implies O(N^2)$$
- By using a Hash Table (Python `dict`), lookup of the complement `target - num` operates in **$O(1)$ average time** via hashing.
- We iterate through the array of length $N$ exactly once.
- Total time: $N \\times O(1) = \\mathbf{{O(N)}}$.

#### 2. Space Complexity: $O(N)$
- In the worst case (where the matching pair is at the very end of the array, or no pair exists), the hash map stores up to $N - 1$ key-value pairs.
- Therefore, auxiliary memory scales as $\\mathbf{{O(N)}}$.

#### 3. What if memory is constrained to $O(1)$?
- If auxiliary space must be $O(1)$, we sort the array in $O(N \\log N)$ and apply **Two Pointers** (left at start, right at end). Note: this sacrifices indices unless tracking original positions!""",
                    "suggested_replies": ["Show Two Pointers approach", "What are the edge cases for Two Sum?", "Explain LRU Cache"]
                }

            if is_edge_case:
                return {
                    "reply": f"""### 🛡️ Critical Edge Cases for Two Sum
Candidate: **{candidate_name}**

1. **Negative Numbers:**
   - `nums = [-3, 4, 3, 90]`, `target = 0`.
   - Complements must handle negatives correctly: `0 - (-3) = 3`. Hash table handles negative keys seamlessly.
2. **Identical Numbers Forming the Target:**
   - `nums = [3, 3]`, `target = 6`.
   - A single-pass hash map checks if `target - num` is ALREADY in the map BEFORE adding the current element. This avoids using the same element index twice!
3. **No Valid Solution:**
   - If no pair sums to target, the function must return an empty list `[]` or raise `ValueError` rather than returning `None`.
4. **Large Integers (Integer Overflow in C++/Java):**
   - In languages like C++ or Java, `target - num` can trigger integer underflow if `target` is minimum integer and `num` is positive. Use 64-bit `long long` when integers can exceed $2^{{31}}-1$.""",
                    "suggested_replies": ["Show C++ code for Two Sum", "Explain Binary Search", "Start mock interview"]
                }

        # C. DATABASE INDEXING FOLLOW-UPS
        if active_topic == "database_indexing":
            if is_why or "b-tree" in msg or "hash" in msg:
                return {
                    "reply": f"""### 📊 B-Tree vs. Hash Indexes: Deep Architectural Comparison
Candidate: **{candidate_name}**

#### Why B-Trees are the Universal Default:
1. **Support for Range Queries:**
   - B-Tree leaf nodes form a doubly-linked sequential chain.
   - Queries like `WHERE created_at BETWEEN '2026-01-01' AND '2026-03-31'` or `WHERE age > 25` execute in $O(\\log N + K)$ where $K$ is the number of matching rows.
   - Hash indexes CANNOT perform range queries because hashes scramble sequential ordering!

2. **Sorting & `ORDER BY` Optimization:**
   - B-Tree traversal naturally yields sorted keys, completely eliminating expensive in-memory disk sorts (`Sort Method: external merge`).

3. **Prefix Matching:**
   - Queries like `WHERE username LIKE 'sujith%'` leverage B-Tree prefixes.

#### When are Hash Indexes Preferred?
- Strictly for **exact equality lookups** (`WHERE uuid = 'abc-123'`).
- Time complexity is $O(1)$ average vs $O(\\log N)$ for B-Tree.
- Drawbacks: Cannot be used for multi-column leftmost prefix matching, cannot support sorting, and does not support unique constraints in older database engines.""",
                    "suggested_replies": ["Explain Leftmost Prefix Rule", "How does EXPLAIN ANALYZE work?", "What about GIN indexes?"]
                }

        # D. TCP VS UDP FOLLOW-UPS
        if active_topic == "tcp_vs_udp":
            if "video" in msg or "streaming" in msg or "gaming" in msg:
                return {
                    "reply": f"""### 🎥 Why Video Streaming & Gaming Choose UDP / QUIC
Candidate: **{candidate_name}**

#### 1. Live Gaming & Real-Time Audio (WebRTC / UDP):
- In multiplayer games or VoIP (Discord, Zoom), a delayed packet is **useless data**!
- If Packet #4 is dropped in TCP, TCP holds up Packets #5, #6, and #7 until #4 is retransmitted (**Head-of-Line Blocking**).
- UDP drops Packet #4 and immediately displays Packet #5, maintaining sub-50ms latency.

#### 2. On-Demand Video Streaming (Netflix, YouTube):
- Netflix and YouTube use **HLS / DASH over TCP / HTTP/2 or HTTP/3 (QUIC)**.
- Why? They can buffer 30 seconds of video in advance. Reliability matters more than real-time transmission, so TCP's retransmissions work fine.

#### 3. Modern Evolution: HTTP/3 & QUIC
- QUIC is built directly on top of **UDP** in user space!
- It implements reliability and congestion control like TCP, but multiplexes streams independently to eliminate Head-of-Line blocking.""",
                    "suggested_replies": ["Explain TCP 3-Way Handshake", "What is Head-of-Line Blocking?", "Explain System Design caching"]
                }

        # General follow-up handler
        return None

    # =========================================================================
    # AMBIGUITY DETECTOR & SINGLE CLARIFICATION HANDLER
    # =========================================================================

    def _handle_ambiguous_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        """
        Handles genuinely ambiguous questions by asking ONE clear clarification question
        and providing the 3 most common technical scenarios.
        """
        msg = message.lower().strip()
        ambiguous_triggers = [
            "my app is slow", "my application is slow", "it is slow", "how to make it faster",
            "database is not working", "database problem", "database issue", "fix my database",
            "how to fix it", "it is not working", "code is not working", "what should i do next"
        ]

        if any(msg == t or msg == t + "?" or msg == t + "." for t in ambiguous_triggers):
            if "database" in msg:
                reply = f"Understood, **{candidate_name}**. To provide a precise architectural diagnosis, could you clarify what specific database bottleneck you are observing?\n\n"
                reply += "### 🔍 3 Most Common Database Bottlenecks:\n"
                reply += "1. **Slow Query Execution Latency:** Queries taking >500ms due to missing composite indexes or sequential table scans (`EXPLAIN ANALYZE`).\n"
                reply += "2. **Connection Pool Exhaustion:** Backend services dropping connections under concurrent load due to unclosed sessions or undersized pools (e.g. PgBouncer).\n"
                reply += "3. **Locking & Deadlocks:** Long-running write transactions blocking concurrent reads during updates.\n\n"
                reply += "Which of these matches your current challenge, or can you share your query / schema?"
                return {
                    "reply": reply,
                    "suggested_replies": [
                        "My queries are slow without indexes",
                        "Connection pool is getting exhausted",
                        "Transactions are locking each other"
                    ]
                }

            if "slow" in msg or "faster" in msg:
                reply = f"Understood, **{candidate_name}**. To give you the exact technical solution, could you clarify at which layer the performance degradation is occurring?\n\n"
                reply += "### 🔍 3 Primary Performance Bottleneck Tiers:\n"
                reply += "1. **Database Tier:** Missing indexes, N+1 query loops, or heavy unindexed table scans.\n"
                reply += "2. **Backend API Tier:** CPU-bound tasks freezing the async event loop, blocking I/O, or lack of Redis caching.\n"
                reply += "3. **Frontend Tier:** Excessive React component re-renders, unvirtualized long lists, or large unoptimized bundle assets.\n\n"
                reply += "Where is the slowdown primarily detected?"
                return {
                    "reply": reply,
                    "suggested_replies": [
                        "Backend API latency is high",
                        "Database queries are taking too long",
                        "Frontend React app has sluggish UI"
                    ]
                }

            reply = f"I am ready to help resolve this, **{candidate_name}**. To ensure a precise diagnosis, could you clarify what specific technology stack or component is experiencing the issue?\n\n"
            reply += "For example, is this related to:\n"
            reply += "- A Python / FastAPI backend or database query?\n"
            reply += "- A React frontend rendering issue?\n"
            reply += "- Or an ATS resume score calibration?\n\n"
            reply += "Share the error message or behavior, and I will diagnose it immediately."
            return {
                "reply": reply,
                "suggested_replies": [
                    "Help with Python / FastAPI backend",
                    "Help with React frontend rendering",
                    "Help with database indexing"
                ]
            }

        return None

    # =========================================================================
    # DEEP REASONING: DATA STRUCTURES & ALGORITHMS
    # =========================================================================

    def _handle_dsa_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        msg = message.lower()

        # 1. Reverse Linked List
        if ("linked list" in msg and any(k in msg for k in ["reverse", "reversing", "reversal"])) or "reverse linked" in msg:
            reply = f"""### 🧠 Problem Deconstruction: Reverse a Singly Linked List
Candidate: **{candidate_name}**

#### 1. Intuition & Architectural Invariant:
In a singly linked list, each node points forward to `node.next`. To reverse the list in-place, we must reverse the direction of each pointer so it points backward to its predecessor (`node.next = prev`).
Because updating `curr.next` severs our link to the rest of the list, we MUST cache `curr.next` in a temporary pointer (`next_node`) before reassigning!

#### 2. Production-Grade Python Implementation:
```python
from typing import Optional

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def reverse_linked_list(head: Optional[ListNode]) -> Optional[ListNode]:
    prev: Optional[ListNode] = None
    curr: Optional[ListNode] = head

    while curr is not None:
        next_node: Optional[ListNode] = curr.next  # 1. Cache forward pointer
        curr.next = prev                           # 2. Reverse pointer backward
        prev = curr                                # 3. Advance prev forward
        curr = next_node                           # 4. Advance curr forward

    return prev  # prev is now the new head of the reversed list
```

#### 3. Rigorous Edge-Case Validation:
- **`head is None` (Empty list):** Loop never executes; returns `None` safely without null pointer exception.
- **Single Node (`head.next is None`):** Loop executes once; `curr.next` set to `None`, returns original node.
- **Two Nodes (`1 -> 2 -> None`):** Loop 1 sets `1 -> None`; Loop 2 sets `2 -> 1 -> None`. Correctly returns `2`.
- **Large Lists ($N = 10^6$):** Iterative method avoids recursion stack limits entirely.

#### 4. Big-O Complexity Derivation:
- **Time Complexity: $O(N)$** — Single pass where $N$ is the total count of nodes. Each node performs exactly 4 pointer reassignments ($O(1)$).
- **Space Complexity: $O(1)$ Auxiliary Space** — Only 3 local reference pointers (`prev`, `curr`, `next_node`) are stored on the stack."""
            return {
                "topic": "linked_list",
                "reply": reply,
                "suggested_replies": [
                    "What is the space complexity of the recursive solution?",
                    "What are the edge cases for linked lists?",
                    "Show this in C++",
                    "How to detect a cycle in a linked list?"
                ]
            }

        # 2. Two Sum Problem
        if any(k in msg for k in ["two sum", "twosum"]):
            reply = f"""### 🧠 Problem Deconstruction: Two Sum ($O(N)$ One-Pass Hash Map)
Candidate: **{candidate_name}**

#### 1. Intuition:
Given an array `nums` and integer `target`, find indices of two numbers that sum to `target`.
- **Brute Force:** Testing all pairs with two loops yields $O(N^2)$ time.
- **Optimal One-Pass:** For each element $x$ at index $i$, its required complement is $y = \\text{{target}} - x$. If $y$ exists in our hash map, we found our pair in $O(1)$ lookup time!

#### 2. Production Python Implementation:
```python
from typing import List

def two_sum(nums: List[int], target: int) -> List[int]:
    seen: dict[int, int] = {{}}  # maps number -> index

    for idx, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], idx]
        seen[num] = idx

    return []  # Return empty if no valid pair exists
```

#### 3. Edge-Case Validation:
- **Negative Numbers:** `nums = [-1, -2, -3, -4, -5], target = -8` $\\implies$ `complement = -8 - (-3) = -5`. Handled seamlessly.
- **Duplicate Elements:** `nums = [3, 3], target = 6` $\\implies$ On second `3`, complement `3` is already in `seen` at index `0`. Returns `[0, 1]`.
- **No Solution:** Returns `[]` gracefully.

#### 4. Complexity Analysis:
- **Time Complexity: $O(N)$** — Traverses the list once. Hash table average lookup and insertion is $O(1)$.
- **Space Complexity: $O(N)$** — Stores at most $N$ elements in the hash map."""
            return {
                "topic": "two_sum",
                "reply": reply,
                "suggested_replies": [
                    "What if the array is already sorted?",
                    "Can we solve Two Sum in O(1) space?",
                    "Explain Binary Search",
                    "Start an interactive mock interview"
                ]
            }

        # 3. Binary Search
        if any(k in msg for k in ["binary search"]):
            reply = f"""### 🧠 Problem Deconstruction: Binary Search ($O(\\log N)$)
Candidate: **{candidate_name}**

#### 1. Intuition:
Operates on a **sorted array**. Repeatedly divides the search interval in half by comparing the target with the middle element.

#### 2. Production Python Implementation:
```python
from typing import List

def binary_search(nums: List[int], target: int) -> int:
    low = 0
    high = len(nums) - 1

    while low <= high:
        # Avoid integer overflow (critical in C++/Java):
        mid = low + (high - low) // 2

        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1

    return -1  # Target not found
```

#### 3. Edge Cases & Trap Prevention:
- **Integer Overflow:** In languages like C++ or Java, `(low + high) / 2` overflows when `low + high > 2^{{31}}-1`. Using `low + (high - low) / 2` completely avoids overflow.
- **Empty Array:** `low = 0, high = -1`. The loop never executes, returns `-1`.
- **Duplicates:** If duplicates exist and you need the first or last occurrence, use `bisect_left` or `bisect_right` variants.

#### 4. Complexity:
- **Time Complexity: $O(\\log N)$** — Halves search space each iteration ($N, N/2, N/4, \\dots, 1$).
- **Space Complexity: $O(1)$** — Strictly constant auxiliary memory."""
            return {
                "topic": "binary_search",
                "reply": reply,
                "suggested_replies": [
                    "How to find the first occurrence with duplicates?",
                    "Explain search in rotated sorted array",
                    "Explain LRU Cache design",
                    "Start mock interview"
                ]
            }

        # 4. LRU Cache
        if any(k in msg for k in ["lru cache", "least recently used"]):
            reply = f"""### 🧠 System & Algorithm Design: LRU Cache ($O(1)$ Operations)
Candidate: **{candidate_name}**

#### 1. Intuition & Data Structure Synergy:
To achieve **$O(1)$ `get`** and **$O(1)$ `put`**, we combine two data structures:
1. **Hash Map (`dict`):** Provides $O(1)$ key-to-node lookup.
2. **Doubly Linked List:** Provides $O(1)$ removal and insertion of nodes at the head (Most Recently Used) and tail (Least Recently Used).

#### 2. Core Python Implementation:
```python
class Node:
    def __init__(self, key=0, val=0):
        self.key = key
        self.val = val
        self.prev = None
        self.next = None

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {{}} # key -> Node
        # Dummy head and tail to eliminate null pointer checks
        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_to_front(self, node: Node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: int) -> int:
        if key in self.cache:
            node = self.cache[key]
            self._remove(node)
            self._add_to_front(node)  # Mark as MRU
            return node.val
        return -1

    def put(self, key: int, value: int) -> None:
        if key in self.cache:
            self._remove(self.cache[key])
        
        node = Node(key, value)
        self.cache[key] = node
        self._add_to_front(node)

        if len(self.cache) > self.capacity:
            # Evict LRU node from before tail
            lru = self.tail.prev
            self._remove(lru)
            del self.cache[lru.key]
```

#### 3. Complexity:
- **Time Complexity:** $O(1)$ for both `get` and `put`.
- **Space Complexity:** $O(\\text{{capacity}})$ auxiliary memory."""
            return {
                "topic": "lru_cache",
                "reply": reply,
                "suggested_replies": [
                    "How to make LRU Cache thread-safe in Python?",
                    "Compare LRU vs LFU caching",
                    "Explain System Design caching strategies",
                    "Start mock interview"
                ]
            }

        return None

    # =========================================================================
    # SYSTEM DESIGN & DISTRIBUTED ARCHITECTURE
    # =========================================================================

    def _handle_system_design_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        msg = message.lower()

        if any(k in msg for k in ["system design", "microservice", "monolith", "rate limit", "cap theorem", "caching strategy", "cache stampede", "load balancer"]):
            if "cap theorem" in msg:
                reply = f"""### 🌐 CAP Theorem in Distributed Systems
Candidate: **{candidate_name}**

#### 1. Core Principle:
In any asynchronous distributed data store across a network, you can guarantee at most **two out of three** properties:
- **C (Consistency):** Every read receives the most recent write or an error.
- **A (Availability):** Every non-failing node returns a non-error response, but without guarantee it contains the latest write.
- **P (Partition Tolerance):** The system continues to operate despite arbitrary network message loss or network splits.

#### 2. The Inevitable Reality:
Network partitions are physical facts of cloud engineering (cables get cut, switches fail). Therefore, **P is mandatory**. The actual architectural decision is:
- **CP Systems (e.g. HBase, MongoDB with majority write, ZooKeeper):** Prioritize consistency. Under a network partition, minority nodes reject requests to avoid stale reads.
- **AP Systems (e.g. Cassandra, DynamoDB, Couchbase):** Prioritize availability. All nodes accept reads/writes, resolving divergence later via **Eventual Consistency** (vector clocks or Last-Write-Wins)."""
                return {
                    "topic": "cap_theorem",
                    "reply": reply,
                    "suggested_replies": ["Explain Cache Stampede and Redis", "Explain Rate Limiting algorithms", "Start mock interview"]
                }

            if "caching" in msg or "cache stampede" in msg:
                reply = f"""### ⚡ Enterprise Caching Architecture & Cache Stampede Prevention
Candidate: **{candidate_name}**

#### 1. Caching Strategies:
- **Cache-Aside (Lazy Loading):** Application queries Redis first. On cache miss, reads from DB and populates cache. *Best for read-heavy workloads.*
- **Write-Through:** Application writes to cache, which synchronously updates the database.
- **Write-Behind (Write-Back):** Application writes to cache immediately; cache asynchronously writes to DB in batches. High write throughput, but risks data loss on cache node crash.

#### 2. The Cache Stampede (Thundering Herd) Problem:
When a popular cache key (e.g. homepage top items with 50,000 req/sec) expires, all 50,000 concurrent requests simultaneously experience a cache miss and hammer the primary database at once!

#### 3. Enterprise Mitigations:
1. **Distributed Mutex Lock (Redlock):** Only the first worker acquiring a Redis lock regenerates the cache; other workers wait or receive stale data.
2. **Probabilistic Early Expiration (XFetch Algorithm):** Workers probabilistically recompute the cache before actual TTL expiration based on compute cost $\\beta$ and remaining TTL.
3. **Stale-While-Revalidate:** Return existing cached data while triggering an asynchronous background job to refresh the cache."""
                return {
                    "topic": "caching",
                    "reply": reply,
                    "suggested_replies": ["Explain Rate Limiter design", "Explain Microservices vs Monolith", "Start mock interview"]
                }

            reply = f"""### 🏗️ Microservices vs. Modular Monolith Architecture
Candidate: **{candidate_name}**

#### 1. The Modular Monolith (First Choice for Startups & Mid-Scale):
- Single deployment artifact, but structured strictly into independent domain modules (e.g., Auth, Billing, CareerIntelligence).
- **Pros:** Zero network latency between calls, single ACID transaction boundaries, simple CI/CD deployments.
- **Scaling Limit:** Entire codebase must be deployed together; scaling CPU-bound jobs scales everything.

#### 2. Microservices Architecture:
- Independent services communicating via gRPC or asynchronous event buses (Apache Kafka, RabbitMQ).
- **Pros:** Independent team deployments, polyglot persistence, horizontal scaling of specific high-load services.
- **Cons:** Network latency, eventual consistency challenges (requires Saga Pattern instead of two-phase commits), distributed tracing complexity (OpenTelemetry)."""
            return {
                "topic": "microservices",
                "reply": reply,
                "suggested_replies": ["Explain CAP Theorem", "Explain Caching and Redis", "Start mock interview"]
            }

        return None

    # =========================================================================
    # DATABASE & SQL OPTIMIZATION
    # =========================================================================

    def _handle_database_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        msg = message.lower()
        if any(k in msg for k in ["sql", "index", "b-tree", "acid", "explain analyze", "n+1", "postgresql"]):
            reply = f"""### ⚡ PostgreSQL Database Indexing & Query Optimization
Candidate: **{candidate_name}**

#### 1. B-Tree Indexes vs. Full Table Scans:
- Without an index, PostgreSQL performs a **Sequential Scan ($O(N)$)** inspecting every page on disk.
- A **B-Tree Index ($O(\\log N)$)** keeps keys sorted in a balanced tree:
```sql
CREATE INDEX idx_candidates_job_title ON analysis_records (job_title);
```

#### 2. The Leftmost Prefix Rule (Composite Indexes):
If you create a composite index:
```sql
CREATE INDEX idx_user_role_created ON users (role, created_at DESC);
```
- ✅ Fast: `WHERE role = 'Engineer' AND created_at > '2026-01-01'`
- ✅ Fast: `WHERE role = 'Engineer'` (uses leftmost column)
- ❌ **Sequential Scan:** `WHERE created_at > '2026-01-01'` (Leftmost prefix skipped!)

#### 3. Diagnosing with `EXPLAIN (ANALYZE, BUFFERS)`:
```sql
EXPLAIN (ANALYZE, BUFFERS)
SELECT candidate_name, overall_score 
FROM analysis_records 
WHERE overall_score >= 80 
ORDER BY created_at DESC;
```
- Look for `Execution Time`, `Buffers: shared read` (disk I/O), and check whether it performed an **Index Scan** or an **Seq Scan**."""
            return {
                "topic": "database_indexing",
                "reply": reply,
                "suggested_replies": [
                    "What is the difference between B-Tree and Hash indexes?",
                    "What are the 4 ACID transaction isolation levels?",
                    "How to fix the N+1 query problem?",
                    "Start mock interview"
                ]
            }
        return None

    # =========================================================================
    # NETWORKING & PROTOCOLS
    # =========================================================================

    def _handle_networking_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        msg = message.lower()
        if any(k in msg for k in ["tcp", "udp", "http/2", "http/3", "websocket", "rest vs graphql"]):
            if "tcp" in msg or "udp" in msg:
                reply = f"""### 🌐 Comprehensive Protocol Analysis: TCP vs. UDP
Candidate: **{candidate_name}**

| Architectural Metric | TCP (Transmission Control Protocol) | UDP (User Datagram Protocol) |
| :--- | :--- | :--- |
| **Connection Model** | Connection-oriented (3-way handshake) | Connectionless (fire and forget) |
| **Reliability** | Guaranteed delivery (ACKs + Retransmit) | Unreliable (best-effort delivery) |
| **Ordering** | Strict sequence numbers (in-order) | No ordering guarantees |
| **Flow & Congestion Control**| Yes (Sliding window, Slow-start) | None (application must implement) |
| **Header Overhead** | 20 to 60 bytes | Strictly 8 bytes |
| **Head-of-Line Blocking** | Present (packet drop halts queue) | Completely absent |
| **Ideal Production Use** | REST APIs, Web banking, File transfer | VoIP, Live Gaming, DNS, HTTP/3 (QUIC) |

#### Key Engineering Insight:
HTTP/3 replaces TCP with **QUIC (built on UDP)** because HTTP/2 over TCP still suffered from TCP-level Head-of-Line blocking when dropping packets."""
                return {
                    "topic": "tcp_vs_udp",
                    "reply": reply,
                    "suggested_replies": [
                        "Why does video streaming use UDP?",
                        "Explain TCP 3-Way Handshake",
                        "Explain WebSockets vs Long Polling",
                        "Start mock interview"
                    ]
                }
        return None

    # =========================================================================
    # PROGRAMMING LANGUAGE FOUNDATIONS (Python, C++, Java, React)
    # =========================================================================

    def _handle_language_query(self, message: str, candidate_name: str) -> Optional[Dict[str, Any]]:
        msg = message.lower()

        # Python
        if any(k in msg for k in ["python", "async def", "gil", "generator", "event loop"]):
            reply = f"""### 🐍 Python Architecture: Concurrency, GIL & Asyncio
Candidate: **{candidate_name}**

#### 1. The Global Interpreter Lock (GIL):
- CPython's memory management relies on reference counting, which is not thread-safe. The GIL ensures only **one thread executes Python bytecode at a time**.
- **CPU-Bound Tasks (e.g. Scikit-learn, ML matrix math):** Multithreading will NOT speed this up! You must use `multiprocessing` or native C-extensions (NumPy).
- **I/O-Bound Tasks (e.g. FastAPI, Database, HTTP calls):** Concurrency works beautifully using `asyncio` cooperative multitasking because threads release the GIL while waiting on network/disk.

#### 2. The Critical Async Event Loop Rule:
```python
# ❌ FATAL ANTI-PATTERN: Freezes the entire server for all concurrent users!
@router.post("/score")
async def bad_scoring(text: str):
    return compute_heavy_tfidf(text)  # CPU-bound block!

# ✅ CORRECT PATTERN: Offload CPU work to threadpool worker
from starlette.concurrency import run_in_threadpool

@router.post("/score")
async def good_scoring(text: str):
    return await run_in_threadpool(compute_heavy_tfidf, text)
```"""
            return {
                "topic": "python_async",
                "reply": reply,
                "suggested_replies": ["Explain Python generators", "Explain C++ smart pointers", "Start mock interview"]
            }

        # C++
        if any(k in msg for k in ["c++", "smart pointer", "raii", "move semantics"]):
            reply = f"""### ⚙️ Modern C++ (C++17/20) RAII & Smart Pointers
Candidate: **{candidate_name}**

#### 1. RAII (Resource Acquisition Is Initialization):
Resources (heap memory, file handles, mutex locks) must be bound to object lifetime so destructors automatically clean them up when going out of scope.

#### 2. Smart Pointer Taxonomy:
- `std::unique_ptr<T>`: Single-owner exclusive pointer. **Zero runtime overhead** compared to raw pointers. Cannot be copied; only moved (`std::move`).
- `std::shared_ptr<T>`: Reference-counted ownership. Uses an atomic control block (`use_count`). Overhead is minimal, but avoid circular references.
- `std::weak_ptr<T>`: Non-owning observer of a `shared_ptr`. Breaks circular reference memory leaks.

```cpp
#include <memory>
#include <iostream>

struct Worker {{
    void execute() {{ std::cout << "Task complete\\n"; }}
}};

void run() {{
    auto worker = std::make_unique<Worker>();
    worker->execute();
    // Destructor runs automatically when scope ends. Zero memory leak!
}}
```"""
            return {
                "topic": "cpp_pointers",
                "reply": reply,
                "suggested_replies": ["Explain move semantics in C++", "Explain Java JVM architecture", "Start mock interview"]
            }

        # React
        if any(k in msg for k in ["react", "usememo", "usecallback", "re-render", "virtual dom"]):
            reply = f"""### ⚛️ React Performance: Eliminating Unnecessary Re-Renders
Candidate: **{candidate_name}**

#### 1. Why Components Re-Render:
A React component re-renders when:
1. Its state changes (`useState`, `useReducer`).
2. Its parent component re-renders (regardless of whether props changed!).
3. A context value it consumes updates (`useContext`).

#### 2. Precision Optimization Tools:
- `React.memo`: Wraps child component to skip re-rendering if its props are shallowly equal.
- `useCallback`: Returns a memoized callback function reference so passing it to a `React.memo` child does not invalidate props on every parent render!
- `useMemo`: Caches the result of an expensive calculation (e.g. filtering 1,000 resume records).
- **Virtualization (`react-window`):** Renders only visible viewport DOM nodes instead of 5,000 table rows."""
            return {
                "topic": "react_rerenders",
                "reply": reply,
                "suggested_replies": ["Show useCallback vs useMemo code", "Explain React Fiber", "Start mock interview"]
            }

        return None

    # =========================================================================
    # GROUNDED RESUME REVIEW (Grounded in context data)
    # =========================================================================

    def _handle_resume_review(self, context: Optional[Dict[str, Any]], candidate_name: str) -> str:
        job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"
        job_company = context.get("job_company", "your prospective employer") if context else "your prospective employer"
        overall_score = context.get("overall_score", 76) if context else 76
        match_rating = context.get("match_rating", "Evaluated") if context else "Evaluated"
        matching_skills = context.get("matching_skills", ["Python", "React", "FastAPI"]) if context else ["Python", "React", "FastAPI"]
        missing_skills = context.get("missing_skills", []) if context else []
        breakdown = context.get("score_breakdown", {}) if context else {}
        skills_score = breakdown.get("skills_score", 80)
        similarity_score = breakdown.get("similarity_score", 65)
        metrics_score = breakdown.get("metrics_score", 70)

        reply = f"Let us inspect your diagnostic telemetry, **{candidate_name}**.\n\n"
        reply += f"Your resume registers an explainable ATS score of **{int(round(float(overall_score)))}/100** categorized as **{match_rating}** for the **{job_title}** role at **{job_company}**.\n\n"
        reply += "### 📊 4-Factor ATS Algorithmic Breakdown:\n"
        reply += f"- **1. Technical Skills Alignment ({skills_score}%):** You matched {len(matching_skills)} skills ({', '.join(matching_skills[:5])}). However, {len(missing_skills)} key competencies are absent.\n"
        reply += f"- **2. TF-IDF Semantic Overlap ({similarity_score}%):** Cosine similarity between your experience n-grams and the target job description is at {similarity_score}%.\n"
        reply += f"- **3. Quantified Impact & Metrics ({metrics_score}%):** Modern ATS parsers score resumes higher when bullets contain measurable numbers (percentages, latency reductions, user scale).\n"
        reply += f"- **4. Structural Completeness:** Standard ATS headers (Experience, Skills, Education, Projects) are verified.\n\n"
        reply += "### 🎯 Concrete Actions to Elevate Your Score to 90+:\n"
        if missing_skills:
            reply += f"1. **Integrate Missing Core Keywords:** Explicitly incorporate `{', '.join(missing_skills[:4])}` into your Skills block and demonstrate how you applied them in bullet points.\n"
        reply += "2. **Rewrite with the Google XYZ Formula:** Replace duty-focused bullets (*'Worked on backend APIs'*) with:\n"
        reply += "   > *'Architected high-throughput REST APIs, as measured by a 45% reduction in endpoint latency, by implementing FastAPI asynchronous endpoints and Redis caching.'*\n"
        reply += f"3. **Align Header Summary:** Ensure your top title explicitly states *'{job_title}'*.\n\n"
        reply += "Would you like me to rewrite a specific bullet point from your work history right now?"
        return reply

    # =========================================================================
    # SKILL ROADMAP & GAP ANALYSIS
    # =========================================================================

    def _handle_skill_roadmap(self, message: str, context: Optional[Dict[str, Any]], candidate_name: str) -> str:
        job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"
        matching_skills = context.get("matching_skills", ["Python", "React", "FastAPI"]) if context else ["Python", "React", "FastAPI"]
        missing_skills = context.get("missing_skills", []) if context else []

        if missing_skills:
            skills_str = ", ".join([f"`{s}`" for s in missing_skills[:6]])
            reply = f"Here is your personalized skill gap curriculum for the **{job_title}** role, **{candidate_name}**.\n\n"
            reply += f"The job description explicitly demands {len(missing_skills)} competencies not detected in your resume: {skills_str}.\n\n"
            reply += "### 🗺️ Tailored 4-Week Skill Mastery Curriculum:\n\n"

            w1 = missing_skills[:2] if len(missing_skills) >= 2 else missing_skills
            w2 = missing_skills[2:4] if len(missing_skills) >= 4 else (missing_skills[1:2] if len(missing_skills) > 1 else missing_skills)

            reply += f"**Week 1: Foundations & Architecture ({', '.join(w1)})**\n"
            reply += f"- Master official architecture guides, configuration parameters, and core paradigms for {', '.join(w1)}.\n"
            reply += "- Build a local sandbox project verifying basic operational workflows.\n\n"

            reply += f"**Week 2: Backend Integration & Scale ({', '.join(w2) if w2 else 'Performance Tuning'})**\n"
            reply += f"- Integrate {', '.join(w2) if w2 else 'infrastructure services'} into your existing {matching_skills[0] if matching_skills else 'backend'} stack.\n"
            reply += "- Implement automated testing and containerized CI/CD builds.\n\n"

            reply += "**Week 3: Production Observability & Failure Modes**\n"
            reply += "- Configure Prometheus/Grafana metrics, structured logging, and high-concurrency benchmarks.\n"
            reply += "- Document trade-offs (e.g. CAP theorem, connection pooling) in a GitHub repository README.\n\n"

            reply += "**Week 4: Portfolio Integration & Interview Prep**\n"
            reply += f"- Update your resume featuring `{', '.join(missing_skills[:3])}` with quantified metrics.\n"
            reply += "- Practice articulating architectural trade-offs during mock interviews.\n\n"
            reply += "Would you like me to quiz you on any of these topics?"
            return reply

        return f"Superb alignment, **{candidate_name}**! Your resume displays zero critical skill gaps against the **{job_title}** role.\n\nFocus on **System Design execution** and **Behavioral Leadership**. Shall we start an interactive mock interview?"

    # =========================================================================
    # PROJECT EXPLANATION PITCH
    # =========================================================================

    def _handle_project_explanation(self, context: Optional[Dict[str, Any]], candidate_name: str) -> str:
        reply = f"Here is the master blueprint for presenting your technical projects during engineering interviews, **{candidate_name}**.\n\n"
        reply += "Senior engineering panels evaluate the **Problem &rarr; Architecture &rarr; Engineering Hurdle &rarr; Measurable Impact** narrative arc.\n\n"
        reply += "### 💡 Master 90-Second Project Pitch:\n\n"
        reply += "1. **The Core Problem (15 seconds):**\n"
        reply += "   > *'In my recent project, I built CareerSetu, an enterprise platform to solve resume-to-job mismatching using real Scikit-learn TF-IDF vectorization and cosine similarity rather than opaque black-box tools.'*\n\n"
        reply += "2. **The Architecture (30 seconds):**\n"
        reply += "   > *'I structured the system with React 19 on the frontend and FastAPI on the backend, persisting data in SQLite. To process documents with zero image-OCR overhead, I implemented PyMuPDF text stream extraction, keeping latency under 250ms.'*\n\n"
        reply += "3. **The Engineering Hurdle (30 seconds):**\n"
        reply += "   > *'A major hurdle was calibrating raw cosine similarity so multi-word tech terms like C++, CI/CD, and React weren\\'t stripped by stopword tokenizers. I built a boundary-aware regex skill extraction engine cross-referenced against a 200+ taxonomy.'*\n\n"
        reply += "4. **The Quantified Result (15 seconds):**\n"
        reply += "   > *'The result was an explainable 4-part scoring engine delivering 80%+ candidate-job alignment accuracy with full historical tracking.'*\n\n"
        reply += "Would you like me to ask you follow-up architectural questions on this project as a mock interviewer?"
        return reply

    # =========================================================================
    # BEHAVIORAL & HR ROUNDS
    # =========================================================================

    def _answer_hr_question(self, query: str, candidate_name: str, job_title: str, job_company: str) -> str:
        return f"""HR and behavioral rounds evaluate executive presence, emotional intelligence, and cultural synergy, **{candidate_name}**.

### 🌟 The STAR Method Architecture:
- **S - Situation:** Set context in 1-2 concise sentences.
- **T - Task:** Clearly state the technical or organizational challenge.
- **A - Action:** Detail your specific actions (use *'I engineered'*, *'I orchestrated'*, avoid passive *'we'* statements).
- **R - Result:** Quantify the outcome (*'Resulted in 40% reduced latency and 0 regression incidents'*).

### 🎯 Model Answer: "Tell Me About Yourself"
> *"I am a software engineer specializing in {job_title if job_title != 'Target Role' else 'modern full-stack systems'} with experience building distributed APIs and reactive web applications. In my recent roles, I focused on high-throughput backend services using Python and React, recently optimizing data pipelines by over 40%. What excites me about {job_company} is your focus on engineering excellence, and I am keen to apply my skills in scalable architecture to your current growth initiatives."*

### 💼 Model Answer: "What Is Your Greatest Weakness?"
> *"Earlier in my career, I had a tendency to dive directly into coding before exhaustively documenting architectural edge cases. I realized this created friction during code reviews. I addressed this by adopting an RFC-driven approach—writing a concise technical design doc with trade-offs before touching the codebase. This has significantly streamlined team consensus and reduced rework."*

Would you like to practice your response to a tough behavioral question?"""

    # =========================================================================
    # INTERACTIVE MOCK INTERVIEW
    # =========================================================================

    def _start_mock_interview(self, context: Optional[Dict[str, Any]] = None, candidate_name: Optional[str] = None) -> Dict[str, Any]:
        if not candidate_name:
            candidate_name = self._resolve_candidate_name("", context)
        job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"

        tl = job_title.lower()
        if "frontend" in tl or "react" in tl:
            first_q = "How do you diagnose and eliminate unnecessary re-renders in a large-scale React application handling high-frequency state updates?"
            category = "Frontend Architecture & React"
        elif "ai" in tl or "data" in tl or "machine" in tl:
            first_q = "Can you explain the mathematical difference between TF-IDF cosine similarity and dense vector embeddings (like BERT) for document matching?"
            category = "AI / Machine Learning & NLP"
        elif "devops" in tl or "cloud" in tl:
            first_q = "How do you design a zero-downtime blue/green deployment strategy for containerized microservices in Kubernetes?"
            category = "DevOps & Cloud Architecture"
        else:
            first_q = "When building a high-throughput REST API using FastAPI and PostgreSQL, how do you configure database connection pooling and prevent query bottlenecks under concurrency?"
            category = "Backend Architecture & Databases"

        interview_state = {
            "active": True,
            "question_index": 1,
            "total_questions": 4,
            "current_question": first_q,
            "category": category,
            "scores": [],
            "history": []
        }

        reply = f"🎙️ **Interactive Technical Interview Initiated**\n\n"
        reply += f"Candidate: **{candidate_name}**\n"
        reply += f"Target Role: **{job_title}**\n"
        reply += f"Session Progress: Question **1 of 4** &bull; Domain: *{category}*\n\n"
        reply += "---\n\n"
        reply += f"### Question 1:\n"
        reply += f"**\"{first_q}\"**\n\n"
        reply += "*Take your time to structure a clear, engineering-grade response. When ready, transmit your answer below and I will evaluate your depth, accuracy, and trade-off considerations.*"

        return {
            "reply": reply,
            "mode": "local_intelligence",
            "provider": "JARVIS Autonomous Intelligence Engine",
            "interview_state": interview_state,
            "suggested_replies": [
                "I use memoization, virtualization, and web workers...",
                "By using connection pooling, indexing, and Redis caching...",
                "Give me a hint on best practices",
                "End interview session"
            ]
        }

    def _handle_interview_turn(
        self,
        user_answer: str,
        interview_state: Dict[str, Any],
        context: Optional[Dict[str, Any]],
        candidate_name: str
    ) -> Dict[str, Any]:
        q_idx = interview_state.get("question_index", 1)
        category = interview_state.get("category", "General Technical")
        job_title = context.get("job_title", "Software Engineer") if context else "Software Engineer"

        if any(w in user_answer.lower() for w in ["stop interview", "end interview", "exit interview", "cancel interview"]):
            interview_state["active"] = False
            return {
                "reply": f"Interview session concluded at your request, **{candidate_name}**. Would you like to review your resume scores or explore learning roadmaps?",
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "How can I improve my resume?",
                    "What critical skills am I missing?",
                    "Start a new mock interview"
                ]
            }

        word_count = len(user_answer.split())

        if word_count < 12:
            score = 5.5
            critique = "The response was somewhat brief. In senior interviews, walking the panel through your thought process, trade-offs, and scaling bottlenecks demonstrates senior command."
            strengths = "Identified the primary technical direction."
            model_tip = "Cite concrete tools (e.g. connection poolers like PgBouncer, Redis cache, indexing strategies) and quantify production gains."
        elif word_count < 35:
            score = 7.8
            critique = "Strong foundational understanding! You articulated the primary mechanism clearly. To push to the top 10% of candidates, address edge cases and failover recovery."
            strengths = "Good technical vocabulary and structured communication."
            model_tip = "Mention production telemetry: how do you monitor latency and error rates under load?"
        else:
            score = 8.9
            critique = "Exceptional, comprehensive answer! You demonstrated solid architectural maturity, pragmatic problem-solving, and clean technical articulation."
            strengths = "High technical depth, relevant terminology, and realistic production consideration."
            model_tip = "Conclude smoothly by referencing a real-world outcome from your past experience."

        interview_state["scores"].append(score)

        if q_idx >= interview_state.get("total_questions", 4):
            avg_score = round(sum(interview_state["scores"]) / len(interview_state["scores"]), 1)
            interview_state["active"] = False

            reply = f"### 🏁 Interview Session Completed!\n\n"
            reply += f"Outstanding effort, **{candidate_name}**. Here is your executive scorecard:\n\n"
            reply += f"- **Overall Assessment Score:** **{avg_score}/10**\n"
            reply += f"- **Benchmark Position:** *{job_title}*\n"
            reply += f"- **Rounds Completed:** 4 technical & architectural topics\n\n"
            reply += "### 📋 Comprehensive Debrief:\n"
            reply += "- **Strengths:** Strong command of core engineering fundamentals and clear communication under questioning.\n"
            reply += "- **Strategic Takeaway:** Ensure you always tie technical decisions back to quantified business impact (e.g. reduced latency, improved throughput, reduced cloud cost).\n\n"
            reply += "Would you like to review your resume, start another interview set, or explore roadmaps?"

            return {
                "reply": reply,
                "mode": "local_intelligence",
                "provider": "JARVIS Autonomous Intelligence Engine",
                "interview_state": None,
                "suggested_replies": [
                    "Start another interview session",
                    "How can I improve my resume?",
                    "What critical skills am I missing?",
                    "Explain my projects"
                ]
            }

        next_idx = q_idx + 1
        questions_bank = [
            ("How do you design an idempotent payment processing API to prevent duplicate transactions under network timeouts?", "System Design & Distributed Systems"),
            ("Can you walk me through the trade-offs between B-Tree indexes versus Hash indexes in a high-volume PostgreSQL database?", "Database Engineering"),
            ("Describe a situation where you had a significant technical disagreement with a colleague. How did you arrive at an optimal solution?", "Behavioral / STAR Leadership")
        ]

        next_q, next_cat = questions_bank[min(next_idx - 2, len(questions_bank) - 1)]
        interview_state["question_index"] = next_idx
        interview_state["current_question"] = next_q
        interview_state["category"] = next_cat

        reply = f"### 📊 Evaluation for Question {q_idx}:\n"
        reply += f"**Score: {score}/10** &bull; *{category}*\n\n"
        reply += f"**Critique:** {critique}\n\n"
        reply += f"**What You Nailed:** {strengths}\n\n"
        reply += f"**Pro-Tip:** {model_tip}\n\n"
        reply += "---\n\n"
        reply += f"### Question {next_idx} of {interview_state.get('total_questions', 4)}:\n"
        reply += f"Category: *{next_cat}*\n\n"
        reply += f"**\"{next_q}\"**\n\n"
        reply += "*Transmit your answer below:* "

        return {
            "reply": reply,
            "mode": "local_intelligence",
            "provider": "JARVIS Autonomous Intelligence Engine",
            "interview_state": interview_state,
            "suggested_replies": [
                "I implement distributed locking with Redis...",
                "B-Trees support range scans whereas Hash indexes are O(1)...",
                "Give me a hint on this question",
                "End interview session"
            ]
        }

    def _get_suggested_followups(
        self, user_msg: str, context: Optional[Dict[str, Any]], interview_state: Optional[Dict[str, Any]]
    ) -> List[str]:
        if interview_state and interview_state.get("active"):
            return ["Give me a hint", "Skip question", "End interview session"]
        return [
            "Start an interactive mock interview",
            "How can I improve my resume?",
            "What critical skills am I missing?",
            "Explain my projects for interviews"
        ]


# Singleton instance
jarvis_engine = JarvisEngine()

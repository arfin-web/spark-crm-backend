import json
import logging
import httpx
from app.core.config import settings

logger = logging.getLogger(__name__)


class GroqAIClient:
    def __init__(self):
        self.api_key = settings.GROQ_AI_API_KEY
        self.model = settings.GROQ_MODEL
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def _get_mock_response(self, feature_type: str, user_input: dict) -> dict:
        """Fallback mock response generator when API key is missing or fails."""
        logger.warning(f"Using mock AI response for feature_type: {feature_type}")
        
        if feature_type == "proposal":
            client_name = user_input.get("client_name", "Valued Client")
            project_name = user_input.get("project_name", "New Project")
            desc = user_input.get("description", "custom agency project")
            
            scope = (
                f"Phase 1: Discovery & Strategy - Define targets for {project_name}.\n"
                f"Phase 2: Execution & Implementation - Deploy standard digital solutions tailored for {client_name}.\n"
                f"Phase 3: Launch, QA & Optimization - Run comprehensive validation and launch client portal."
            )
            deliverables = (
                f"- Brand Strategy & Creative Mockups for {project_name}\n"
                f"- Dynamic Web App / Landing Page built to client specifications\n"
                f"- Comprehensive training documentation and 30-day post-launch support"
            )
            timeline = "6 Weeks (Estimated: Phase 1: 1.5w, Phase 2: 3.5w, Phase 3: 1w)"
            
            # Simple rule-based cost estimation
            cost = 4500.00
            if "high" in desc.lower() or "enterprise" in desc.lower():
                cost = 15000.00
            elif "small" in desc.lower() or "quick" in desc.lower():
                cost = 1800.00
                
            return {
                "scope": scope,
                "deliverables": deliverables,
                "timeline": timeline,
                "cost": cost,
                "input_tokens": 150,
                "output_tokens": 300
            }
            
        elif feature_type == "email_draft":
            client_name = user_input.get("client_name", "Valued Client")
            purpose = user_input.get("purpose", "check_in")
            notes = user_input.get("notes", "")
            
            subject_map = {
                "follow_up": f"Following up on our discussion - {settings.GROQ_MODEL[:5].upper()}",
                "proposal": f"Proposal for review: Next steps - Spark-CRM",
                "check_in": f"Spark-CRM: Quick check-in & project update",
                "custom": f"Update regarding our partnership"
            }
            
            body_map = {
                "follow_up": (
                    f"Hi {client_name},\n\n"
                    f"I wanted to follow up on our recent chat. Let me know if you have any questions "
                    f"or if you're ready to proceed with our proposal. Looking forward to working together!\n\n"
                    f"Best regards,\nSpark Agency Team"
                ),
                "proposal": (
                    f"Hi {client_name},\n\n"
                    f"Attached is our detailed project proposal based on our discussion. Please review "
                    f"and let us know if the scope, timeline, and deliverables align with your goals.\n\n"
                    f"Best regards,\nSpark Agency Team"
                ),
                "check_in": (
                    f"Hi {client_name},\n\n"
                    f"Hope you are having a great week! I wanted to check in and see how everything is going "
                    f"on your side. Let me know if we can assist with anything this week.\n\n"
                    f"Best regards,\nSpark Agency Team"
                ),
                "custom": (
                    f"Hi {client_name},\n\n"
                    f"I'm reaching out to share some exciting progress updates. {notes if notes else 'Let me know a good time to sync up soon.'}\n\n"
                    f"Best regards,\nSpark Agency Team"
                )
            }
            
            return {
                "subject": subject_map.get(purpose, "Project Update"),
                "body": body_map.get(purpose, f"Hi {client_name}, let's catch up soon!"),
                "input_tokens": 120,
                "output_tokens": 200
            }
            
        elif feature_type == "scoring":
            client_name = user_input.get("client_name", "Client")
            activities = user_input.get("activities", [])
            notes = user_input.get("notes", "")
            
            # Simple health score logic: start with 80, modify based on note content & activity count
            score = 80
            explanation = "Client relationship is in stable condition."
            
            if activities:
                score += min(len(activities) * 4, 15)
            else:
                score -= 20
                explanation = "No recent interactions or touchpoints registered in the system."
                
            if notes:
                notes_lower = notes.lower()
                if "happy" in notes_lower or "thrilled" in notes_lower or "great" in notes_lower:
                    score += 10
                    explanation = "Client expressed high satisfaction in recent communications."
                elif "unhappy" in notes_lower or "delay" in notes_lower or "issue" in notes_lower or "frustrated" in notes_lower:
                    score -= 25
                    explanation = "Client noted issues or delays, suggesting relationship friction."
            
            score = max(min(score, 100), 0)
            return {
                "health_score": score,
                "explanation": explanation,
                "input_tokens": 180,
                "output_tokens": 90
            }
            
        elif feature_type == "summary":
            client_name = user_input.get("client_name", "Client")
            activities_summary = user_input.get("activities_summary", "No activities recorded.")
            notes = user_input.get("notes", "")
            
            summary = (
                f"Relationship analysis for {client_name}. "
                f"We have tracked multiple client touchpoints. Notes reflect general engagement: '{notes[:100] if notes else 'N/A'}'. "
                f"Recent touchpoints log: {activities_summary[:150]}"
            )
            recommendations = (
                f"1. Schedule a quick 15-minute call to check alignment.\n"
                f"2. Confirm outstanding items on projects and draft a follow-up email."
            )
            
            return {
                "summary": summary,
                "recommendations": recommendations,
                "input_tokens": 200,
                "output_tokens": 150
            }
            
        return {"error": "Unknown feature type", "input_tokens": 0, "output_tokens": 0}

    async def _call_api(self, messages: list, response_format: dict | None = None) -> tuple[dict, int, int]:
        """Wrapper to call the Groq Chat Completion API."""
        if not self.api_key or self.api_key.startswith("your_") or "change_me" in self.api_key:
            raise ValueError("Invalid API Key")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }
        if response_format:
            payload["response_format"] = response_format

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.base_url,
                headers=self.headers,
                json=payload
            )
            
            if response.status_code != 200:
                logger.error(f"Groq API Error {response.status_code}: {response.text}")
                raise RuntimeError(f"Groq API error: {response.text}")
                
            data = response.json()
            content = data["choices"][0]["message"]["content"]
            
            # Extract token usage
            usage = data.get("usage", {})
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            
            # Parse json if format requested
            if response_format and response_format.get("type") == "json_object":
                try:
                    result = json.loads(content)
                except json.JSONDecodeError:
                    # In case the model did not output proper JSON, fallback
                    logger.error(f"Failed to parse JSON from response: {content}")
                    raise RuntimeError("Failed to parse JSON from AI response")
            else:
                result = {"content": content}
                
            return result, input_tokens, output_tokens

    async def generate_proposal(
        self, client_name: str, client_industry: str | None, project_name: str, brief_description: str
    ) -> dict:
        user_input = {
            "client_name": client_name,
            "project_name": project_name,
            "description": brief_description
        }
        
        system_prompt = (
            "You are an expert agency proposal writer. Write a detailed, realistic project proposal based on client details. "
            "You must output a JSON object containing precisely: 'scope' (markdown string, detailed phases), 'deliverables' "
            "(markdown string, list of specific files/items), 'timeline' (string, e.g. 4 Weeks), and 'cost' (decimal value/float, "
            "appropriate budget for the agency project). DO NOT include markdown code blocks around the JSON output, just the raw JSON."
        )
        
        user_prompt = (
            f"Client Name: {client_name}\n"
            f"Client Industry: {client_industry or 'Digital'}\n"
            f"Project Name: {project_name}\n"
            f"Brief Description: {brief_description}"
        )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            res, in_t, out_t = await self._call_api(messages, response_format={"type": "json_object"})
            res["input_tokens"] = in_t
            res["output_tokens"] = out_t
            return res
        except Exception as e:
            logger.error(f"generate_proposal API call failed: {e}")
            return self._get_mock_response("proposal", user_input)

    async def generate_email_draft(
        self, client_name: str, client_industry: str | None, purpose: str, notes: str | None, client_notes_summary: str | None
    ) -> dict:
        user_input = {
            "client_name": client_name,
            "purpose": purpose,
            "notes": notes
        }
        
        system_prompt = (
            "You are a professional relationship management agent for digital agencies. Generate a highly polished, "
            "context-appropriate email draft. You must output a JSON object containing precisely: 'subject' (string, email subject "
            "line) and 'body' (string, complete email body with place holders if needed, formatting with line breaks). "
            "DO NOT include markdown code blocks around the JSON output, just the raw JSON."
        )
        
        user_prompt = (
            f"Recipient Name: {client_name}\n"
            f"Client Industry: {client_industry or 'Digital'}\n"
            f"Email Purpose: {purpose} (e.g., follow_up, proposal, check_in, custom)\n"
            f"Context / Notes: {notes or 'No additional instructions.'}\n"
            f"Previous Client Activity Summary: {client_notes_summary or 'No history recorded.'}"
        )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            res, in_t, out_t = await self._call_api(messages, response_format={"type": "json_object"})
            res["input_tokens"] = in_t
            res["output_tokens"] = out_t
            return res
        except Exception as e:
            logger.error(f"generate_email_draft API call failed: {e}")
            return self._get_mock_response("email_draft", user_input)

    async def calculate_client_health(
        self, client_name: str, client_notes: str | None, activities_summary: str
    ) -> dict:
        user_input = {
            "client_name": client_name,
            "notes": client_notes,
            "activities": activities_summary.split("\n") if activities_summary else []
        }
        
        system_prompt = (
            "You are a client success analyst. Review the client relationship notes and activity history to assess client satisfaction. "
            "You must output a JSON object containing precisely: 'health_score' (integer between 0 and 100 representing health score, "
            "where 100 is excellent and 0 is severe churn risk) and 'explanation' (string summarizing why this score was selected). "
            "DO NOT include markdown code blocks around the JSON output, just the raw JSON."
        )
        
        user_prompt = (
            f"Client: {client_name}\n"
            f"Overall Relationship Notes: {client_notes or 'None'}\n"
            f"Recent Interaction Activities:\n{activities_summary or 'No recent activities.'}"
        )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            res, in_t, out_t = await self._call_api(messages, response_format={"type": "json_object"})
            res["input_tokens"] = in_t
            res["output_tokens"] = out_t
            return res
        except Exception as e:
            logger.error(f"calculate_client_health API call failed: {e}")
            return self._get_mock_response("scoring", user_input)

    async def generate_client_summary(
        self, client_name: str, client_industry: str | None, activities_summary: str, client_notes: str | None
    ) -> dict:
        user_input = {
            "client_name": client_name,
            "activities_summary": activities_summary,
            "notes": client_notes
        }
        
        system_prompt = (
            "You are an agency account strategist. Analyze a client's history and provide a concise, high-value status summary "
            "and recommendations. You must output a JSON object containing precisely: 'summary' (string, quick paragraph "
            "assessing the client account) and 'recommendations' (string, bullet list of recommended next steps). "
            "DO NOT include markdown code blocks around the JSON output, just the raw JSON."
        )
        
        user_prompt = (
            f"Client Name: {client_name}\n"
            f"Client Industry: {client_industry or 'Digital'}\n"
            f"Recent CRM Activities:\n{activities_summary or 'No activities.'}\n"
            f"Client Account Notes: {client_notes or 'None'}"
        )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            res, in_t, out_t = await self._call_api(messages, response_format={"type": "json_object"})
            res["input_tokens"] = in_t
            res["output_tokens"] = out_t
            return res
        except Exception as e:
            logger.error(f"generate_client_summary API call failed: {e}")
            return self._get_mock_response("summary", user_input)


# Create client instance
ai_client = GroqAIClient()

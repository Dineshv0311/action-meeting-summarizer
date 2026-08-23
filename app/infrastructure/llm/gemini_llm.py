import json
from google import genai
from google.genai import types
from app.interfaces.llm_service import ILLMService
from app.domain.models import MeetingSummaryResult
from app.core.exceptions import AppException

class SummarizationError(AppException):
    def __init__(self, message: str):
        super().__init__(message, status_code=502)

SYSTEM_PROMPT = """
You are an expert Executive Meeting Intelligence Assistant.
Your task is to analyze meeting transcripts and extract accurate, action-oriented intelligence.

Extraction Guidelines:
1. Executive Summary: Write a coherent, dense paragraph highlighting context, main discussions, and outcomes.
2. Key Decisions: Extract explicit conclusions, technical agreements, or strategic decisions made during the discussion.
3. Action Items: Extract every assigned task. Explicitly capture the owner (name) and deadline (timeframe/date) if stated. If not stated, assign 'Unassigned' or 'Unspecified'.
4. Open Questions: List lingering blockers, unresolved questions, or items deferred to subsequent meetings.
5. Strict Grounding: Extract only information explicitly supported by the transcript. Do not fabricate facts.
"""

class GeminiSummarizerService(ILLMService):
    """Gemini implementation of ILLMService with structured JSON output."""

    # Updated default model to gemini-3.6-flash
    def __init__(self, api_key: str, model_name: str = "gemini-3.6-flash"):
        if not api_key:
            raise ValueError("GEMINI_API_KEY is missing in environment variables.")
        self._client = genai.Client(api_key=api_key)
        self._model_name = model_name

    def summarize_transcript(self, transcript: str) -> MeetingSummaryResult:
        if not transcript or not transcript.strip():
            raise SummarizationError("Cannot summarize an empty transcript.")

        prompt = f"Analyze the following meeting transcript and produce structured action-oriented output:\n\n{transcript}"

        try:
            response = self._client.models.generate_content(
                model=self._model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_PROMPT,
                    response_mime_type="application/json",
                    response_schema=MeetingSummaryResult,
                    temperature=0.2,
                ),
            )

            parsed_dict = json.loads(response.text)
            return MeetingSummaryResult(**parsed_dict)

        except Exception as e:
            raise SummarizationError(f"Gemini summarization failed: {str(e)}") from e
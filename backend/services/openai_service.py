# backend/services/openai_service.py
import logging
from openai import AsyncOpenAI # Use the async client
# --- ADD THIS IMPORT ---
from typing import Optional
# --- END ADD ---
from schemas.mood import SentimentAnalysisResult # Import result schema

logger = logging.getLogger(__name__)

async def analyze_journal_entry(
    openai_client: AsyncOpenAI, # Inject the client instance
    text: str
) -> Optional[SentimentAnalysisResult]:
    """
    Analyzes the sentiment of a journal entry using OpenAI GPT model.
    Expects the OpenAI client to be initialized and passed in.
    Returns a Pydantic model with results or None if analysis fails.
    """
    if not text or not text.strip():
        logger.debug("Skipping sentiment analysis for empty journal text.")
        return None

    # Construct the prompt for OpenAI's ChatCompletion endpoint with JSON mode
    prompt = f"""Analyze the following journal entry. Provide the output ONLY in valid JSON format with EXACTLY these keys: "sentiment", "intensity", and "summary".

    Rules:
    1. Classify the overall sentiment as one of: "Positive", "Negative", "Neutral".
    2. Rate the emotional intensity on a scale from 1 (very low) to 10 (very high). This reflects the strength of the expressed emotion, regardless of whether it's positive or negative. Neutral entries should generally have low intensity (1-3).
    3. Provide a concise, one-sentence summary of the emotional tone.
    4. Attempt to capture nuance like sarcasm or mixed feelings in the summary if possible. Intensity should reflect the dominant emotion.

    Journal Entry:
    \"\"\"
    {text}
    \"\"\"

    JSON Output:
    """

    try:
        logger.info(f"Sending journal text to OpenAI for analysis (first 50 chars): {text[:50]}...")
        response = await openai_client.chat.completions.create(
            # Consider cost/performance: gpt-3.5-turbo might be sufficient and cheaper
            model="gpt-3.5-turbo",
            # model="gpt-4-turbo-preview", # Or your preferred GPT-4 model ID
            response_format={"type": "json_object"}, # Enable JSON mode
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert sentiment analysis assistant. Analyze the user's journal entry based on the rules provided and return the analysis ONLY as a valid JSON object with keys 'sentiment', 'intensity', and 'summary'."
                },
                {"role": "user", "content": prompt}
            ],
            temperature=0.3, # Keep temperature relatively low for consistent classification
            max_tokens=150, # Usually enough for the structured JSON output
            timeout=25.0, # Set a reasonable timeout for the API call
        )

        # Access the response content
        if response.choices and response.choices[0].message and response.choices[0].message.content:
            content_str = response.choices[0].message.content
            logger.debug(f"Raw OpenAI response content: {content_str}")
            # Validate the response using the Pydantic model
            try:
                analysis_data = SentimentAnalysisResult.model_validate_json(content_str)
                logger.info(f"Sentiment analysis successful: {analysis_data.sentiment} ({analysis_data.intensity})")
                return analysis_data
            except Exception as json_error:
                logger.error(f"Failed to parse JSON response from OpenAI: {json_error} - Content: {content_str}")
                return None
        else:
            logger.warning(f"Received no valid choice/content from OpenAI API.")
            return None

    except Exception as e:
        # Log OpenAI API errors
        logger.error(f"Error calling OpenAI API for sentiment analysis: {e}", exc_info=True)
        return None # Return None on failure
"""
Gemini AI Integration for Legal Document Understanding
Handles legal question answering with context from retrieved documents.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GeminiLegalAssistant:
    """
    Google Gemini integration for legal document question answering.
    """

    def __init__(self,
                 model_name: str = "gemini-2.5-flash",
                 api_key: Optional[str] = None):
        """
        Initialize the Gemini legal assistant.

        Args:
            model_name: Name of the Gemini model to use
            api_key: Gemini API key (optional, will use env var)
        """
        self.model_name = model_name
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError("Gemini API key not found. Set GEMINI_API_KEY environment variable.")

        # Initialize Gemini client
        self.client = genai.Client(api_key=self.api_key)

        # Configure safety settings for legal content
        self.safety_settings = [
            types.SafetySetting(
                category="HARM_CATEGORY_HARASSMENT",
                threshold="BLOCK_LOW_AND_ABOVE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_HATE_SPEECH",
                threshold="BLOCK_LOW_AND_ABOVE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_SEXUALLY_EXPLICIT",
                threshold="BLOCK_LOW_AND_ABOVE",
            ),
            types.SafetySetting(
                category="HARM_CATEGORY_DANGEROUS_CONTENT",
                threshold="BLOCK_MEDIUM_AND_ABOVE",
            ),
        ]

    def generate_legal_response(self,
                              query: str,
                              context_chunks: List[Dict[str, Any]],
                              conversation_history: Optional[List[Dict[str, str]]] = None,
                              streaming: bool = False) -> str:
        """
        Generate a legal response based on user query and retrieved context.

        Args:
            query: User's legal question
            context_chunks: Retrieved relevant document chunks
            conversation_history: Previous conversation turns
            streaming: Whether to use streaming response

        Returns:
            Generated legal response
        """
        try:
            # Prepare context from retrieved chunks
            context = self._prepare_context(context_chunks)

            # Build the prompt
            prompt = self._build_legal_prompt(query, context, conversation_history)

            # Prepare contents for Gemini
            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]

            # Configure generation
            generate_config = types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=-1),  # Enable thinking
                safety_settings=self.safety_settings,
                tools=[types.Tool(googleSearch=types.GoogleSearch())],  # Enable web search if needed
                temperature=0.1,  # Low temperature for factual responses
                top_p=0.8,
                top_k=40,
                max_output_tokens=2048,
            )

            if streaming:
                return self._generate_streaming_response(contents, generate_config)
            else:
                return self._generate_single_response(contents, generate_config)

        except Exception as e:
            logger.error(f"Error generating legal response: {e}")
            return self._generate_fallback_response(query)

    def _prepare_context(self, context_chunks: List[Dict[str, Any]]) -> str:
        """
        Prepare context string from retrieved chunks.

        Args:
            context_chunks: List of retrieved document chunks

        Returns:
            Formatted context string
        """
        if not context_chunks:
            return "No relevant legal documents found for this query."

        context_parts = []

        for i, chunk in enumerate(context_chunks, 1):
            chunk_info = f"""
Document: {chunk.get('document_filename', 'Unknown')}
Type: {chunk.get('document_type', 'General Legal')}
Relevance Score: {chunk.get('score', 0):.3f}
Content: {chunk.get('content', '')}

---"""
            context_parts.append(chunk_info)

        return "\n".join(context_parts)

    def _build_legal_prompt(self,
                          query: str,
                          context: str,
                          conversation_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        Build a comprehensive legal prompt for Gemini.

        Args:
            query: User's legal question
            context: Retrieved context
            conversation_history: Previous conversation

        Returns:
            Formatted prompt
        """
        # Build conversation context if available
        conversation_context = ""
        if conversation_history:
            history_parts = []
            for turn in conversation_history[-3:]:  # Last 3 turns
                history_parts.append(f"User: {turn.get('user', '')}")
                history_parts.append(f"Assistant: {turn.get('assistant', '')}")
            conversation_context = "\n".join(history_parts)

        prompt = f"""You are an expert legal assistant helping general users understand legal documents and clauses.

CONVERSATION HISTORY:
{conversation_context}

RETRIEVED LEGAL CONTEXT:
{context}

CURRENT USER QUESTION: {query}

INSTRUCTIONS FOR LEGAL ANALYSIS:

1. **Accuracy First**: Base your answer primarily on the provided legal context
2. **Plain Language**: Explain legal concepts in simple, everyday terms that anyone can understand
3. **Practical Impact**: Focus on what this means for the user's rights, obligations, and practical implications
4. **Structure Your Response**:
   - Start with a clear, direct answer
   - Explain the legal basis from the documents
   - Highlight key rights and responsibilities
   - Include practical examples or scenarios
   - Note any limitations or exceptions
   - End with appropriate disclaimers

5. **Legal Disclaimers**: Always include that this is general information and users should consult qualified legal professionals for their specific situation

6. **Handle Uncertainty**: If the context doesn't fully answer the question, clearly state what you can and cannot determine from the documents

RESPONSE FORMAT:
- **Clear Answer**: Direct response to the question
- **Legal Basis**: Reference to specific document sections/clauses
- **Practical Implications**: What this means in real life
- **Important Notes**: Any limitations, exceptions, or additional considerations
- **Disclaimer**: Professional legal advice recommendation

Please provide a comprehensive yet accessible legal analysis based on the provided context."""

        return prompt

    def _generate_single_response(self, contents: List, config: types.GenerateContentConfig) -> str:
        """
        Generate a single (non-streaming) response.

        Args:
            contents: Message contents
            config: Generation configuration

        Returns:
            Generated response text
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            return response.text if response.text else "I apologize, but I couldn't generate a response. Please try rephrasing your question."

        except Exception as e:
            logger.error(f"Error in single response generation: {e}")
            return self._generate_fallback_response("")

    def _generate_streaming_response(self, contents: List, config: types.GenerateContentConfig):
        """
        Generate a streaming response.

        Args:
            contents: Message contents
            config: Generation configuration

        Returns:
            Generator yielding response chunks
        """
        try:
            for chunk in self.client.models.generate_content_stream(
                model=self.model_name,
                contents=contents,
                config=config
            ):
                if chunk.text:
                    yield chunk.text

        except Exception as e:
            logger.error(f"Error in streaming response generation: {e}")
            yield "I apologize, but I encountered an error generating the response. Please try again."

    def _generate_fallback_response(self, query: str) -> str:
        """
        Generate a fallback response when main generation fails.

        Args:
            query: Original user query

        Returns:
            Fallback response
        """
        return f"""I apologize, but I'm having trouble generating a comprehensive response to your legal question: "{query}"

While I cannot provide specific legal analysis at the moment, here are some general recommendations:

1. **Consult Primary Sources**: Always refer to the actual legal documents and official government websites
2. **Seek Professional Advice**: For personal legal matters, consult with qualified attorneys or legal experts
3. **Understand Your Rights**: Legal documents often contain important information about rights, obligations, and procedures
4. **Document Everything**: Keep records of all legal communications and transactions

Please try rephrasing your question or ask about a different aspect of legal documents."""

    def analyze_legal_document(self,
                             document_text: str,
                             analysis_type: str = "summary") -> str:
        """
        Analyze a legal document for specific insights.

        Args:
            document_text: Full document text
            analysis_type: Type of analysis ("summary", "key_clauses", "risks")

        Returns:
            Analysis result
        """
        try:
            analysis_prompts = {
                "summary": "Provide a concise summary of this legal document, highlighting the main purpose and key provisions.",
                "key_clauses": "Identify and explain the key clauses and provisions in this legal document.",
                "risks": "Analyze this legal document for potential risks, obligations, and important considerations for the involved parties.",
                "rights": "Explain the rights and protections outlined in this legal document."
            }

            prompt = f"""You are a legal document analyzer. Please analyze the following document:

{analysis_prompts.get(analysis_type, analysis_prompts['summary'])}

DOCUMENT TEXT:
{document_text[:4000]}... (truncated for analysis)

Please provide a clear, structured analysis focusing on practical implications."""

            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]

            config = types.GenerateContentConfig(
                safety_settings=self.safety_settings,
                temperature=0.1,
                max_output_tokens=1024
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            return response.text if response.text else "Unable to analyze the document at this time."

        except Exception as e:
            logger.error(f"Error analyzing legal document: {e}")
            return "Document analysis is currently unavailable. Please try again later."

    def compare_legal_texts(self,
                          text1: str,
                          text2: str,
                          comparison_type: str = "differences") -> str:
        """
        Compare two legal texts.

        Args:
            text1: First legal text
            text2: Second legal text
            comparison_type: Type of comparison

        Returns:
            Comparison analysis
        """
        try:
            prompt = f"""Compare these two legal texts and highlight the key {comparison_type}:

TEXT 1:
{text1[:2000]}...

TEXT 2:
{text2[:2000]}...

Please provide a structured comparison focusing on legal implications and practical differences."""

            contents = [types.Content(
                role="user",
                parts=[types.Part.from_text(text=prompt)]
            )]

            config = types.GenerateContentConfig(
                safety_settings=self.safety_settings,
                temperature=0.1,
                max_output_tokens=1024
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config
            )

            return response.text if response.text else "Unable to compare the texts at this time."

        except Exception as e:
            logger.error(f"Error comparing legal texts: {e}")
            return "Text comparison is currently unavailable."


# Usage example
if __name__ == "__main__":
    # Initialize the assistant
    assistant = GeminiLegalAssistant()

    # Example query
    query = "What are the tenant rights under rent control acts?"
    context_chunks = [
        {
            "content": "Under the rent control act, tenants have the right to continue tenancy as long as they pay rent regularly.",
            "document_filename": "rent_control_act.pdf",
            "score": 0.85
        }
    ]

    # Generate response
    response = assistant.generate_legal_response(query, context_chunks)
    print(response)

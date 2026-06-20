# backend/services/llm_service.py
# FULL IMPLEMENTATION — replaces stub from Step 3

import os
import logging

from google import genai

from utils.prompt_templates import (
    build_rag_prompt,
    build_revision_prompt,
    build_interview_questions_prompt,
    format_chunks_as_context
)

logger = logging.getLogger(__name__)

MODEL_NAME = "gemini-2.5-flash"

# Generation config controls how the model generates text.
# temperature=0.3: Low randomness — we want factual, consistent answers.
#   0.0 = fully deterministic, 1.0 = very creative/random.
#   For interview prep (factual domain), low temperature is correct.
# max_output_tokens=1024: Max response length (~750 words). Enough for
#   detailed answers without runaway generation.



def call_gemini(prompt: str) -> str:
    try:
        client = genai.Client(
            api_key=os.getenv("GOOGLE_API_KEY")
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt
        )

        return response.text

    except Exception as e:
        logger.exception("Gemini API call failed")
        raise RuntimeError(
            f"LLM generation failed: {str(e)}"
        )

async def generate_answer(
    question: str,
    context_chunks: list[dict]
) -> str:
    """
    Generates a RAG-based answer for a user question.

    Args:
        question:       The user's question
        context_chunks: Retrieved chunks from ChromaDB

    Returns:
        Generated answer string

    Flow:
    1. Format chunks into readable context string
    2. Build the full prompt with context + question
    3. Call Gemini
    4. Return the answer
    """
    if not context_chunks:
        return (
            "I couldn't find relevant information in your uploaded documents "
            "for this question. Please try:\n"
            "- Uploading more study materials on this topic\n"
            "- Rephrasing your question\n"
            "- Removing filters if you have any active"
        )

    # Format chunks into the context string
    context = format_chunks_as_context(context_chunks)

    # Build the complete prompt
    prompt = build_rag_prompt(context=context, question=question)

    logger.info(
        f"Calling Gemini for RAG answer | "
        f"question='{question[:60]}' | "
        f"context_chunks={len(context_chunks)} | "
        f"prompt_length={len(prompt)} chars"
    )

    # Generate and return
    answer = call_gemini(prompt)
    logger.info(f"Generated answer: {len(answer)} chars")
    return answer


async def generate_revision_notes(
    topic: str,
    context_chunks: list[dict]
) -> str:
    """
    Generates structured revision notes for a topic.

    Args:
        topic:          Topic to generate notes for (e.g., "DBMS", "OS")
        context_chunks: Retrieved chunks relevant to the topic

    Returns:
        Formatted revision notes string
    """
    if not context_chunks:
        return (
            f"No uploaded documents found for '{topic}'. "
            f"Please upload study notes on this topic first."
        )

    context = format_chunks_as_context(context_chunks)
    prompt  = build_revision_prompt(context=context, topic=topic)

    logger.info(f"Generating revision notes | topic='{topic}' | chunks={len(context_chunks)}")

    notes = call_gemini(prompt)
    logger.info(f"Generated revision notes: {len(notes)} chars")
    return notes


async def generate_interview_questions(
    topic: str,
    context_chunks: list[dict],
    num_questions: int = 20,
    company: str | None = None
) -> str:
    """
    Generates interview questions based on uploaded content.

    Args:
        topic:          Topic to generate questions for
        context_chunks: Retrieved chunks from ChromaDB
        num_questions:  How many questions to generate
        company:        Optional company focus (e.g., "amazon")

    Returns:
        Formatted interview questions string
    """
    if not context_chunks:
        return (
            f"No uploaded documents found for '{topic}'. "
            f"Please upload study notes or interview experiences first."
        )

    context = format_chunks_as_context(context_chunks)
    prompt  = build_interview_questions_prompt(
        context=context,
        topic=topic,
        num_questions=num_questions,
        company=company
    )

    logger.info(
        f"Generating interview questions | "
        f"topic='{topic}' | "
        f"num={num_questions} | "
        f"company={company}"
    )

    questions = call_gemini(prompt)

    print("\n\n========== GEMINI RESPONSE ==========\n")
    print(questions)
    print("\n=====================================\n")

    logger.info(
        f"Generated {num_questions} interview questions: {len(questions)} chars"
    )

    return questions

def quota_fallback(prompt_type: str):
    if prompt_type == "revision":
        return """
# Revision Notes

Gemini quota exceeded.
Fallback content generated.

Key concepts:
- Deadlock
- ACID Properties
- Normalization
"""
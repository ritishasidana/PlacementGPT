# backend/utils/prompt_templates.py  (complete replacement)

# ─────────────────────────────────────────────────────────────────────────────
# PROMPT ENGINEERING NOTES (explain this in interviews):
#
# 1. Role assignment   → tells Gemini WHO it is → calibrates tone/depth
# 2. Context labeling  → SOURCE headers help Gemini attribute correctly
# 3. Hard constraints  → "ONLY use context" reduces hallucination
# 4. Output structure  → explicit format → consistent, parseable output
# 5. Negative examples → "Do NOT" instructions are surprisingly effective
# ─────────────────────────────────────────────────────────────────────────────


# ── RAG Answer Prompt ──────────────────────────────────────────────────────────
RAG_ANSWER_PROMPT = """You are PlacementGPT, an expert AI assistant helping \
engineering students prepare for campus placements and technical interviews.

You have been given relevant excerpts from the student's own uploaded study \
materials and interview experiences. Answer their question using ONLY the \
provided context.

CONTEXT FROM UPLOADED DOCUMENTS:
{context}

STUDENT'S QUESTION:
{question}

INSTRUCTIONS:
1. Answer using ONLY the information in the context above.
2. If context lacks sufficient information, say exactly:
   "I couldn't find specific information about this in your uploaded documents. Try uploading more notes on this topic."
3. For technical concepts: include definition, how it works, and an example.
4. If context includes interview experiences, mention which company asked it.
5. Use clear structure: short paragraphs or bullet points where appropriate.
6. Do NOT invent information not present in the context.
7. End with one "💡 Interview Tip:" sentence relevant to the question.
8. When explaining algorithms, protocols, scheduling methods, page replacement algorithms, networking protocols, or DBMS techniques, use Markdown Heading Level 3 (###) for the algorithm name and bullet points only for details.


ANSWER:"""


# ── Revision Notes Prompt ──────────────────────────────────────────────────────
REVISION_NOTES_PROMPT = """You are PlacementGPT, an expert at creating \
structured, exam-ready revision notes for engineering placement preparation.

The student has uploaded their own study materials. Use ONLY the provided \
context to generate revision notes. Do not add information from outside \
the context.

TOPIC: {topic}

CONTEXT FROM STUDENT'S UPLOADED DOCUMENTS:
{context}

Generate comprehensive revision notes using EXACTLY this structure:

## 📌 Topic Overview
[2-3 sentence summary of {topic} — what it is and why it matters]

## 🔑 Key Concepts & Definitions
[Bullet list of must-know terms with one-line definitions from the context]

## 📖 Important Details
Use short paragraphs.
Avoid excessive blank lines.
Avoid nested bullet lists unless absolutely necessary.

## ⚙️ Algorithms / Formulas / Techniques

For every algorithm, protocol, technique, formula, or model, use Markdown Heading Level 3.

CORRECT FORMAT:

### First-In, First-Out (FIFO)

* Definition: ...
* How it Works: ...
* Example: ...
* Drawbacks: ...

### Optimal (OPT)

* Definition: ...
* How it Works: ...
* Example: ...
* Drawbacks: ...

### Least Recently Used (LRU)

* Definition: ...
* How it Works: ...
* Example: ...
* Drawbacks: ...

IMPORTANT RULES:

* Algorithm names MUST use Markdown Heading Level 3 (###).
* Never write algorithm names as bullet points.
* Never write algorithm names as numbered lists.
* Never place a bullet point before a heading.
* Only Definition, How it Works, Example, Advantages, Disadvantages, and Drawbacks may use bullet points.
* Do NOT create nested bullet lists.
* Keep spacing compact.
* Leave only one blank line between sections.
* Do not insert large vertical gaps between headings and bullet points.

BAD EXAMPLE:

* First-In, First-Out (FIFO)

  * Definition: ...
  * Example: ...

GOOD EXAMPLE:

### First-In, First-Out (FIFO)

* Definition: ...
* Example: ...

### Optimal (OPT)

* Definition: ...
* Example: ...

REVISION NOTES:"""

# ── Interview Questions Prompt ─────────────────────────────────────────────────
INTERVIEW_QUESTIONS_PROMPT = """You are PlacementGPT, an expert at generating \
targeted technical interview questions for engineering campus placements.

You have access to two types of context:
1. Study notes — theoretical content on the topic
2. Interview experiences — real questions asked at companies

Use BOTH to generate questions that are technically accurate AND \
company-relevant.

TOPIC: {topic}
TARGET COMPANY: {company_display}
NUMBER OF QUESTIONS: {num_questions}

CONTEXT FROM STUDENT'S UPLOADED DOCUMENTS:
{context}

Generate EXACTLY {num_questions} interview questions.

IMPORTANT RULES:
- You MUST generate all {num_questions} questions.
- Do NOT stop after Question 1.
- Number questions sequentially as Q1, Q2, Q3 ... Q{num_questions}.
- If response length becomes large, shorten the Expected Answer instead of generating fewer questions.
- Every question must contain all fields below.

Use EXACTLY this format for EACH question:

**Q1: [Question text]**
> **Difficulty**: [Easy / Medium / Hard]
> **Expected Answer**: [Concise answer in 1-2 sentences]
> **Follow-up**: [One follow-up question]
> **Source**: [Document or company source]

**Q2: [Question text]**
> **Difficulty**: [Easy / Medium / Hard]
> **Expected Answer**: [Concise answer in 1-2 sentences]
> **Follow-up**: [One follow-up question]
> **Source**: [Document or company source]

Continue until Q{num_questions}.

GUIDELINES:
- {company_instruction}
- Mix difficulties: ~30% Easy, ~50% Medium, ~20% Hard
- Cover both conceptual ("What is X?") and applied ("How would you handle X?")
- For Easy: definitions and basic concepts
- For Medium: comparisons, tradeoffs, how things work
- For Hard: design decisions, edge cases, implementation details
- Prioritize questions that appear in the interview experiences in the context
- Do NOT repeat the same question with different wording

INTERVIEW QUESTIONS:"""


# ── Instruction fragments ──────────────────────────────────────────────────────
COMPANY_FOCUS_INSTRUCTION = (
    "Prioritize questions actually asked at {company} based on the interview "
    "experiences in the context. Label company-sourced questions clearly."
)

GENERAL_INSTRUCTION = (
    "Draw questions from all interview experiences in the context. "
    "Label which company asked each question where traceable."
)


# ── Builder functions ──────────────────────────────────────────────────────────

def build_rag_prompt(context: str, question: str) -> str:
    return RAG_ANSWER_PROMPT.format(
        context=context,
        question=question
    )


def build_revision_prompt(context: str, topic: str) -> str:
    return REVISION_NOTES_PROMPT.format(
        context=context,
        topic=topic
    )


def build_interview_questions_prompt(
    context:       str,
    topic:         str,
    num_questions: int,
    company:       str | None = None
) -> str:
    company_display = company.title() if company else "All Companies"
    company_instruction = (
        COMPANY_FOCUS_INSTRUCTION.format(company=company.title())
        if company else GENERAL_INSTRUCTION
    )
    return INTERVIEW_QUESTIONS_PROMPT.format(
        context=context,
        topic=topic,
        num_questions=num_questions,
        company_display=company_display,
        company_instruction=company_instruction
    )


def format_chunks_as_context(chunks: list[dict]) -> str:
    """
    Formats retrieved chunks into a labeled context block.

    Separates theory chunks from interview experience chunks visually
    so Gemini can distinguish source types.
    """
    if not chunks:
        return "No relevant context found in uploaded documents."

    theory_chunks    = []
    interview_chunks = []

    for i, chunk in enumerate(chunks, start=1):
        doc_type = chunk.get("metadata", {}).get("doc_type", "")
        entry = {
            "index":    i,
            "chunk":    chunk,
            "source":   chunk.get("metadata", {}).get("source", f"Source {i}"),
            "text":     chunk.get("text", ""),
        }
        if doc_type == "interview_experience":
            interview_chunks.append(entry)
        else:
            theory_chunks.append(entry)

    parts = []

    # Theory sections
    if theory_chunks:
        parts.append("=== STUDY NOTES ===")
        for entry in theory_chunks:
            parts.append(
                f"--- SOURCE {entry['index']}: {entry['source']} ---\n"
                f"{entry['text']}"
            )

    # Interview experience sections
    if interview_chunks:
        parts.append("\n=== INTERVIEW EXPERIENCES ===")
        for entry in interview_chunks:
            company = entry["chunk"].get("metadata", {}).get("company", "Unknown")
            parts.append(
                f"--- SOURCE {entry['index']}: {entry['source']} "
                f"[Company: {company.title()}] ---\n"
                f"{entry['text']}"
            )

    return "\n\n".join(parts)
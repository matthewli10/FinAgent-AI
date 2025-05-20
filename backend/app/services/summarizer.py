import os
from openai import OpenAI
from app.services.sanitizer import sanitize_transcript  # ✅ new import

def split_transcript_into_chunks(text: str, max_words: int = 2200) -> list:
    words = text.split()
    chunks = []
    for i in range(0, len(words), max_words):
        chunk = " ".join(words[i:i+max_words])
        chunks.append(chunk)
    return chunks

def summarize_chunk(chunk: str, chunk_index: int) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    prompt = (
        f"You are a financial analyst. This is part {chunk_index} of an earnings call transcript.\n"
        "Summarize any financial results, EPS, revenue, forward guidance, and any quotes from the CEO/CFO.\n\n"
        f"Chunk:\n{chunk}"
    )

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=400
    )

    return response.choices[0].message.content.strip()

def combine_chunk_summaries(summaries: list) -> str:
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    combined_prompt = (
        "You are a senior financial analyst. Given the following summaries of an earnings call, "
        "write a final, concise summary with all key results (EPS, revenue, guidance), and tone of the call.\n\n"
    )
    combined_prompt += "\n\n".join([f"Part {i+1}:\n{summary}" for i, summary in enumerate(summaries)])

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": combined_prompt}],
        temperature=0.3,
        max_tokens=500
    )

    return response.choices[0].message.content.strip()

def summarize_transcript(transcript_text: str, ticker: str) -> str:
    # ✅ sanitize before doing anything
    cleaned_text = sanitize_transcript(transcript_text)
    chunks = split_transcript_into_chunks(cleaned_text, max_words=2200)
    partial_summaries = [summarize_chunk(chunk, i+1) for i, chunk in enumerate(chunks)]
    final_summary = combine_chunk_summaries(partial_summaries)
    return final_summary

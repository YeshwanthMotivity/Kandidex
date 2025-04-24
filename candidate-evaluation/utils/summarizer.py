from transformers import pipeline
from concurrent.futures import ThreadPoolExecutor


# summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
# summarizer = pipeline("summarization", model="facebook/bart-base")
summarizer = pipeline("summarization", model="Falconsai/text_summarization")

def summarize_single_chunk(chunk, max_chunk_length=150, min_chunk_length=40):
    return summarizer(
        chunk,
        max_length=max_chunk_length,
        min_length=min_chunk_length,
        do_sample=False
    )[0]['summary_text']
    

def summarize_chunks_parallel(chunks, max_chunk_length=150, min_chunk_length=40):
    """
    Summarizes a list of text chunks in parallel.
    """
    
    print("⚡ Running summarization in parallel...")
    with ThreadPoolExecutor() as executor:
        results = list(executor.map(
            lambda chunk: summarize_single_chunk(chunk, max_chunk_length, min_chunk_length),
            chunks
        ))
    return results

def summarize_text(text, max_tokens=1024, max_chunk_length=150, min_chunk_length=40):
    """
    Splits a long text into chunks and summarizes them in parallel.

    Args:
        text (str): The input text to be summarized.
        max_tokens (int): Max character length per chunk (approximate).
        max_chunk_length (int): Max summary length per chunk.
        min_chunk_length (int): Min summary length per chunk.

    Returns:
        str: Combined summary text.
    """
    # Split the text into manageable chunks
    chunks = [text[i:i+max_tokens] for i in range(0, len(text), max_tokens)]

    # Parallel summarization
    summaries = summarize_chunks_parallel(chunks, max_chunk_length, min_chunk_length)
    return " ".join(summaries)

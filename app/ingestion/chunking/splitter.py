from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
import logfire


def chunk_text(text: str, chunk_size: int = 1500) -> List[str]:
    with logfire.span("✂️ Text Chunking", text_length=len(text)):

        if not text.strip():
            return []

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

        chunks = splitter.split_text(text)

        logfire.info(f"✅ Generated {len(chunks)} chunks")

        return chunks
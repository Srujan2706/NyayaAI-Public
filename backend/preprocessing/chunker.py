import json
import logging
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import tiktoken

from backend.utils.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    PERMANENT_CHUNKS,
    PERMANENT_CLEANED,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Initialize tokenizer once
enc = tiktoken.get_encoding("cl100k_base")


@dataclass
class SectionData:
    """Dataclass to hold parent section data before chunking."""
    parent_id: str
    law: str
    law_full_name: str
    part: Optional[str]
    chapter: Optional[str]
    chapter_title: Optional[str]
    section: str
    title: str
    text: str
    source_file: str


@dataclass
class ChunkData:
    """Dataclass to hold individual chunk data."""
    chunk_id: str
    parent_id: str
    law: str
    law_full_name: str
    part: Optional[str]
    part_no: Optional[str]
    chapter: Optional[str]
    chapter_no: Optional[str]
    chapter_title: Optional[str]
    section: str
    section_no: Optional[str]
    title: str
    chunk_no: int
    total_chunks: int
    text: str
    token_count: int
    token_start: int
    token_end: int
    previous_chunk_id: Optional[str]
    next_chunk_id: Optional[str]
    source_file: str
    chunk_type: str
    hierarchy_path: str


def detect_law(filename: str) -> Tuple[str, str]:
    """Detect law ONLY from filename."""
    name = Path(filename).stem.upper()
    if name.startswith("BNSS"):
        return "BNSS", "Bharatiya Nagarik Suraksha Sanhita, 2023"
    elif name.startswith("BNS"):
        return "BNS", "Bharatiya Nyaya Sanhita, 2023"
    elif name.startswith("BSA"):
        return "BSA", "Bharatiya Sakshya Adhiniyam, 2023"
    elif name.startswith("CONSTITUTION"):
        return "Constitution", "Constitution of India"
    return Path(filename).stem, Path(filename).stem


def remove_table_of_contents(text: str) -> str:
    """Removes TOC and begins parsing from the actual Act body."""
    enacted_match = re.search(r'BE\s+it\s+enacted', text, re.IGNORECASE)
    if enacted_match:
        body_text = text[enacted_match.end():]
        chapter_match = re.search(r'^\s*(?:CHAPTER\s+I|PART\s+I)\b', body_text, re.IGNORECASE | re.MULTILINE)
        if chapter_match:
            chapter_text = body_text[chapter_match.start():]
            sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', chapter_text, re.IGNORECASE | re.MULTILINE)
            if sec1_match:
                return chapter_text[sec1_match.start():]
            return chapter_text
        sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', body_text, re.IGNORECASE | re.MULTILINE)
        if sec1_match:
            return body_text[sec1_match.start():]
        return body_text

    const_match = re.search(r'WE,\s+THE\s+PEOPLE\s+OF\s+INDIA', text, re.IGNORECASE)
    if const_match:
        body_text = text[const_match.start():]
        sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', body_text, re.IGNORECASE | re.MULTILINE)
        if sec1_match:
            return body_text[sec1_match.start():]
        return body_text

    chapter_matches = list(re.finditer(r'^\s*CHAPTER\s+I\b', text, re.IGNORECASE | re.MULTILINE))
    if len(chapter_matches) >= 2:
        chapter_text = text[chapter_matches[1].start():]
        sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', chapter_text, re.IGNORECASE | re.MULTILINE)
        if sec1_match:
            return chapter_text[sec1_match.start():]
        return chapter_text
        
    part_matches = list(re.finditer(r'^\s*PART\s+I\b', text, re.IGNORECASE | re.MULTILINE))
    if len(part_matches) >= 2:
        part_text = text[part_matches[1].start():]
        sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', part_text, re.IGNORECASE | re.MULTILINE)
        if sec1_match:
            return part_text[sec1_match.start():]
        return part_text
        
    toc_match = re.search(r'ARRANGEMENT\s+OF\s+SECTIONS|CONTENTS', text, re.IGNORECASE)
    if toc_match:
        post_toc_text = text[toc_match.end():]
        sec1_match = re.search(r'^\s*(?:Section|Article)?\s*1\.\s*[—\-–]?\s*', post_toc_text, re.IGNORECASE | re.MULTILINE)
        if sec1_match:
            return post_toc_text[sec1_match.start():]

    return text


def extract_parent_sections(text: str, law: str, law_full_name: str, filename: str) -> List[SectionData]:
    """Parses hierarchy and extracts unique parent sections."""
    sections: List[SectionData] = []
    seen_parent_ids: Set[str] = set()
    
    current_part: Optional[str] = None
    current_chapter: Optional[str] = None
    current_chapter_title: Optional[str] = None
    current_sec_num: Optional[str] = None
    current_sec_title: Optional[str] = None
    current_sec_text: List[str] = []
    
    lines = text.split('\n')
    
    part_re = re.compile(r'^PART\s+([A-Z0-9IVXLCDM]+)(?:\s+(.*))?$', re.IGNORECASE)
    chapter_re = re.compile(r'^CHAPTER\s+([A-Z0-9IVXLCDM]+)(?:\s+(.*))?$', re.IGNORECASE)
    section_re = re.compile(r'^(?:Section|Article)?\s*(\d+[A-Z]{0,3})\.\s*[—\-–]?\s*(.*)$', re.IGNORECASE)
    structural_re = re.compile(r'^(?:PART\s+[A-Z0-9IVXLCDM]+|CHAPTER\s+[A-Z0-9IVXLCDM]+|(?:Section|Article)?\s*\d+[A-Z]{0,3}\.)', re.IGNORECASE)
    noise_re = re.compile(r'^(Amendment|Notification|Gazette|Commencement|Published)', re.IGNORECASE)
    stop_re = re.compile(r'^(THE\s+)?(FIRST|SECOND|THIRD|FOURTH|FIFTH|SIXTH|SEVENTH|EIGHTH|NINTH|TENTH)?\s*SCHEDULE\s*$', re.IGNORECASE)
    page_re = re.compile(r'^\d+$')
    
    expecting_chapter_title = False
    expecting_part_title = False
    expecting_sec_title = False
    
    def save_current_section() -> None:
        if current_sec_num:
            sec_text_joined = "\n".join(current_sec_text).strip()
            sec_text_cleaned = re.sub(r'[ \t]+', ' ', sec_text_joined)
            sec_text_cleaned = (
                sec_text_cleaned
                .replace("â€”", "—")
                .replace("â€“", "–")
                .replace("â€˜", "'")
                .replace("â€™", "'")
            )
            
            clean_num = re.sub(r'[\s\-]+', '', current_sec_num).upper()
            
            if law == "Constitution":
                parent_id = f"{law}_Article{clean_num}"
                sec_label = f"Article {clean_num}"
            else:
                parent_id = f"{law}_{clean_num}"
                sec_label = f"Section {clean_num}"
                
            if parent_id not in seen_parent_ids:
                sections.append(SectionData(
                    parent_id=parent_id,
                    law=law,
                    law_full_name=law_full_name,
                    part=current_part,
                    chapter=current_chapter,
                    chapter_title=current_chapter_title,
                    section=sec_label,
                    title=current_sec_title or "",
                    text=sec_text_cleaned,
                    source_file=filename
                ))
                seen_parent_ids.add(parent_id)
            
    for line in lines:
        clean_line = line.strip()
        if not clean_line or noise_re.match(clean_line):
            continue
            
        if stop_re.match(clean_line):
            save_current_section()
            break
            
        if page_re.match(clean_line):
            continue
            
        if expecting_part_title:
            expecting_part_title = False
            if not structural_re.match(clean_line):
                continue
                
        if expecting_chapter_title:
            expecting_chapter_title = False
            if not structural_re.match(clean_line):
                current_chapter_title = clean_line
                continue
                
        if expecting_sec_title and current_sec_num:
            if not structural_re.match(clean_line):
                current_sec_title = re.sub(r'^[—\-–]\s*', '', clean_line).strip()
                expecting_sec_title = False
            else:
                expecting_sec_title = False
                
        part_match = part_re.match(clean_line)
        if part_match:
            current_part = f"Part {part_match.group(1).upper()}"
            if not part_match.group(2):
                expecting_part_title = True
            continue
            
        chapter_match = chapter_re.match(clean_line)
        if chapter_match:
            current_chapter = f"Chapter {chapter_match.group(1).upper()}"
            inline_title = chapter_match.group(2)
            if inline_title:
                current_chapter_title = inline_title.strip()
            else:
                current_chapter_title = None
                expecting_chapter_title = True
            continue
            
        sec_match = section_re.match(clean_line)
        if sec_match:
            save_current_section()
            current_sec_num = sec_match.group(1).upper()
            title_text = sec_match.group(2).strip()
            current_sec_title = re.sub(r'^[—\-–]\s*', '', title_text).strip()
            
            if not current_sec_title:
                expecting_sec_title = True
                
            current_sec_text = [clean_line]
            continue
            
        if current_sec_num:
            current_sec_text.append(clean_line)
            
    save_current_section()
    return sections


def extract_metadata(sec_data: SectionData) -> Dict[str, Optional[str]]:
    """Helper to parse numbers from structural strings."""
    def extract(pattern: str, text: Optional[str]) -> Optional[str]:
        if not text: return None
        m = re.search(pattern, text)
        return m.group(0) if m else None

    return {
        "part_no": extract(r'\d+|[IVXLCDM]+', sec_data.part),
        "chapter_no": extract(r'\d+|[IVXLCDM]+', sec_data.chapter),
        "section_no": extract(r'\d+[A-Z]*', sec_data.section)
    }


def determine_chunk_type(text: str) -> str:
    """Determine semantic type based on text content."""
    text_upper = text.strip().upper()
    if text_upper.startswith("EXPLANATION"): return "explanation"
    if text_upper.startswith("ILLUSTRATION"): return "illustration"
    if text_upper.startswith("EXCEPTION"): return "exception"
    if text_upper.startswith("PROVIDED THAT") or text_upper.startswith("PROVIDED FURTHER"): return "proviso"
    return "main_section"


def build_hierarchy_path(sec: SectionData) -> str:
    """Builds a string representation of the section's hierarchy."""
    path = []
    if sec.part: path.append(sec.part)
    if sec.chapter: path.append(sec.chapter)
    path.append(sec.section)
    return " > ".join(path)


def semantic_token_chunker(text: str) -> List[Tuple[str, List[int]]]:
    """
    Tiered chunking: Legal Boundaries -> Sentences -> Token Fallback.
    Merges tiny chunks (<150 tokens) with preceding ones if space allows.
    """
    # 1. Split on structural markers or blank lines
    blocks = re.split(r'\n\s*\n|(?=\n\s*(?:Explanation|Illustration|Exception|Provided\s+that|Provided\s+further)\b)', text)
    
    raw_chunks: List[Tuple[str, List[int]]] = []
    
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        block_tokens = enc.encode(block)
        
        if len(block_tokens) <= CHUNK_SIZE:
            raw_chunks.append((block, block_tokens))
        else:
            # Fallback to sentences (respecting legal lists like (a), (i), 1.)
            sentences = re.split(r'(?<=[.!?])\s+(?![a-z]\)|[ivx]+\)|\d+\.)', block)
            for sent in sentences:
                sent = sent.strip()
                if not sent:
                    continue
                
                sent_tokens = enc.encode(sent)
                if len(sent_tokens) <= CHUNK_SIZE:
                    raw_chunks.append((sent, sent_tokens))
                else:
                    # Final fallback: Recursive token split
                    for i in range(0, len(sent_tokens), CHUNK_SIZE):
                        sub_tokens = sent_tokens[i : i + CHUNK_SIZE]
                        raw_chunks.append((enc.decode(sub_tokens), sub_tokens))
                        
    # 2. Greedy accumulation with token overlap
    accumulated_chunks: List[Tuple[str, List[int]]] = []
    current_text = ""
    current_toks: List[int] = []
    
    for txt, toks in raw_chunks:
        if len(current_toks) + len(toks) <= CHUNK_SIZE:
            current_text = f"{current_text}\n\n{txt}" if current_text else txt
            current_toks.extend(toks)
        else:
            if current_toks:
                accumulated_chunks.append((current_text.strip(), current_toks))
                
            overlap_toks = current_toks[-CHUNK_OVERLAP:] if current_toks else []
            current_text = enc.decode(overlap_toks) + f"\n\n{txt}" if overlap_toks else txt
            current_toks = overlap_toks + toks
            
    if current_toks:
        accumulated_chunks.append((current_text.strip(), current_toks))
        
    # 3. Merge tiny chunks (< 150 tokens)
    merged_chunks: List[Tuple[str, List[int]]] = []
    for txt, toks in accumulated_chunks:
        if not merged_chunks:
            merged_chunks.append((txt, toks))
        else:
            prev_txt, prev_toks = merged_chunks[-1]
            if len(toks) < 150 and (len(prev_toks) + len(toks) <= CHUNK_SIZE):
                merged_chunks[-1] = (f"{prev_txt}\n\n{txt}", prev_toks + toks)
            else:
                merged_chunks.append((txt, toks))
                
    return merged_chunks


def create_chunks(sections: List[SectionData]) -> List[ChunkData]:
    """Transforms Parent Sections into specialized semantic chunk objects."""
    chunks: List[ChunkData] = []
    
    for sec in sections:
        # Validate metadata
        if not sec.section or not sec.parent_id or not sec.law:
            continue
            
        meta = extract_metadata(sec)
        hierarchy = build_hierarchy_path(sec)
        
        tokenized_blocks = semantic_token_chunker(sec.text)
        total = len(tokenized_blocks)
        
        current_token_idx = 0
        
        for i, (txt, toks) in enumerate(tokenized_blocks, 1):
            tok_count = len(toks)
            c_id = f"{sec.parent_id}_{i}"
            
            chunks.append(ChunkData(
                chunk_id=c_id,
                parent_id=sec.parent_id,
                law=sec.law,
                law_full_name=sec.law_full_name,
                part=sec.part,
                part_no=meta['part_no'],
                chapter=sec.chapter,
                chapter_no=meta['chapter_no'],
                chapter_title=sec.chapter_title,
                section=sec.section,
                section_no=meta['section_no'],
                title=sec.title,
                chunk_no=i,
                total_chunks=total,
                text=txt,
                token_count=tok_count,
                token_start=current_token_idx,
                token_end=current_token_idx + tok_count,
                previous_chunk_id=f"{sec.parent_id}_{i-1}" if i > 1 else None,
                next_chunk_id=f"{sec.parent_id}_{i+1}" if i < total else None,
                source_file=sec.source_file,
                chunk_type=determine_chunk_type(txt),
                hierarchy_path=hierarchy
            ))
            
            # Increment index but account for overlap in the global section scale
            if i < total:
                current_token_idx += (tok_count - CHUNK_OVERLAP)
            else:
                current_token_idx += tok_count
                
    return chunks


def process_file(file_path: Path) -> List[ChunkData]:
    """Reads file, extracts parent sections, and executes token-aware chunking."""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            text = f.read()
    except Exception as e:
        logger.error(f"Failed to read {file_path}: {e}")
        return []

    law, law_full_name = detect_law(file_path.name)
    body_text = remove_table_of_contents(text)
    sections = extract_parent_sections(body_text, law, law_full_name, file_path.name)
    return create_chunks(sections)


def run() -> None:
    """Execution pipeline handling incremental JSON generation."""
    input_dir = Path(PERMANENT_CLEANED)
    output_dir = Path(PERMANENT_CHUNKS)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if not input_dir.exists():
        logger.error(f"Input directory does not exist: {input_dir}")
        return

    for file_path in input_dir.glob("*.txt"):
        logger.info(f"Reading: {file_path.name}")
        chunks = process_file(file_path)
        
        if not chunks:
            logger.warning(f"No chunks generated for {file_path.name}")
            continue
            
        law = chunks[0].law
        output_file = output_dir / f"{law}_chunks.json"
        
        # Analytics Tracking
        total_sections = len(set(c.parent_id for c in chunks))
        total_chunks = len(chunks)
        token_counts = [c.token_count for c in chunks]
        
        avg_tokens = sum(token_counts) // total_chunks if total_chunks else 0
        largest_chunk = max(token_counts) if token_counts else 0
        smallest_chunk = min(token_counts) if token_counts else 0

        logger.info(f"--- {law} Summary ---")
        logger.info(f"Sections      : {total_sections}")
        logger.info(f"Chunks        : {total_chunks}")
        logger.info(f"Avg Tokens    : {avg_tokens}")
        logger.info(f"Largest Chunk : {largest_chunk} tokens")
        logger.info(f"Smallest Chunk: {smallest_chunk} tokens")
        
        try:
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump([asdict(c) for c in chunks], f, indent=4, ensure_ascii=False)
            logger.info(f"Successfully saved {law} to {output_file.name}")
        except Exception as e:
            logger.error(f"Failed to save {law} chunks: {e}")


if __name__ == "__main__":
    run()
import re
from typing import List, Dict


def read_text_file(file_path: str) -> str:
    """قراءة المستند مع تجربة الترميزات الأكثر شيوعاً للنصوص العربية."""
    encodings = ["utf-8", "utf-8-sig", "windows-1256", "cp1256", "iso-8859-6", "latin1"]
    for enc in encodings:
        try:
            with open(file_path, "r", encoding=enc) as f:
                content = f.read()
                if content and len(content.strip()) > 10:
                    return content
        except (UnicodeDecodeError, FileNotFoundError):
            continue
            
    with open(file_path, "rb") as f:
        raw = f.read()
        return raw.decode("utf-8", errors="ignore")


def parse_articles(raw_text: str) -> List[Dict[str, str]]:
    """
    استخراج المواد بشكل منظم (مادة مادة).
    """
    lines = [l.strip() for l in raw_text.splitlines() if l.strip()]
    articles = []
    
    article_pattern = re.compile(r'^(المادة|مادة)\s*(\(?\d+\)?|[^\:\-]+)[\:\-]?\s*(.*)', re.IGNORECASE)
    current_art = None
    
    for line in lines:
        match = article_pattern.match(line)
        if match:
            if current_art:
                articles.append(current_art)
            art_num = match.group(2).strip("():- ")
            art_title = match.group(3).strip()
            current_art = {
                "title": f"المادة {art_num}" + (f": {art_title}" if art_title else ""),
                "article_id": f"art_{art_num}",
                "content": line
            }
        else:
            if current_art:
                current_art["content"] += "\n" + line
            else:
                current_art = {
                    "title": "مقدمة / عام",
                    "article_id": "art_intro",
                    "content": line
                }
                
    if current_art:
        articles.append(current_art)
        
    if len(articles) <= 1 and len(lines) > 3:
        articles = []
        for idx, para in enumerate(raw_text.split("\n\n"), 1):
            para = para.strip()
            if para:
                articles.append({
                    "title": f"المادة/الفقرة {idx}",
                    "article_id": f"art_{idx}",
                    "content": para
                })
                
    return articles

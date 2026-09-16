import re
import math
import requests
from typing import List, Dict
from collections import Counter
from app.config import settings


class Embedder:
    """
    محرك التضمين الدلالي (Semantic Vectorizer):
    - يدعم استدعاء نماذج OpenAI مثل (openai/text-embedding-3-large بدقة 3072 بعد) عبر OpenRouter API.
    - يحتوي على كاش داخلي لتفادي استهلاك الرصيد عند تكرار النصوص.
    - يدعم التراجع الآمن للمحرك المدمج الداخلي في حال انقطاع الاتصال أو عدم توفر المفتاح.
    """
    def __init__(self, model_name: str = None):
        self._explicit_model_name = model_name
        self.embeddings_url = "https://openrouter.ai/api/v1/embeddings"
        self._cache: Dict[str, List[float]] = {}
        self.vocabulary: Dict[str, int] = {}
        self.idf: Dict[str, float] = {}
        self.last_dimension: int = 3072
        self.using_api: bool = False

    @property
    def model_name(self) -> str:
        return self._explicit_model_name or settings.active_embedding_model

    @property
    def api_key(self) -> str:
        return settings.active_api_key

    def _is_api_supported(self) -> bool:
        return bool(self.api_key and len(self.api_key) > 10 and ("openai/" in self.model_name or "embedding" in self.model_name))

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r'[^\w\s]', ' ', text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 1]
        
        char_ngrams = []
        for t in tokens:
            if len(t) >= 3:
                for i in range(len(t) - 2):
                    char_ngrams.append(f"#{t[i:i+3]}")
        return tokens + char_ngrams

    def fit_vocabulary(self, corpus: List[str]):
        doc_count = len(corpus)
        df = Counter()
        for doc in corpus:
            unique_tokens = set(self._tokenize(doc))
            for tok in unique_tokens:
                df[tok] += 1
                
        sorted_vocab = [tok for tok, count in df.most_common(1500)]
        self.vocabulary = {tok: idx for idx, tok in enumerate(sorted_vocab)}
        
        for tok, count in df.items():
            if tok in self.vocabulary:
                self.idf[tok] = math.log((1.0 + doc_count) / (1.0 + count)) + 1.0

    def _embed_local(self, text: str) -> List[float]:
        tokens = self._tokenize(text)
        vec = [0.0] * max(1, len(self.vocabulary))
        if not tokens or not self.vocabulary:
            return vec
            
        tf = Counter(tokens)
        for tok, count in tf.items():
            if tok in self.vocabulary:
                idx = self.vocabulary[tok]
                vec[idx] = count * self.idf.get(tok, 1.0)
                
        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
        self.last_dimension = len(vec)
        return vec

    def _call_api_embeddings(self, texts: List[str]) -> List[List[float]]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_site_name,
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model_name,
            "input": texts
        }
        resp = requests.post(self.embeddings_url, headers=headers, json=payload, timeout=20)
        resp.raise_for_status()
        data = resp.json()
        embeddings = [item["embedding"] for item in data["data"]]
        if embeddings and len(embeddings[0]) > 0:
            self.last_dimension = len(embeddings[0])
            self.using_api = True
        return embeddings

    def embed(self, text: str) -> List[float]:
        clean_text = text.strip()
        if clean_text in self._cache:
            return self._cache[clean_text]

        if self._is_api_supported():
            try:
                vectors = self._call_api_embeddings([clean_text])
                if vectors:
                    self._cache[clean_text] = vectors[0]
                    return vectors[0]
            except Exception as e:
                print(f"[Embedder] تعذر الاتصال بـ API التضمين ({self.model_name}): {e} - الرجوع للمحرك الداخلي.")
                self.using_api = False

        # الرجوع للمحرك المدمج
        vec = self._embed_local(clean_text)
        self._cache[clean_text] = vec
        return vec

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        clean_texts = [t.strip() for t in texts]
        
        # تجهيز المفردات للمحرك الداخلي كخيار احتياطي
        if not self.vocabulary:
            self.fit_vocabulary(clean_texts)

        if self._is_api_supported():
            uncached = [t for t in clean_texts if t not in self._cache]
            if uncached:
                try:
                    # إرسال على دفعات بحجم 16 نص كحد أقصى لكل طلب
                    batch_size = 16
                    for i in range(0, len(uncached), batch_size):
                        chunk = uncached[i:i + batch_size]
                        vecs = self._call_api_embeddings(chunk)
                        for text, vec in zip(chunk, vecs):
                            self._cache[text] = vec
                except Exception as e:
                    print(f"[Embedder Batch] تعذر طلب API: {e} - استخدام المحرك الداخلي.")
                    self.using_api = False

        return [self.embed(t) for t in clean_texts]

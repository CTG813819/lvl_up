import os
import json

TRUSTED_SOURCES_FILE = os.path.join(os.path.dirname(__file__), 'trusted_sources.json')

DEFAULT_TRUSTED_SOURCES = [
    "https://stackoverflow.com",
    "https://ai.stackexchange.com",
    "https://datascience.stackexchange.com",
    "https://www.reddit.com/r/MachineLearning",
    "https://www.reddit.com/r/artificial",
    "https://github.com",
    "https://huggingface.co/models",
    "https://paperswithcode.com",
    "https://arxiv.org",
    "https://www.semanticscholar.org",
    "https://medium.com",
    "https://dev.to",
    "https://ai.googleblog.com",
    "https://openai.com/blog",
    "https://docs.python.org",
    "https://pytorch.org",
    "https://www.tensorflow.org",
    "https://scikit-learn.org",
    "https://fastapi.tiangolo.com"
]

_trusted_sources = []

def load_trusted_sources():
    global _trusted_sources
    if os.path.exists(TRUSTED_SOURCES_FILE):
        with open(TRUSTED_SOURCES_FILE, 'r') as f:
            _trusted_sources = json.load(f)
    else:
        _trusted_sources = DEFAULT_TRUSTED_SOURCES.copy()

def save_trusted_sources():
    with open(TRUSTED_SOURCES_FILE, 'w') as f:
        json.dump(_trusted_sources, f, indent=2)

def get_trusted_sources():
    return list(_trusted_sources)

def add_trusted_source(url: str) -> bool:
    if url not in _trusted_sources:
        _trusted_sources.append(url)
        save_trusted_sources()
        return True
    return False

def remove_trusted_source(url: str) -> bool:
    if url in _trusted_sources:
        _trusted_sources.remove(url)
        save_trusted_sources()
        return True
    return False

def is_trusted_source(url: str) -> bool:
    for source in _trusted_sources:
        if url.startswith(source):
            return True
    return False

# Load trusted sources on import
load_trusted_sources()

import os
import json
import re
from typing import List, Dict, Optional, Set, Any
from urllib.parse import urlparse, urljoin
import aiohttp
import asyncio
from datetime import datetime, timedelta
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.cluster import KMeans
import structlog

logger = structlog.get_logger()

TRUSTED_SOURCES_FILE = os.path.join(os.path.dirname(__file__), 'trusted_sources.json')
LEARNING_SOURCES_FILE = os.path.join(os.path.dirname(__file__), 'learning_sources.json')
SOURCE_ANALYTICS_FILE = os.path.join(os.path.dirname(__file__), 'source_analytics.json')

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

# AI-specific source discovery patterns with ML enhancement
AI_SOURCE_PATTERNS = {
    "imperium": [
        r"https?://[^/]*\.ai\b",
        r"https?://[^/]*machine-learning[^/]*",
        r"https?://[^/]*artificial-intelligence[^/]*",
        r"https?://[^/]*ai-governance[^/]*",
        r"https?://[^/]*meta-learning[^/]*",
        r"https?://[^/]*autonomous[^/]*",
        r"https?://[^/]*orchestration[^/]*",
        r"https?://[^/]*ai-ethics[^/]*",
        r"https?://[^/]*ai-safety[^/]*"
    ],
    "guardian": [
        r"https?://[^/]*security[^/]*",
        r"https?://[^/]*vulnerability[^/]*",
        r"https?://[^/]*secure-coding[^/]*",
        r"https?://[^/]*code-quality[^/]*",
        r"https?://[^/]*static-analysis[^/]*",
        r"https?://[^/]*penetration-testing[^/]*",
        r"https?://[^/]*cybersecurity[^/]*",
        r"https?://[^/]*threat-detection[^/]*"
    ],
    "sandbox": [
        r"https?://[^/]*experiment[^/]*",
        r"https?://[^/]*prototype[^/]*",
        r"https?://[^/]*innovation[^/]*",
        r"https?://[^/]*research[^/]*",
        r"https?://[^/]*novel[^/]*",
        r"https?://[^/]*experimental[^/]*",
        r"https?://[^/]*cutting-edge[^/]*",
        r"https?://[^/]*breakthrough[^/]*"
    ],
    "conquest": [
        r"https?://[^/]*app-development[^/]*",
        r"https?://[^/]*mobile[^/]*",
        r"https?://[^/]*flutter[^/]*",
        r"https?://[^/]*react-native[^/]*",
        r"https?://[^/]*ux-design[^/]*",
        r"https?://[^/]*user-experience[^/]*",
        r"https?://[^/]*app-store[^/]*",
        r"https?://[^/]*mobile-optimization[^/]*"
    ]
}

# ML-enhanced source quality keywords
SOURCE_QUALITY_KEYWORDS = {
    "imperium": ["ai", "machine learning", "artificial intelligence", "autonomous", "orchestration", "governance", "meta-learning"],
    "guardian": ["security", "vulnerability", "secure coding", "code quality", "static analysis", "penetration testing", "cybersecurity"],
    "sandbox": ["experiment", "prototype", "innovation", "research", "novel", "experimental", "cutting-edge"],
    "conquest": ["app development", "mobile", "flutter", "react native", "ux design", "user experience", "app store"]
}

_trusted_sources = []
_learning_sources = {}  # AI-specific discovered sources
_source_metrics = {}  # Track source performance
_source_analytics = {}  # ML-enhanced analytics
_source_clusters = {}  # Clustered sources for better discovery

def load_trusted_sources():
    global _trusted_sources, _learning_sources, _source_metrics, _source_analytics, _source_clusters
    if os.path.exists(TRUSTED_SOURCES_FILE):
        with open(TRUSTED_SOURCES_FILE, 'r') as f:
            _trusted_sources = json.load(f)
    else:
        _trusted_sources = DEFAULT_TRUSTED_SOURCES.copy()
    
    # Load AI-specific learning sources
    if os.path.exists(LEARNING_SOURCES_FILE):
        with open(LEARNING_SOURCES_FILE, 'r') as f:
            data = json.load(f)
            _learning_sources = data.get('learning_sources', {})
            _source_metrics = data.get('source_metrics', {})
    else:
        _learning_sources = {}
        _source_metrics = {}
    
    # Load source analytics
    if os.path.exists(SOURCE_ANALYTICS_FILE):
        with open(SOURCE_ANALYTICS_FILE, 'r') as f:
            _source_analytics = json.load(f)
    else:
        _source_analytics = {
            'source_clusters': {},
            'quality_scores': {},
            'discovery_patterns': {},
            'growth_metrics': {},
            'last_updated': datetime.now().isoformat()
        }

def save_trusted_sources():
    with open(TRUSTED_SOURCES_FILE, 'w') as f:
        json.dump(_trusted_sources, f, indent=2)

def save_learning_sources():
    with open(LEARNING_SOURCES_FILE, 'w') as f:
        json.dump({
            'learning_sources': _learning_sources,
            'source_metrics': _source_metrics,
            'last_updated': datetime.now().isoformat()
        }, f, indent=2)

def save_source_analytics():
    _source_analytics['last_updated'] = datetime.now().isoformat()
    with open(SOURCE_ANALYTICS_FILE, 'w') as f:
        json.dump(_source_analytics, f, indent=2)

def get_trusted_sources():
    return list(_trusted_sources)

def get_learning_sources(ai_type: Optional[str] = None) -> Dict[str, List[str]]:
    """Get AI-specific learning sources with ML-enhanced discovery"""
    if ai_type:
        sources = _learning_sources.get(ai_type, [])
        # Add ML-recommended sources
        ml_recommendations = _get_ml_recommended_sources(ai_type)
        sources.extend(ml_recommendations)
        return {ai_type: list(set(sources))}  # Remove duplicates
    return _learning_sources.copy()

def add_trusted_source(url: str) -> bool:
    if url not in _trusted_sources:
        _trusted_sources.append(url)
        save_trusted_sources()
        _update_source_analytics('trusted_sources_added', url)
        return True
    return False

def remove_trusted_source(url: str) -> bool:
    if url in _trusted_sources:
        _trusted_sources.remove(url)
        save_trusted_sources()
        _update_source_analytics('trusted_sources_removed', url)
        return True
    return False

def is_trusted_source(url: str) -> bool:
    for source in _trusted_sources:
        if url.startswith(source):
            return True
    return False

async def discover_new_sources_from_learning_result(ai_type: str, learning_result: Dict) -> List[str]:
    """Discover new sources from learning results with ML enhancement"""
    discovered_sources = []
    
    try:
        # Extract URLs from learning result content
        content = f"{learning_result.get('title', '')} {learning_result.get('summary', '')} {learning_result.get('content', '')}"
        
        # Find URLs in content
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        urls = re.findall(url_pattern, content)
        
        for url in urls:
            # Clean URL
            url = url.split(')')[0].split(']')[0].split('"')[0].split("'")[0]
            
            # Check if it's a new source for this AI type with ML enhancement
            if await _is_relevant_source_for_ai_ml(ai_type, url, content):
                discovered_sources.append(url)
        
        # Add discovered sources to AI-specific learning sources
        if discovered_sources:
            if ai_type not in _learning_sources:
                _learning_sources[ai_type] = []
            
            for source in discovered_sources:
                if source not in _learning_sources[ai_type]:
                    _learning_sources[ai_type].append(source)
                    _update_source_metrics(ai_type, source, learning_result)
                    _update_source_analytics('source_discovered', source, ai_type)
            
            save_learning_sources()
            _update_growth_metrics(ai_type, len(discovered_sources))
        
        return discovered_sources
        
    except Exception as e:
        logger.error(f"Error discovering sources for {ai_type}: {e}")
        return []

async def _is_relevant_source_for_ai_ml(ai_type: str, url: str, content: str = "") -> bool:
    """Check if a URL is relevant for a specific AI type using ML enhancement"""
    try:
        # Check against AI-specific patterns
        patterns = AI_SOURCE_PATTERNS.get(ai_type, [])
        for pattern in patterns:
            if re.search(pattern, url, re.IGNORECASE):
                return True
        
        # ML-enhanced content analysis
        if content:
            relevance_score = _calculate_content_relevance(ai_type, content)
            if relevance_score > 0.6:  # Threshold for relevance
                return True
        
        # Check domain quality with ML scoring
        domain_quality = _calculate_domain_quality(url)
        if domain_quality > 0.7:  # High quality domain
            return True
        
        # Check against AI-specific quality keywords
        keywords = SOURCE_QUALITY_KEYWORDS.get(ai_type, [])
        url_lower = url.lower()
        content_lower = content.lower()
        
        keyword_matches = sum(1 for keyword in keywords if keyword in url_lower or keyword in content_lower)
        if keyword_matches >= 2:  # At least 2 keyword matches
            return True
        
        return False
        
    except Exception as e:
        logger.error(f"Error in ML source relevance check: {e}")
        return False

def _calculate_content_relevance(ai_type: str, content: str) -> float:
    """Calculate content relevance using TF-IDF and cosine similarity"""
    try:
        # Get reference content for AI type
        reference_content = _get_reference_content(ai_type)
        
        if not reference_content:
            return 0.5  # Default relevance
        
        # Create TF-IDF vectors
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        
        # Combine reference content with new content
        all_content = reference_content + [content]
        tfidf_matrix = vectorizer.fit_transform(all_content)
        
        # Calculate similarity between new content and reference
        new_content_vector = tfidf_matrix[-1:].toarray()
        reference_vectors = tfidf_matrix[:-1].toarray()
        
        # Calculate average similarity
        similarities = cosine_similarity(new_content_vector, reference_vectors)[0]
        avg_similarity = np.mean(similarities)
        
        return float(avg_similarity)
        
    except Exception as e:
        logger.error(f"Error calculating content relevance: {e}")
        return 0.5

def _calculate_domain_quality(url: str) -> float:
    """Calculate domain quality score using ML"""
    try:
        domain = urlparse(url).netloc
        
        # Quality domain patterns
        high_quality_domains = [
            'github.com', 'stackoverflow.com', 'medium.com', 'dev.to',
            'arxiv.org', 'paperswithcode.com', 'huggingface.co',
            'ai.googleblog.com', 'openai.com', 'pytorch.org',
            'tensorflow.org', 'scikit-learn.org', 'fastapi.tiangolo.com'
        ]
        
        # Check against high-quality domains
        for quality_domain in high_quality_domains:
            if quality_domain in domain:
                return 0.9
        
        # Check for educational/research domains
        edu_research_domains = ['.edu', '.ac.', 'research.', 'lab.']
        for edu_domain in edu_research_domains:
            if edu_domain in domain:
                return 0.8
        
        # Check for professional domains
        professional_domains = ['.org', '.com', '.io', '.ai']
        for prof_domain in professional_domains:
            if prof_domain in domain:
                return 0.6
        
        return 0.3  # Default quality score
        
    except Exception:
        return 0.3

def _get_reference_content(ai_type: str) -> List[str]:
    """Get reference content for AI type"""
    reference_content = {
        "imperium": [
            "artificial intelligence machine learning autonomous systems",
            "AI governance meta-learning orchestration autonomous agents",
            "machine learning artificial intelligence autonomous systems"
        ],
        "guardian": [
            "security vulnerability secure coding code quality",
            "cybersecurity threat detection static analysis",
            "penetration testing secure development practices"
        ],
        "sandbox": [
            "experiment prototype innovation research novel",
            "experimental cutting-edge breakthrough research",
            "innovation prototype experimental novel approaches"
        ],
        "conquest": [
            "app development mobile flutter react native",
            "user experience UX design mobile optimization",
            "app store mobile development user interface"
        ]
    }
    
    return reference_content.get(ai_type, ["general technology development"])

def _get_ml_recommended_sources(ai_type: str) -> List[str]:
    """Get ML-recommended sources based on clustering and similarity"""
    try:
        if ai_type not in _source_analytics.get('source_clusters', {}):
            return []
        
        # Get cluster recommendations
        cluster_recommendations = _source_analytics['source_clusters'].get(ai_type, [])
        
        # Get similarity-based recommendations
        similarity_recommendations = _get_similarity_recommendations(ai_type)
        
        return list(set(cluster_recommendations + similarity_recommendations))
        
    except Exception as e:
        logger.error(f"Error getting ML recommendations: {e}")
        return []

def _get_similarity_recommendations(ai_type: str) -> List[str]:
    """Get similarity-based source recommendations"""
    try:
        current_sources = _learning_sources.get(ai_type, [])
        if len(current_sources) < 2:
            return []
        
        # Create source embeddings
        vectorizer = TfidfVectorizer(stop_words='english', max_features=50)
        source_texts = [f"source_{i}" for i in range(len(current_sources))]
        
        # Calculate similarity matrix
        tfidf_matrix = vectorizer.fit_transform(source_texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find similar sources
        similar_sources = []
        for i, source in enumerate(current_sources):
            similarities = similarity_matrix[i]
            similar_indices = np.argsort(similarities)[-3:]  # Top 3 similar
            for idx in similar_indices:
                if idx != i:
                    similar_sources.append(current_sources[idx])
        
        return list(set(similar_sources))
        
    except Exception as e:
        logger.error(f"Error getting similarity recommendations: {e}")
        return []

def _update_source_metrics(ai_type: str, source: str, learning_result: Dict):
    """Update source performance metrics with ML enhancement"""
    if ai_type not in _source_metrics:
        _source_metrics[ai_type] = {}
    
    if source not in _source_metrics[ai_type]:
        _source_metrics[ai_type][source] = {
            'discovery_count': 0,
            'success_count': 0,
            'failure_count': 0,
            'quality_score': 0.0,
            'last_used': None,
            'learning_value': 0.0
        }
    
    metrics = _source_metrics[ai_type][source]
    metrics['discovery_count'] += 1
    metrics['last_used'] = datetime.now().isoformat()
    
    # Calculate learning value
    learning_value = _calculate_learning_value(learning_result)
    metrics['learning_value'] = (metrics['learning_value'] + learning_value) / 2
    
    # Update quality score based on learning value
    if learning_value > 0.7:
        metrics['success_count'] += 1
        metrics['quality_score'] = min(1.0, metrics['quality_score'] + 0.1)
    else:
        metrics['failure_count'] += 1
        metrics['quality_score'] = max(0.0, metrics['quality_score'] - 0.05)

def _calculate_learning_value(learning_result: Dict) -> float:
    """Calculate learning value using ML metrics"""
    try:
        # Extract learning indicators
        title = learning_result.get('title', '').lower()
        summary = learning_result.get('summary', '').lower()
        content = learning_result.get('content', '').lower()
        
        # Learning value indicators
        positive_indicators = [
            'learn', 'improve', 'enhance', 'optimize', 'solution', 'fix',
            'best practice', 'tutorial', 'guide', 'example', 'implementation'
        ]
        
        negative_indicators = [
            'error', 'fail', 'broken', 'issue', 'problem', 'bug'
        ]
        
        # Calculate positive score
        positive_score = 0
        for indicator in positive_indicators:
            if indicator in title or indicator in summary or indicator in content:
                positive_score += 1
        
        # Calculate negative score
        negative_score = 0
        for indicator in negative_indicators:
            if indicator in title or indicator in summary or indicator in content:
                negative_score += 1
        
        # Calculate final learning value
        total_indicators = positive_score + negative_score
        if total_indicators == 0:
            return 0.5  # Neutral value
        
        learning_value = positive_score / total_indicators
        return min(1.0, max(0.0, learning_value))
        
    except Exception:
        return 0.5

def _update_source_analytics(event_type: str, source: str, ai_type: str = None):
    """Update source analytics with ML tracking"""
    if 'events' not in _source_analytics:
        _source_analytics['events'] = []
    
    event = {
        'type': event_type,
        'source': source,
        'ai_type': ai_type,
        'timestamp': datetime.now().isoformat()
    }
    
    _source_analytics['events'].append(event)
    
    # Keep only recent events
    if len(_source_analytics['events']) > 1000:
        _source_analytics['events'] = _source_analytics['events'][-500:]
    
    save_source_analytics()

def _update_growth_metrics(ai_type: str, new_sources_count: int):
    """Update growth metrics for AI learning sources"""
    if 'growth_metrics' not in _source_analytics:
        _source_analytics['growth_metrics'] = {}
    
    if ai_type not in _source_analytics['growth_metrics']:
        _source_analytics['growth_metrics'][ai_type] = {
            'total_sources': 0,
            'new_sources_this_week': 0,
            'growth_rate': 0.0,
            'last_updated': datetime.now().isoformat()
        }
    
    metrics = _source_analytics['growth_metrics'][ai_type]
    metrics['total_sources'] = len(_learning_sources.get(ai_type, []))
    metrics['new_sources_this_week'] += new_sources_count
    
    # Calculate growth rate
    if metrics['total_sources'] > 0:
        metrics['growth_rate'] = new_sources_count / metrics['total_sources']
    
    metrics['last_updated'] = datetime.now().isoformat()
    
    save_source_analytics()

def get_source_performance(ai_type: Optional[str] = None) -> Dict[str, Dict]:
    """Get source performance metrics with ML enhancement"""
    if ai_type:
        return {ai_type: _source_metrics.get(ai_type, {})}
    return _source_metrics.copy()

def get_top_performing_sources(ai_type: str, limit: int = 5) -> List[str]:
    """Get top performing sources using ML ranking"""
    try:
        if ai_type not in _source_metrics:
            return []
        
        sources = _source_metrics[ai_type]
        
        # Calculate ML-based performance score
        scored_sources = []
        for source, metrics in sources.items():
            # ML performance score calculation
            quality_score = metrics.get('quality_score', 0.0)
            learning_value = metrics.get('learning_value', 0.0)
            success_rate = metrics.get('success_count', 0) / max(metrics.get('discovery_count', 1), 1)
            
            # Weighted performance score
            performance_score = (quality_score * 0.4 + learning_value * 0.4 + success_rate * 0.2)
            
            scored_sources.append((source, performance_score))
        
        # Sort by performance score
        scored_sources.sort(key=lambda x: x[1], reverse=True)
        
        return [source for source, score in scored_sources[:limit]]
        
    except Exception as e:
        logger.error(f"Error getting top performing sources: {e}")
        return []

async def expand_ai_learning_sources(ai_type: str, topic: str) -> List[str]:
    """Expand AI learning sources using ML-based discovery"""
    try:
        # Get current sources
        current_sources = _learning_sources.get(ai_type, [])
        
        # Use ML to find related sources
        related_sources = await _find_related_sources_ml(ai_type, topic, current_sources)
        
        # Add new sources
        new_sources = []
        for source in related_sources:
            if source not in current_sources:
                if ai_type not in _learning_sources:
                    _learning_sources[ai_type] = []
                _learning_sources[ai_type].append(source)
                new_sources.append(source)
        
        if new_sources:
            save_learning_sources()
            _update_growth_metrics(ai_type, len(new_sources))
        
        return new_sources
        
    except Exception as e:
        logger.error(f"Error expanding AI learning sources: {e}")
        return []

async def _find_related_sources_ml(ai_type: str, topic: str, current_sources: List[str]) -> List[str]:
    """Find related sources using ML similarity"""
    try:
        # Create topic embedding
        vectorizer = TfidfVectorizer(stop_words='english', max_features=100)
        
        # Combine topic with current sources for similarity analysis
        all_texts = [topic] + current_sources[:10]  # Use top 10 current sources
        
        # Create similarity matrix
        tfidf_matrix = vectorizer.fit_transform(all_texts)
        similarity_matrix = cosine_similarity(tfidf_matrix)
        
        # Find sources similar to the topic
        topic_similarities = similarity_matrix[0][1:]  # Topic similarity with sources
        
        # Get sources with high similarity
        similar_sources = []
        for i, similarity in enumerate(topic_similarities):
            if similarity > 0.3 and i < len(current_sources):  # Threshold for similarity
                similar_sources.append(current_sources[i])
        
        # Generate new source suggestions based on patterns
        new_suggestions = _generate_source_suggestions(ai_type, topic, similar_sources)
        
        return list(set(similar_sources + new_suggestions))
        
    except Exception as e:
        logger.error(f"Error finding related sources: {e}")
        return []

def _generate_source_suggestions(ai_type: str, topic: str, similar_sources: List[str]) -> List[str]:
    """Generate new source suggestions using ML patterns"""
    try:
        suggestions = []
        
        # Extract domain patterns from similar sources
        domains = set()
        for source in similar_sources:
            try:
                domain = urlparse(source).netloc
                domains.add(domain)
            except:
                continue
        
        # Generate suggestions based on patterns
        for domain in domains:
            # Create variations based on topic
            topic_keywords = topic.lower().split()
            for keyword in topic_keywords[:3]:  # Use top 3 keywords
                suggestion = f"https://{domain}/{keyword.replace(' ', '-')}"
                suggestions.append(suggestion)
        
        # Add AI-specific suggestions
        ai_patterns = AI_SOURCE_PATTERNS.get(ai_type, [])
        for pattern in ai_patterns[:3]:  # Use top 3 patterns
            # Extract domain from pattern
            domain_match = re.search(r'https?://([^/]+)', pattern)
            if domain_match:
                domain = domain_match.group(1)
                suggestion = f"https://{domain}/{topic.lower().replace(' ', '-')}"
                suggestions.append(suggestion)
        
        return suggestions[:10]  # Limit to 10 suggestions
        
    except Exception as e:
        logger.error(f"Error generating source suggestions: {e}")
        return []

def get_ai_learning_sources_summary() -> Dict[str, Dict]:
    """Get comprehensive AI learning sources summary with ML analytics"""
    summary = {}
    
    for ai_type in ['imperium', 'guardian', 'sandbox', 'conquest']:
        sources = _learning_sources.get(ai_type, [])
        metrics = _source_metrics.get(ai_type, {})
        growth_metrics = _source_analytics.get('growth_metrics', {}).get(ai_type, {})
        
        # Calculate ML-enhanced metrics
        total_sources = len(sources)
        top_performing = get_top_performing_sources(ai_type, 5)
        
        # Calculate growth rate
        growth_rate = growth_metrics.get('growth_rate', 0.0)
        new_sources_week = growth_metrics.get('new_sources_this_week', 0)
        
        # Calculate quality metrics
        quality_scores = [metrics.get(source, {}).get('quality_score', 0.0) for source in sources]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0.0
        
        summary[ai_type] = {
            'total_sources': total_sources,
            'top_performing_sources': top_performing,
            'recent_discoveries': new_sources_week,
            'growth_rate': round(growth_rate, 3),
            'average_quality_score': round(avg_quality, 3),
            'ml_enhanced': True
        }
    
    return summary

# Initialize on module load
load_trusted_sources()

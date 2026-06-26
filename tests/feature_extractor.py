"""
Shared feature extractor module.
This class must be in a stable module path for pickle to work correctly.
"""

import re
import math
from collections import Counter
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin

try:
    from textblob import TextBlob
    HAS_TEXTBLOB = True
except:
    HAS_TEXTBLOB = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    HAS_VADER = True
    vader = SentimentIntensityAnalyzer()
except:
    HAS_VADER = False

class StatisticalFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract statistical features from text - purely algorithmic."""
    
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        features_list = []
        for text in X:
            features = self._extract_features(text)
            features_list.append(features)
        return np.array(features_list)
    
    def _extract_features(self, text):
        features = []
        words = text.split()
        chars = len(text)
        
        # 1. Basic metrics
        features.append(len(words))
        features.append(chars)
        features.append(sum(len(w) for w in words) / max(len(words), 1))
        
        # 2. URL density
        url_pattern = re.compile(r'https?://\S+|www\.\S+|\S+\.(com|net|org|in|io|co|xyz|cc|tk|top|club|buzz)\b', re.I)
        url_count = len(url_pattern.findall(text))
        features.append(url_count)
        features.append(url_count / max(len(words), 1))
        
        # 3. Monetary density
        money_pattern = re.compile(r'rs\.?\s*[\d,]+|\$\s*\d+|\d+%')
        money_count = len(money_pattern.findall(text))
        features.append(money_count)
        features.append(money_count / max(len(words), 1))
        
        # 4. Number ratio
        number_pattern = re.compile(r'\b\d+\b')
        number_count = len(number_pattern.findall(text))
        features.append(number_count)
        features.append(number_count / max(len(words), 1))
        
        # 5. Uppercase ratio
        upper_chars = sum(1 for c in text if c.isupper())
        features.append(upper_chars / max(chars, 1))
        
        # 6. Punctuation
        punct_chars = sum(1 for c in text if c in '!?.')
        features.append(punct_chars / max(chars, 1))
        features.append(text.count('!'))
        features.append(text.count('?'))
        
        # 7. Phone presence
        phone_pattern = re.compile(r'\+?\d[\d\s-]{9,}')
        features.append(1 if phone_pattern.search(text) else 0)
        
        # 8. Imperative ratio
        imperative_seeds = {'update', 'verify', 'click', 'pay', 'claim', 'join', 'apply', 
                           'register', 'call', 'contact', 'renew', 'login', 'download',
                           'install', 'secure', 'fix', 'check', 'confirm', 'approve',
                           'withdraw', 'invest', 'earn', 'donate', 'help', 'subscribe',
                           'upgrade', 'unblock', 'unlock', 'reactivate', 'activate'}
        imperative_count = sum(1 for w in words if w.lower().rstrip('.,;:') in imperative_seeds)
        features.append(imperative_count / max(len(words), 1))
        
        # 9. Vocabulary diversity
        unique_words = len(set(w.lower() for w in words))
        features.append(unique_words / max(len(words), 1))
        
        # 10. Sentence metrics
        sentences = re.split(r'[.!?]+', text)
        sentences = [s for s in sentences if s.strip()]
        features.append(max(len(sentences), 1))
        features.append(len(words) / max(len(sentences), 1))
        
        # 11. Sentiment
        if HAS_TEXTBLOB:
            try:
                blob = TextBlob(text)
                features.append(blob.sentiment.polarity)
                features.append(blob.sentiment.subjectivity)
            except:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
        
        if HAS_VADER:
            try:
                scores = vader.polarity_scores(text)
                features.extend([scores['compound'], scores['pos'], scores['neg'], scores['neu']])
            except:
                features.extend([0, 0, 0, 0])
        else:
            features.extend([0, 0, 0, 0])
        
        # 12. Character entropy
        if chars > 0:
            char_counts = Counter(text)
            entropy = -sum((c/chars) * math.log2(c/chars) for c in char_counts.values())
            features.append(entropy)
        else:
            features.append(0)
        
        # 13. Special chars
        special_chars = sum(1 for c in text if not c.isalnum() and not c.isspace())
        features.append(special_chars / max(chars, 1))
        
        # 14. Placeholders
        features.append(1 if re.search(r'\[.*?\]', text) else 0)
        
        # 15. @ symbol
        features.append(1 if '@' in text else 0)
        
        return features
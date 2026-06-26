from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.responses import FileResponse
import os
import shutil
import pytesseract
import unicodedata
import math
import cv2
import numpy as np
from collections import Counter
from PIL import Image, ImageOps, ImageEnhance
import re
import urllib.parse
import requests
from bs4 import BeautifulSoup
import base64
from io import BytesIO
from sklearn.cluster import KMeans
from sklearn.base import BaseEstimator, TransformerMixin
import json
import pickle
import platform

app = FastAPI(title="SatyaSetu API")

# =====================================================================
# CROSS-PLATFORM TESSERACT PATH (Windows + Linux)
# =====================================================================
if platform.system() == 'Windows':
    pytesseract.pytesseract.tesseract_cmd = r'E:\SatyaSetu\tesseract.exe'
else:
    pytesseract.pytesseract.tesseract_cmd = '/usr/bin/tesseract'

UPLOAD_DIR = "uploaded_images"
os.makedirs(UPLOAD_DIR, exist_ok=True)

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../frontend'))

# =====================================================================
# ADD TESTS DIRECTORY TO PYTHON PATH (MUST be before model loading)
# =====================================================================
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests')))

# Import the feature extractor class from shared module
from feature_extractor import StatisticalFeatureExtractor

# =====================================================================
# PRIMARY STATISTICAL ML MODEL LOADING
# =====================================================================
STAT_MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../tests/model/primary_statistical_model.pkl'))
STAT_MODEL = None

try:
    with open(STAT_MODEL_PATH, 'rb') as f:
        STAT_MODEL = pickle.load(f)
    print(f"✓ Primary Statistical Model loaded from: {STAT_MODEL_PATH}")
except Exception as e:
    print(f"⚠ Primary Statistical Model not found. Run: python tests/train_statistical_model.py")
    print(f"  Error: {e}")

@app.get("/")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, 'index.html'))

# =====================================================================
# DAY 12: USER BLUR REGION DETECTION
# =====================================================================
def get_word_bounding_boxes(pil_image):
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    data = pytesseract.image_to_data(pil_image, output_type=pytesseract.Output.DICT)
    words = []
    n_boxes = len(data['text'])
    for i in range(n_boxes):
        text = data['text'][i].strip()
        conf = int(data['conf'][i])
        if text and conf > 30:
            words.append({
                'text': text,
                'x': data['left'][i],
                'y': data['top'][i],
                'w': data['width'][i],
                'h': data['height'][i],
                'conf': conf
            })
    return words

def box_overlap(box, rect):
    return (box['x'] < rect['x'] + rect['width'] and 
            box['x'] + box['w'] > rect['x'] and 
            box['y'] < rect['y'] + rect['height'] and 
            box['y'] + box['h'] > rect['y'])

def apply_user_blurs_to_text(words, blur_rectangles):
    if not blur_rectangles:
        return " ".join([w['text'] for w in words]), 0
    parts = []
    count = 0
    for word in words:
        if any(box_overlap(word, r) for r in blur_rectangles):
            parts.append("[BLURRED]")
            count += 1
        else:
            parts.append(word['text'])
    return " ".join(parts), count

# =====================================================================
# DAY 11: IMAGE PROVENANCE & AUTHENTICITY ENGINE
# =====================================================================
def rgb_to_hsl(r, g, b):
    r, g, b = r/255.0, g/255.0, b/255.0
    mx, mn = max(r, g, b), min(r, g, b)
    l = (mx + mn) / 2
    if mx == mn:
        h = s = 0
    else:
        d = mx - mn
        s = d / (2 - mx - mn) if l > 0.5 else d / (mx + mn)
        if mx == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif mx == g:
            h = (b - r) / d + 2
        else:
            h = (r - g) / d + 4
        h /= 6
    return h * 360, s, l

def calculate_color_harmony(palette):
    if len(palette) < 2:
        return 80
    hues = []
    for r, g, b in palette:
        h, s, l = rgb_to_hsl(r, g, b)
        if s > 0.1 and 0.1 < l < 0.9:
            hues.append(h)
    if len(hues) < 2:
        return 75
    hues.sort()
    diffs = []
    for i in range(len(hues)):
        diff = abs(hues[i] - hues[(i + 1) % len(hues)])
        if diff > 180:
            diff = 360 - diff
        diffs.append(diff)
    avg_diff = sum(diffs) / len(diffs)
    analogous_score = max(0, 100 - abs(avg_diff - 45) * 2)
    complementary_score = max(0, 100 - abs(avg_diff - 180) * 1.5)
    monochromatic_score = max(0, 100 - avg_diff * 3)
    triadic_score = max(0, 100 - abs(avg_diff - 120) * 1.5)
    return int(max(analogous_score, complementary_score, monochromatic_score, triadic_score))

def extract_dominant_palette(pil_image, k=5):
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    small_img = pil_image.resize((150, 150))
    pixels = np.array(small_img).reshape(-1, 3)
    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
    kmeans.fit(pixels)
    return kmeans.cluster_centers_.astype(int).tolist()

def detect_jpeg_generation(pil_image):
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape
    block_size = 8
    dct_values = []
    for y in range(0, h - block_size, block_size):
        for x in range(0, w - block_size, block_size):
            block = np.float32(gray[y:y+block_size, x:x+block_size])
            dct = cv2.dct(block)
            dct_values.extend(dct[4:, 4:].flatten().tolist())
    if not dct_values:
        return {"generation_estimate": 1, "quality_score": 80, "compression_artifacts": 0}
    dct_array = np.array(dct_values)
    zero_ratio = np.sum(np.abs(dct_array) < 1.0) / len(dct_array)
    if zero_ratio > 0.7:
        generation, quality_score = 4, 20
    elif zero_ratio > 0.5:
        generation, quality_score = 3, 45
    elif zero_ratio > 0.3:
        generation, quality_score = 2, 65
    else:
        generation, quality_score = 1, 85
    return {
        "generation_estimate": generation,
        "quality_score": quality_score,
        "compression_artifacts": round(zero_ratio * 100, 1),
        "confidence": "high" if len(dct_values) > 100 else "low"
    }

def analyze_image_authenticity(pil_image):
    palette = extract_dominant_palette(pil_image)
    harmony_score = calculate_color_harmony(palette)
    jpeg_analysis = detect_jpeg_generation(pil_image)
    authenticity_score = 100
    if jpeg_analysis["generation_estimate"] >= 3:
        authenticity_score -= 35
    elif jpeg_analysis["generation_estimate"] == 2:
        authenticity_score -= 15
    if harmony_score < 40:
        authenticity_score -= 25
    elif harmony_score < 60:
        authenticity_score -= 10
    authenticity_score = max(0, min(100, authenticity_score))
    reasons = []
    if harmony_score >= 70:
        reasons.append(f"✓ Professional color palette (Harmony: {harmony_score}%)")
    else:
        reasons.append(f"⚠ Chaotic color palette (Harmony: {harmony_score}%)")
    if jpeg_analysis["generation_estimate"] <= 1:
        reasons.append("✓ Original quality image")
    else:
        reasons.append(f"⚠ Image recompressed {jpeg_analysis['generation_estimate']-1}x")
    return {
        "authenticity_score": authenticity_score,
        "color_harmony": harmony_score,
        "dominant_palette": palette,
        "jpeg_generation": jpeg_analysis,
        "reasons": reasons
    }

# =====================================================================
# HELPER FUNCTIONS
# =====================================================================
def pil_to_base64(pil_img):
    if pil_img.mode != 'RGB':
        pil_img = pil_img.convert('RGB')
    buffered = BytesIO()
    pil_img.save(buffered, format="JPEG", quality=85)
    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
    return f"data:image/jpeg;base64,{img_str}"

def deobfuscate_text(text):
    text = text.replace('[.]', '.').replace('(.)', '.')
    text = re.sub(r'hxxp', 'http', text, flags=re.IGNORECASE)
    text = re.sub(r'\b[AvV]{1,2}ww\b', 'www', text)
    text = re.sub(r'(https?[:/])(?!/)', r'\1/', text)
    return text

BRAND_DOMAIN_MATRIX = {
    'hdfc': ['hdfcbank.com', 'hdfcbk.io', 'hdfc.com'],
    'sbi': ['sbi.co.in', 'sbi.in', 'onlinesbi.com', 'statebank'],
    'icici': ['icicibank.com', 'icici.id'],
    'federal': ['federalbank.co.in', 'sihub.in'],
    'axis': ['axisbank.com'],
    'paytm': ['paytm.com'],
    'phonepe': ['phonepe.com'],
    'amazon': ['amazon.in', 'amzn.to']
}

def check_cross_channel_match(text, url_domain):
    text_lower = text.lower()
    mentioned_brands = [brand for brand in BRAND_DOMAIN_MATRIX.keys() if brand in text_lower]
    if not mentioned_brands:
        return False, []
    for brand in mentioned_brands:
        allowed_domains = BRAND_DOMAIN_MATRIX[brand]
        if any(allowed in url_domain for allowed in allowed_domains):
            return True, [f"✓ Cross-Check: URL '{url_domain}' linked to '{brand.upper()}'."]
    return False, [f"⚠ Cross-Check Mismatch: Text mentions {mentioned_brands} but URL is '{url_domain}'."]

def normalize_text_advanced(text):
    invisible_chars = re.compile(r'[\u200B-\u200D\uFEFF\u00A0\u2028\u2029]')
    text = invisible_chars.sub('', text)
    text = unicodedata.normalize('NFKC', text)
    homoglyph_map = {
        'а': 'a', 'с': 'c', 'е': 'e', 'о': 'o', 'р': 'p', 'х': 'x', 'у': 'y', 'і': 'i',
        'А': 'A', 'С': 'C', 'Е': 'E', 'О': 'O', 'Р': 'P', 'Х': 'X', 'У': 'Y', 'І': 'I',
        'ј': 'j', 'ѕ': 's', 'ԁ': 'd', 'ɡ': 'g', 'ԛ': 'q', 'ԝ': 'w', 'ν': 'v', 'τ': 't'
    }
    for fake_char, real_char in homoglyph_map.items():
        text = text.replace(fake_char, real_char)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\.\s+(com|net|org|in|io|co|info|biz|me|be|xyz|app|web)\b', r'.\1', text, flags=re.IGNORECASE)
    text = re.sub(r'(https?[:/])\s+', r'\1', text, flags=re.IGNORECASE)
    return text

def preprocess_image(image):
    if image.mode != 'RGB':
        image = image.convert('RGB')
    gray = ImageOps.grayscale(image)
    width, height = gray.size
    gray = gray.resize((width * 2, height * 2), Image.Resampling.LANCZOS)
    gray = ImageEnhance.Contrast(gray).enhance(3.0)
    threshold = 130
    binary = gray.point(lambda p: 255 if p > threshold else 0)
    return ImageEnhance.Sharpness(binary).enhance(2.0)

# =====================================================================
# DAY 10: SMART QR INTELLIGENCE ENGINE
# =====================================================================
def preprocess_for_qr(pil_image):
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    height, width = gray.shape
    gray = cv2.resize(gray, (width * 3, height * 3), interpolation=cv2.INTER_CUBIC)
    thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 11, 2)
    return cv2.GaussianBlur(thresh, (5, 5), 0)

def detect_qr_and_boxes(pil_image):
    qr_results = []
    qr_preprocessed = preprocess_for_qr(pil_image)
    if pil_image.mode != 'RGB':
        pil_image_rgb = pil_image.convert('RGB')
    else:
        pil_image_rgb = pil_image
    original_cv = cv2.cvtColor(np.array(pil_image_rgb), cv2.COLOR_RGB2BGR)
    images_to_try = [
        ("Preprocessed", qr_preprocessed),
        ("Original Grayscale", cv2.cvtColor(original_cv, cv2.COLOR_BGR2GRAY)),
        ("Original Color", original_cv)
    ]
    for strategy_name, img in images_to_try:
        try:
            try:
                detector = cv2.QRCodeDetector_create()
            except:
                detector = cv2.QRCodeDetector()
            retval, decoded_info, points, _ = detector.detectAndDecodeMulti(img)
            if retval and points is not None and len(decoded_info) > 0:
                for i in range(len(decoded_info)):
                    if decoded_info[i] and decoded_info[i].strip():
                        qr_results.append({
                            "data": decoded_info[i].strip(),
                            "points": points[i]
                        })
            if not qr_results:
                data, pts, _ = detector.detectAndDecode(img)
                if data and data.strip() and pts is not None:
                    qr_results.append({"data": data.strip(), "points": pts})
        except Exception as e:
            continue
        if qr_results:
            break
    return qr_results

def draw_qr_boxes(pil_image, qr_results):
    if pil_image.mode != 'RGB':
        pil_image = pil_image.convert('RGB')
    cv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    for qr in qr_results:
        pts = qr["points"].astype(int)
        cv2.polylines(cv_img, [pts], True, (0, 255, 0), 5)
    rgb_img = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
    return Image.fromarray(rgb_img)

def classify_and_enrich_qr(qr_data):
    intent = "UNKNOWN"
    metadata = {}
    warning = None
    if qr_data.lower().startswith("upi://pay"):
        intent = "UPI_PAYMENT"
        parsed = urllib.parse.urlparse(qr_data)
        params = urllib.parse.parse_qs(parsed.query)
        payee_name = params.get('pn', ['Unknown Merchant'])[0]
        payee_addr = params.get('pa', ['Unknown UPI ID'])[0]
        amount = params.get('am', ['0'])[0]
        metadata = {
            "payee_name": payee_name,
            "payee_address": payee_addr,
            "amount": amount
        }
        warning = f"Warning: Scanning will transfer ₹{amount} to '{payee_name}'!"
    elif qr_data.lower().startswith("http://") or qr_data.lower().startswith("https://") or re.match(r'^[a-zA-Z0-9-]+\.[a-zA-Z]{2,}', qr_data):
        intent = "URL"
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            response = requests.get(qr_data, timeout=3, headers=headers, allow_redirects=True)
            soup = BeautifulSoup(response.text, 'html.parser')
            title = soup.title.string.strip() if soup.title and soup.title.string else "No Title Found"
            metadata["title"] = title
            metadata["final_url"] = response.url
        except Exception as e:
            metadata["title"] = "Could not fetch preview"
    elif "BEGIN:VCARD" in qr_data.upper():
        intent = "CONTACT_CARD"
        name_match = re.search(r'FN:(.*)', qr_data)
        if name_match:
            metadata["name"] = name_match.group(1).strip()
    else:
        intent = "PLAIN_TEXT"
        metadata["text_preview"] = qr_data[:100] + "..." if len(qr_data) > 100 else qr_data
    return {"intent": intent, "metadata": metadata, "warning": warning, "raw_data": qr_data}

# =====================================================================
# URL EXTRACTION
# =====================================================================
def extract_urls_robust(text):
    urls = []
    patterns = [
        r'https?[:/]', r'www\.',
        r'\b[a-zA-Z0-9-]+\.[a-zA-Z0-9.-]+/[a-zA-Z0-9/._-]*',
        r'\b[a-zA-Z0-9-]+\.(?:com|net|org|in|io|co|info|biz|me|be|xyz|app|link|site|online|top|club|store|tech|live|fun|today|click|web|cloud|digital|global|zone|cc|tk|buzz)\b'
    ]
    combined_pattern = re.compile('|'.join(patterns), re.IGNORECASE)
    matches = combined_pattern.finditer(text)
    
    known_tlds = {'com', 'net', 'org', 'in', 'io', 'co', 'info', 'biz', 'me', 'be', 
                  'xyz', 'app', 'web', 'cc', 'tk', 'top', 'club', 'buzz', 'site', 
                  'online', 'store', 'tech', 'live', 'fun'}
    email_domains = {'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com', 'icici.com', 'hdfc.com'}
    
    def contains_tld(word):
        w = word.lower().strip('.,;:')
        for tld in known_tlds:
            if w.endswith('.' + tld) or w == tld:
                return True
        if '.web.app' in w or w.endswith('.web'):
            return True
        return False

    processed_starts = set()
    for match in matches:
        start_idx = match.start()
        if start_idx in processed_starts:
            continue
        processed_starts.add(start_idx)
        remaining_text = text[start_idx:]
        tokens = re.split(r'(\s+)', remaining_text)
        url_parts = []
        has_seen_slash = False
        has_seen_tld = False
        i = 0
        while i < len(tokens):
            token = tokens[i]
            if re.match(r'^\s*$', token):
                if i + 1 < len(tokens):
                    next_word = tokens[i+1].strip()
                    next_next_word = tokens[i+3].strip() if i + 3 < len(tokens) else ""
                    should_break = False
                    if len(next_word) == 1:
                        should_break = True
                    elif next_word.isupper() and len(next_word) > 2:
                        should_break = True
                    elif next_word and next_word[-1] in '.,!?;:':
                        if not contains_tld(next_word):
                            should_break = True
                    elif next_word.isalpha() and next_next_word.isalpha():
                        if not contains_tld(next_next_word):
                            should_break = True
                    elif has_seen_tld and not next_word.startswith(('/', '.')):
                        should_break = True
                    if should_break:
                        break
                    if contains_tld(next_word):
                        has_seen_tld = True
                    if '/' in next_word:
                        has_seen_slash = True
                    url_parts.append(next_word)
                    i += 2
                    continue
                else:
                    break
            else:
                if '/' in token:
                    has_seen_slash = True
                if contains_tld(token):
                    has_seen_tld = True
                url_parts.append(token)
                i += 1
        raw_url = "".join(url_parts)
        raw_url = re.sub(r'^https?:/*', 'https://', raw_url, flags=re.IGNORECASE)
        raw_url = re.sub(r'^\|', 'l', raw_url)
        raw_url = re.sub(r'[\[\]\(\)\{\}<>]', '', raw_url)
        raw_url = re.sub(r'([a-zA-Z0-9])(com|net|org|in|io|co|info|biz|me|be|xyz|app|web|cc|tk)\b', r'\1.\2', raw_url, flags=re.IGNORECASE)
        raw_url = re.sub(r'\d{1,2}:\d{2}\s?(am|pm)?$', '', raw_url, flags=re.IGNORECASE)
        raw_url = raw_url.rstrip('.,;:-')
        if raw_url.lower() in email_domains:
            continue
        if raw_url:
            urls.append(raw_url)
    final_urls = []
    for u in urls:
        if not any(u != other and u in other for other in urls):
            final_urls.append(u)
    return final_urls

# =====================================================================
# SENSITIVE DATA REDACTION
# =====================================================================
def redact_sensitive_data(text):
    def mask_email(match):
        return f"{match.group(1)[:2]}{'X' * max(0, len(match.group(1)) - 2)}@{match.group(2)}"
    text = re.sub(r'([a-zA-Z0-9._-]+)@([a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', mask_email, text)
    def mask_pan(match):
        return 'XXXXX' + match.group(0)[5:]
    text = re.sub(r'\b[A-Z]{5}\d{4}[A-Z]\b', mask_pan, text)
    def mask_aadhaar(match):
        return 'XXXX XXXX ' + re.sub(r'\s', '', match.group(0))[-4:]
    text = re.sub(r'\b(\d\s*){12}\b', mask_aadhaar, text)
    def mask_phone(match):
        digits = re.sub(r'\D', '', match.group(0))
        if len(digits) == 10:
            return digits[:2] + 'XXXXXX' + digits[-2:]
        elif len(digits) == 12:
            return '+91-' + digits[2:4] + 'XXXXXX' + digits[-2:]
        return match.group(0)
    text = re.sub(r'(?:\+91[\s-]?)?\b\d{10}\b', mask_phone, text)
    def mask_account(match):
        acc = match.group(0)
        return 'X' * (len(acc) - 4) + acc[-4:] if len(acc) > 4 else acc
    text = re.sub(r'\b\d{9,18}\b', mask_account, text)
    return text

def extract_entities(text):
    urls = extract_urls_robust(text)
    phones = re.findall(r'(?:\+91[\s-]?)?\b\d{10,13}\b', text)
    upi_blacklist = {'gmail', 'yahoo', 'hotmail', 'outlook', 'icici', 'hdfc', 'sbi', 'rediffmail'}
    raw_upis = re.findall(r'([a-zA-Z0-9.\-_]+)@([a-zA-Z0-9]+)', text)
    upi_ids = [f"{local}@{handle}" for local, handle in raw_upis if handle.lower() not in upi_blacklist]
    return {"urls": urls, "phone_numbers": list(set(phones)), "upi_ids": list(set(upi_ids))}

# =====================================================================
# ENTERPRISE URL ANALYSIS
# =====================================================================
def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    return previous_row[-1]

def calculate_entropy(s):
    if not s:
        return 0
    counts = Counter(s)
    length = len(s)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())

def analyze_url_layers(url):
    url_score = 0
    url_reasons = []
    domain_match = re.search(r'(?:https?://)?(?:www\.)?([^/\s:]+)', url)
    if not domain_match:
        return 0, []
    full_domain = domain_match.group(1).lower()
    parts = full_domain.split('.')
    tld = parts[-1]
    sld = parts[-2] if len(parts) > 1 else parts[0]
    WHITELIST = {
        'hdfcbk.io', 'icici.id', 'sbi.co.in', 'hdfcbank.com', 'icicibank.com',
        'axisbank.com', 'paytm.com', 'phonepe.com', 'amazon.in', 'flipkart.com', 'sihub.in'
    }
    if full_domain in WHITELIST or f"{sld}.{tld}" in WHITELIST:
        url_reasons.append("✓ Layer 1: Exact match with Official Whitelist (Safe)")
        return -50, url_reasons
    BRANDS = ['hdfc', 'sbi', 'icici', 'axis', 'paytm', 'phonepe', 'amazon', 'flipkart']
    OFFICIAL_NAMES = {'hdfc': 'hdfcbank', 'sbi': 'statebank', 'icici': 'icicibank', 'axis': 'axisbank'}
    for brand in BRANDS:
        if brand in full_domain:
            url_score += 30
            url_reasons.append(f"✓ Layer 2: Contains brand keyword ('{brand}') but NOT whitelisted")
            break
    for brand in BRANDS:
        target = OFFICIAL_NAMES.get(brand, brand)
        dist = levenshtein_distance(sld, target)
        if 0 < dist <= 2 and sld != target:
            url_score += 40
            url_reasons.append(f"✓ Layer 2: Typosquatting! '{sld}' is {dist} edit distance from '{target}'")
            break
    entropy = calculate_entropy(sld)
    if entropy > 3.5 and len(sld) > 6:
        url_score += 25
        url_reasons.append(f"✓ Layer 2: High Entropy (Randomly generated domain string)")
    try:
        import whois
        from datetime import datetime
        w = whois.whois(full_domain)
        if w.creation_date:
            creation_date = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            age_days = (datetime.now() - creation_date).days
            if age_days < 90:
                url_score += 40
                url_reasons.append(f"✓ Layer 3: Domain is very new ({age_days} days old)")
            elif age_days < 365:
                url_score += 15
                url_reasons.append(f"✓ Layer 3: Domain is less than a year old ({age_days} days)")
    except Exception:
        pass
    return url_score, url_reasons

# =====================================================================
# HYBRID SCAM ANALYSIS ENGINE (Statistical ML + Algorithmic Signals)
# =====================================================================
def analyze_scam(text, urls, qr_enrichments, visual_report):
    """
    PRIMARY: Statistical ML model makes the main decision.
    SECONDARY: Algorithmic signals (URL, QR, Visual) provide additional confidence.
    """
    score = 0
    reasons = []
    category = "Unknown"
    scam_prob = 0.5
    
    # =================================================================
    # PRIMARY SIGNAL: STATISTICAL ML MODEL (Makes the main decision)
    # =================================================================
    if STAT_MODEL is not None:
        try:
            # Get probability directly from model
            scam_prob = STAT_MODEL.predict_proba([text])[0][1]
            
            # Model makes the primary decision
            if scam_prob > 0.7:
                score = int(70 + (scam_prob - 0.7) * 100)  # 70-100
                reasons.append(f"🤖 ML Model: HIGH scam confidence ({scam_prob:.1%})")
            elif scam_prob > 0.5:
                score = int(50 + (scam_prob - 0.5) * 100)  # 50-70
                reasons.append(f"🤖 ML Model: Moderate scam confidence ({scam_prob:.1%})")
            elif scam_prob > 0.3:
                score = int(30 + (scam_prob - 0.3) * 100)  # 30-50
                reasons.append(f"🤖 ML Model: Uncertain ({scam_prob:.1%})")
            else:
                score = int(scam_prob * 100)  # 0-30
                reasons.append(f"🤖 ML Model: Likely legitimate ({1-scam_prob:.1%})")
            
        except Exception as e:
            reasons.append(f"⚠ ML Model error: {str(e)}")
            score = 50  # Default uncertain
    else:
        reasons.append("⚠ ML Model not loaded")
        score = 50
    
    # =================================================================
    # SECONDARY SIGNALS: Algorithmic (Add confidence, don't override)
    # =================================================================
    
    # Visual authenticity
    auth = visual_report.get("authenticity_score", 100)
    if auth < 40:
        score = min(100, score + 10)
        reasons.append(f"🚨 Low image authenticity ({auth}%)")
    elif auth >= 70:
        reasons.append(f"✓ High image authenticity ({auth}%)")
    
    # QR codes
    if qr_enrichments:
        for qr in qr_enrichments:
            if qr["intent"] == "UPI_PAYMENT":
                score = min(100, score + 20)
                reasons.append("🚨 QR CODE IS A DIRECT UPI PAYMENT REQUEST!")
                category = "Malicious QR Scam"
    
    # URL analysis
    is_shortener = False
    if urls:
        score = min(100, score + 5)
        reasons.append("✓ Contains a link")
        for url in urls:
            us, ur = analyze_url_layers(url)
            if us > 0:  # Suspicious URL
                score = min(100, score + 10)
                reasons.extend(ur[:1])  # Only add first reason to avoid clutter
            if us >= 0:
                if re.search(r'\.(cc|tk|xyz|top|club|buzz)$', url.lower()):
                    is_shortener = True
                    score = min(100, score + 10)
                    reasons.append("✓ High-risk TLD")
    
    # =================================================================
    # CATEGORY DETERMINATION (Based on signals)
    # =================================================================
    if category == "Unknown":
        # Use URL patterns for category hints
        if urls:
            url_text = " ".join(urls).lower()
            if "kyc" in url_text:
                category = "Bank KYC Scam"
            elif any(b in url_text for b in ["hdfc", "sbi", "icici", "axis", "bank"]):
                category = "Banking Scam"
            elif any(c in url_text for c in ["courier", "fedex", "customs", "dhl"]):
                category = "Courier Scam"
            elif any(g in url_text for g in ["incometax", "epfo", "gov"]):
                category = "Government Scam"
        
        # Use ML confidence for category
        if scam_prob > 0.7 and category == "Unknown":
            category = "Suspicious Message"
    
    # =================================================================
    # FINAL SCORE
    # =================================================================
    if is_shortener and score > 30:
        score = max(score, 85)
        if category == "Unknown":
            category = "Phishing Scam"
    
    score = max(0, min(score, 100))
    
    if score < 30:
        category = "Likely Safe"
        if score == 0 and not reasons:
            reasons.append("✓ No scam indicators found")
    
    return {"risk_score": score, "category": category, "reasons": reasons}

def generate_recommendation(category, score):
    if score < 30:
        return "✅ This message appears safe."
    elif score < 70:
        return "Exercise caution. Verify using the official app."
    else:
        recs = {
            "QR": "🚨 EXTREME RISK: Malicious QR code. DO NOT SCAN.",
            "KYC": "🚨 HIGH RISK: Banks never ask for KYC via SMS.",
            "Fake Receipt": "🚨 HIGH RISK: FAKE RECEIPT. Legitimate receipts never ask for action.",
            "E-Challan": "🚨 HIGH RISK: E-CHALLAN SCAM. Visit official police website.",
            "Utility": "🚨 HIGH RISK: UTILITY SCAM. Contact official customer service.",
            "Job": "🚨 HIGH RISK: JOB SCAM. Legitimate jobs don't ask for fees.",
            "Lottery": "🚨 HIGH RISK: LOTTERY SCAM. You can't win what you didn't enter.",
            "Courier": "🚨 HIGH RISK: Courier scam. Contact courier directly.",
            "Government": "🚨 HIGH RISK: Government impersonation.",
            "Banking": "🚨 HIGH RISK: Phishing attempt. Use official app.",
            "Phishing": "🚨 HIGH RISK: Phishing attempt. Use official app.",
            "Crypto": "🚨 HIGH RISK: Cryptocurrency scam. Never invest based on unsolicited messages.",
            "Tech Support": "🚨 HIGH RISK: Tech support scam. Contact official support directly.",
            "Romance": "🚨 HIGH RISK: Romance scam. Never send money to online contacts.",
            "Fake Charity": "🚨 HIGH RISK: Fake charity scam. Verify before donating.",
        }
        for key, rec in recs.items():
            if key in category:
                return rec
        return "🚨 HIGH RISK: Confirmed scam pattern."

# =====================================================================
# MAIN ENDPOINT
# =====================================================================
@app.post("/upload/")
async def upload_and_analyze_screenshot(
    file: UploadFile = File(...),
    blur_rectangles: str = Form(default="[]")
):
    if file.content_type not in ["image/png", "image/jpeg", "image/jpg"]:
        raise HTTPException(status_code=400, detail="Only PNG, JPG, and JPEG are allowed.")
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    try:
        rectangles = json.loads(blur_rectangles)
        if not isinstance(rectangles, list):
            rectangles = []
    except:
        rectangles = []
    try:
        image = Image.open(file_path)
        processed_image = preprocess_image(image)
        visual_report = analyze_image_authenticity(image)
        qr_results = detect_qr_and_boxes(image)
        highlighted_img = draw_qr_boxes(image, qr_results)
        highlighted_img_base64 = pil_to_base64(highlighted_img)
        qr_enrichments = [classify_and_enrich_qr(qr["data"]) for qr in qr_results]
        raw_text = pytesseract.image_to_string(processed_image, config='--psm 6')
        words_with_boxes = get_word_bounding_boxes(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")
    normalized_text = normalize_text_advanced(raw_text)
    defanged_text = deobfuscate_text(normalized_text)
    user_blurred_text, user_blur_count = apply_user_blurs_to_text(words_with_boxes, rectangles)
    redacted_text = redact_sensitive_data(defanged_text)
    entities = extract_entities(defanged_text)
    scam_analysis = analyze_scam(redacted_text, entities["urls"], qr_enrichments, visual_report)
    scam_analysis["recommendation"] = generate_recommendation(scam_analysis["category"], scam_analysis["risk_score"])
    display_text = user_blurred_text if user_blur_count > 0 else redacted_text
    if user_blur_count > 0:
        display_text = redact_sensitive_data(display_text)
    return {
        "message": "Analysis Complete",
        "filename": file.filename,
        "extracted_text": display_text.strip(),
        "entities": entities,
        "highlighted_image": highlighted_img_base64,
        "qr_analysis": qr_enrichments,
        "visual_authenticity": visual_report,
        "user_blur_count": user_blur_count,
        "trust_report": scam_analysis
    }
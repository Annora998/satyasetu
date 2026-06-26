"""
Diagnose why specific scams are being missed.
Shows the actual extracted text and score breakdown.
"""

import requests
from pathlib import Path
import json

API_URL = "http://127.0.0.1:8000/upload/"
SCAMS_DIR = Path(__file__).parent / "scams"

def analyze_failure(image_path):
    """Analyze a single failed scam image."""
    with open(image_path, 'rb') as f:
        files = {'file': (image_path.name, f, 'image/png')}
        data = {'blur_rectangles': '[]'}
        response = requests.post(API_URL, files=files, data=data)
    
    if response.status_code != 200:
        return None
    
    result = response.json()
    return {
        'file': image_path.name,
        'extracted_text': result.get('extracted_text', ''),
        'risk_score': result['trust_report']['risk_score'],
        'category': result['trust_report']['category'],
        'reasons': result['trust_report']['reasons'],
        'urls': result['entities']['urls'],
    }

def main():
    print("=" * 70)
    print("FAILURE DIAGNOSTIC")
    print("=" * 70)
    
    # Get all scam images
    scam_files = sorted(SCAMS_DIR.glob("*.png"))
    
    failures = {'0': [], '25': [], '50': [], '60-65': []}
    
    for img_path in scam_files:
        result = analyze_failure(img_path)
        if result and result['risk_score'] < 70:
            score = result['risk_score']
            if score == 0:
                failures['0'].append(result)
            elif score == 25:
                failures['25'].append(result)
            elif score == 50:
                failures['50'].append(result)
            elif 60 <= score <= 65:
                failures['60-65'].append(result)
    
    print(f"\nTotal failures: {sum(len(v) for v in failures.values())}")
    print(f"  Score 0:    {len(failures['0'])}")
    print(f"  Score 25:   {len(failures['25'])}")
    print(f"  Score 50:   {len(failures['50'])}")
    print(f"  Score 60-65: {len(failures['60-65'])}")
    
    # Show samples from each category
    for score_bucket, cases in failures.items():
        if not cases:
            continue
        print(f"\n{'='*70}")
        print(f"SCORE {score_bucket} SAMPLES (showing first 3)")
        print(f"{'='*70}")
        for case in cases[:3]:
            print(f"\n📄 {case['file']}")
            print(f"   Score: {case['risk_score']} | Category: {case['category']}")
            print(f"   Text: {case['extracted_text'][:150]}...")
            print(f"   URLs: {case['urls']}")
            print(f"   Reasons:")
            for r in case['reasons']:
                print(f"      {r}")

if __name__ == "__main__":
    main()
"""
SatyaSetu Test Suite - Day 13
Runs automated tests on scam and legitimate message datasets.
"""

import os
import requests
import json
import time
from datetime import datetime
from pathlib import Path

API_URL = "http://127.0.0.1:8000/upload/"
TESTS_DIR = Path(__file__).parent
SCAMS_DIR = TESTS_DIR / "scams"
LEGIT_DIR = TESTS_DIR / "legit"
RESULTS_DIR = TESTS_DIR / "results"

RESULTS_DIR.mkdir(exist_ok=True)

def test_single_image(image_path, expected_category):
    """Tests a single image against the API."""
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (image_path.name, f, 'image/png')}
            data = {'blur_rectangles': '[]'}
            
            start_time = time.time()
            response = requests.post(API_URL, files=files, data=data)
            elapsed = time.time() - start_time
            
            if response.status_code != 200:
                return {
                    'file': image_path.name,
                    'status': 'ERROR',
                    'error': f"HTTP {response.status_code}",
                    'expected': expected_category,
                    'predicted': None,
                    'risk_score': None,
                    'time': elapsed
                }
            
            result = response.json()
            trust_report = result.get('trust_report', {})
            
            return {
                'file': image_path.name,
                'status': 'SUCCESS',
                'expected': expected_category,
                'predicted': trust_report.get('category', 'Unknown'),
                'risk_score': trust_report.get('risk_score', 0),
                'reasons': trust_report.get('reasons', []),
                'recommendation': trust_report.get('recommendation', ''),
                'entities': result.get('entities', {}),
                'qr_count': len(result.get('qr_analysis', [])),
                'user_blur_count': result.get('user_blur_count', 0),
                'time': elapsed
            }
            
    except Exception as e:
        return {
            'file': image_path.name,
            'status': 'ERROR',
            'error': str(e),
            'expected': expected_category,
            'predicted': None,
            'risk_score': None,
            'time': 0
        }

def calculate_metrics(scam_results, legit_results):
    """Calculates accuracy metrics."""
    metrics = {
        'total_tests': 0,
        'successful_tests': 0,
        'failed_tests': 0,
        'scam_total': len(scam_results),
        'scam_detected': 0,
        'scam_missed': 0,
        'scam_avg_score': 0,
        'legit_total': len(legit_results),
        'legit_correct': 0,
        'legit_flagged': 0,
        'legit_avg_score': 0,
        'accuracy': 0,
        'precision': 0,
        'recall': 0,
        'f1_score': 0,
        'avg_processing_time': 0
    }
    
    all_results = scam_results + legit_results
    successful = [r for r in all_results if r['status'] == 'SUCCESS']
    
    metrics['total_tests'] = len(all_results)
    metrics['successful_tests'] = len(successful)
    metrics['failed_tests'] = len(all_results) - len(successful)
    
    scam_scores = []
    for r in scam_results:
        if r['status'] == 'SUCCESS':
            score = r['risk_score']
            scam_scores.append(score)
            if score >= 50:
                metrics['scam_detected'] += 1
            else:
                metrics['scam_missed'] += 1
    
    if scam_scores:
        metrics['scam_avg_score'] = round(sum(scam_scores) / len(scam_scores), 2)
    
    legit_scores = []
    for r in legit_results:
        if r['status'] == 'SUCCESS':
            score = r['risk_score']
            legit_scores.append(score)
            if score < 30:
                metrics['legit_correct'] += 1
            else:
                metrics['legit_flagged'] += 1
    
    if legit_scores:
        metrics['legit_avg_score'] = round(sum(legit_scores) / len(legit_scores), 2)
    
    true_positives = metrics['scam_detected']
    true_negatives = metrics['legit_correct']
    false_positives = metrics['legit_flagged']
    false_negatives = metrics['scam_missed']
    
    total_correct = true_positives + true_negatives
    total_tests = true_positives + true_negatives + false_positives + false_negatives
    
    if total_tests > 0:
        metrics['accuracy'] = round((total_correct / total_tests) * 100, 2)
    
    if (true_positives + false_positives) > 0:
        metrics['precision'] = round(
            (true_positives / (true_positives + false_positives)) * 100, 2
        )
    
    if (true_positives + false_negatives) > 0:
        metrics['recall'] = round(
            (true_positives / (true_positives + false_negatives)) * 100, 2
        )
    
    if metrics['precision'] + metrics['recall'] > 0:
        metrics['f1_score'] = round(
            2 * (metrics['precision'] * metrics['recall']) / 
            (metrics['precision'] + metrics['recall']), 2
        )
    
    times = [r['time'] for r in successful if r['time'] > 0]
    if times:
        metrics['avg_processing_time'] = round(sum(times) / len(times), 2)
    
    return metrics

def generate_report(scam_results, legit_results, metrics):
    """Generates a detailed test report."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    report = {
        'test_run': {
            'timestamp': datetime.now().isoformat(),
            'api_url': API_URL,
            'scam_dataset_size': len(scam_results),
            'legit_dataset_size': len(legit_results)
        },
        'metrics': metrics,
        'scam_results': scam_results,
        'legit_results': legit_results
    }
    
    # Save JSON report
    json_path = RESULTS_DIR / f"test_report_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    # Save human-readable summary
    summary_path = RESULTS_DIR / f"test_summary_{timestamp}.txt"
    with open(summary_path, 'w') as f:
        f.write("=" * 70 + "\n")
        f.write("SATYASETU TEST REPORT\n")
        f.write("=" * 70 + "\n\n")
        
        f.write(f"Test Run: {report['test_run']['timestamp']}\n")
        f.write(f"Dataset: {metrics['scam_total']} scams, {metrics['legit_total']} legitimate\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("KEY METRICS\n")
        f.write("-" * 70 + "\n")
        f.write(f"Overall Accuracy:    {metrics['accuracy']}%\n")
        f.write(f"Precision:           {metrics['precision']}%\n")
        f.write(f"Recall:              {metrics['recall']}%\n")
        f.write(f"F1 Score:            {metrics['f1_score']}\n")
        f.write(f"Avg Processing Time: {metrics['avg_processing_time']}s\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("SCAM DETECTION\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Scams:         {metrics['scam_total']}\n")
        f.write(f"Correctly Detected:  {metrics['scam_detected']}\n")
        f.write(f"Missed:              {metrics['scam_missed']}\n")
        f.write(f"Average Risk Score:  {metrics['scam_avg_score']}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("LEGITIMATE MESSAGE HANDLING\n")
        f.write("-" * 70 + "\n")
        f.write(f"Total Legit:         {metrics['legit_total']}\n")
        f.write(f"Correctly Passed:    {metrics['legit_correct']}\n")
        f.write(f"False Positives:     {metrics['legit_flagged']}\n")
        f.write(f"Average Risk Score:  {metrics['legit_avg_score']}\n\n")
        
        f.write("-" * 70 + "\n")
        f.write("PROBLEMATIC CASES\n")
        f.write("-" * 70 + "\n")
        
        missed_scams = [r for r in scam_results if r['status'] == 'SUCCESS' and r['risk_score'] < 70]
        if missed_scams:
            f.write("\nMissed Scams (risk_score < 70):\n")
            for r in missed_scams:
                f.write(f"  - {r['file']} (score: {r['risk_score']}, category: {r['predicted']})\n")
        
        false_positives = [r for r in legit_results if r['status'] == 'SUCCESS' and r['risk_score'] >= 30]
        if false_positives:
            f.write("\nFalse Positives (legit flagged as scam):\n")
            for r in false_positives:
                f.write(f"  - {r['file']} (score: {r['risk_score']}, category: {r['predicted']})\n")
        
        f.write("\n" + "=" * 70 + "\n")
    
    return json_path, summary_path

def main():
    """Main test runner."""
    print("=" * 70)
    print("SATYASETU TEST SUITE")
    print("=" * 70)
    print()
    
    # Check if API is running
    try:
        requests.get("http://127.0.0.1:8000/", timeout=2)
        print("✓ API is running")
    except:
        print("✗ API is not running. Start it with: uvicorn main:app --reload")
        return
    
    # Check datasets
    scam_files = list(SCAMS_DIR.glob("*.png")) + list(SCAMS_DIR.glob("*.jpg")) + list(SCAMS_DIR.glob("*.jpeg"))
    legit_files = list(LEGIT_DIR.glob("*.png")) + list(LEGIT_DIR.glob("*.jpg")) + list(LEGIT_DIR.glob("*.jpeg"))
    
    print(f"✓ Found {len(scam_files)} scam images")
    print(f"✓ Found {len(legit_files)} legitimate images")
    
    if not scam_files and not legit_files:
        print("\n✗ No test images found!")
        return
    
    print()
    print("-" * 70)
    print("RUNNING TESTS...")
    print("-" * 70)
    
    # Test scam images
    scam_results = []
    for i, img_path in enumerate(scam_files, 1):
        print(f"[{i}/{len(scam_files)}] Testing scam: {img_path.name}")
        result = test_single_image(img_path, "scam")
        scam_results.append(result)
        if result['status'] == 'SUCCESS':
            status = "✓ DETECTED" if result['risk_score'] >= 70 else "✗ MISSED"
            print(f"   → {status} (score: {result['risk_score']}, category: {result['predicted']})")
        else:
            print(f"   → ERROR: {result.get('error', 'Unknown')}")
    
    # Test legitimate images
    legit_results = []
    for i, img_path in enumerate(legit_files, 1):
        print(f"[{i}/{len(legit_files)}] Testing legit: {img_path.name}")
        result = test_single_image(img_path, "legitimate")
        legit_results.append(result)
        if result['status'] == 'SUCCESS':
            status = "✓ PASSED" if result['risk_score'] < 30 else "✗ FALSE POSITIVE"
            print(f"   → {status} (score: {result['risk_score']}, category: {result['predicted']})")
        else:
            print(f"   → ERROR: {result.get('error', 'Unknown')}")
    
    print()
    print("-" * 70)
    print("CALCULATING METRICS...")
    print("-" * 70)
    
    metrics = calculate_metrics(scam_results, legit_results)
    json_path, summary_path = generate_report(scam_results, legit_results, metrics)
    
    print()
    print("=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Overall Accuracy:    {metrics['accuracy']}%")
    print(f"Precision:           {metrics['precision']}%")
    print(f"Recall:              {metrics['recall']}%")
    print(f"F1 Score:            {metrics['f1_score']}")
    print(f"Avg Processing Time: {metrics['avg_processing_time']}s")
    print()
    print(f"Scam Detection:      {metrics['scam_detected']}/{metrics['scam_total']}")
    print(f"Legit Handling:      {metrics['legit_correct']}/{metrics['legit_total']}")
    print()
    print(f"Reports saved to:")
    print(f"  - {json_path}")
    print(f"  - {summary_path}")
    print("=" * 70)

if __name__ == "__main__":
    main()
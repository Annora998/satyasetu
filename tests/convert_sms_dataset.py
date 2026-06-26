"""
Convert SMS Spam Collection dataset into test images for SatyaSetu.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

# UPDATE THIS PATH based on where your file is:
# Option A: If file is directly in tests folder:
DATASET_FILE = Path(r"E:\SatyaSetu\tests\SMSSpamCollection")

# Option B: If file is inside a subfolder, use this instead:
# DATASET_FILE = Path(r"E:\SatyaSetu\tests\SMSSpamCollection\SMSSpamCollection")

TESTS_DIR = Path(__file__).parent
SCAMS_DIR = TESTS_DIR / "scams"
LEGIT_DIR = TESTS_DIR / "legit"

SCAMS_DIR.mkdir(exist_ok=True)
LEGIT_DIR.mkdir(exist_ok=True)

def create_message_image(text, filename, label):
    """Creates an image from SMS text."""
    width, height = 800, 300
    img = Image.new('RGB', (width, height), color='white')
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 18)
        label_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        label_font = font
    
    label_text = "SCAM MESSAGE (Test Data)" if label == "spam" else "LEGITIMATE MESSAGE (Test Data)"
    label_color = 'red' if label == "spam" else 'green'
    d.text((40, 15), label_text, fill=label_color, font=label_font)
    d.line([(40, 40), (760, 40)], fill='gray', width=1)
    
    margin = 40
    current_height = 55
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) > 90:
            lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    for line in lines[:8]:
        d.text((margin, current_height), line, fill='black', font=font)
        current_height += 25
        if current_height > height - 50:
            break
    
    img.save(filename)
    return True

def main():
    print("=" * 70)
    print("SMS SPAM COLLECTION - CONVERTER")
    print("=" * 70)
    print()
    
    if not DATASET_FILE.exists():
        print(f"✗ Dataset file not found: {DATASET_FILE}")
        print("\nPlease check the DATASET_FILE path in the script.")
        print("The file should be named 'SMSSpamCollection' (no extension)")
        return
    
    print(f"Reading dataset from: {DATASET_FILE}")
    spam_messages = []
    ham_messages = []
    
    with open(DATASET_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            parts = line.split('\t', 1)
            if len(parts) == 2:
                label, message = parts
                label = label.lower()
                
                if label == 'spam':
                    spam_messages.append(message)
                elif label == 'ham':
                    ham_messages.append(message)
    
    print(f"✓ Found {len(spam_messages)} spam messages")
    print(f"✓ Found {len(ham_messages)} legitimate messages")
    print()
    
    num_scams = min(30, len(spam_messages))
    num_legit = min(20, len(ham_messages))
    
    random.seed(42)
    selected_scams = random.sample(spam_messages, num_scams)
    selected_legit = random.sample(ham_messages, num_legit)
    
    print(f"Selected {num_scams} spam and {num_legit} legitimate messages")
    print()
    
    print("Creating scam test images...")
    for i, message in enumerate(selected_scams, 1):
        filename = SCAMS_DIR / f"sms_spam_{i:02d}.png"
        create_message_image(message, filename, "spam")
    print(f"✓ Created {num_scams} scam images")
    
    print("Creating legitimate test images...")
    for i, message in enumerate(selected_legit, 1):
        filename = LEGIT_DIR / f"sms_legit_{i:02d}.png"
        create_message_image(message, filename, "ham")
    print(f"✓ Created {num_legit} legitimate images")
    
    print()
    print("=" * 70)
    print("CONVERSION COMPLETE")
    print("=" * 70)
    print(f"✓ Scam images: {SCAMS_DIR}")
    print(f"✓ Legit images: {LEGIT_DIR}")
    print()
    print("Next: Run the test suite")
    print("  python tests/run_tests.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
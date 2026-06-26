"""
Generate realistic Indian banking scam test images for SatyaSetu.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

TESTS_DIR = Path(__file__).parent
SCAMS_DIR = TESTS_DIR / "scams"
LEGIT_DIR = TESTS_DIR / "legit"

for f in SCAMS_DIR.glob("*.png"): f.unlink()
for f in LEGIT_DIR.glob("*.png"): f.unlink()

SCAM_TEMPLATES = [
    "Dear customer, your KYC is pending. Update now to avoid account closure. Click: hdfc-kyc-update.com/verify",
    "ALERT: Suspicious transaction of Rs.25,000 detected. Verify immediately: sbi-secure-login.net/check",
    "Your SBI account will be blocked today. Update PAN details: sbi-pan-update.in/urgent",
    "Congratulations! You won Rs.50,000 cashback. Claim now: paytm-reward.xyz/claim",
    "ICICI Bank: Your account is locked. Verify identity: icici-verify.com/login",
    "Payment of Rs.15,000 received. Scan QR to confirm: [UPI_QR_CODE]",
    "Customs Department: Your package is held. Pay duty Rs.500: customs-duty.cc/pay",
    # FIXED: Changed sihub.in (legit) to a suspicious domain
    "Federal Bank: E-mandate activated. Manage: federal-mandate-scam.xyz/manage",
    "Your HDFC credit card statement is ready. View: hdfc-statement-view.com/login",
    "Axis Bank: OTP is 847291. Never share. Verify: axis-otp-verify.net",
    "PhonePe: Rs.2,000 cashback credited. Scan to withdraw: phonepe-cashback.xyz",
    "Income Tax: Refund of Rs.12,500 pending. Claim: incometax-refund.cc/claim",
    "Your account credited Rs.45,000. Scan QR to pay: [MALICIOUS_QR]",
    "EPFO: Your PF withdrawal approved. Verify: epfo-claim.in/verify",
    "Amazon Pay: Rs.500 reward. Click to claim: amazon-reward.xyz/claim",
    "Bank Alert: Login from new device. Verify: hdfc-secure.net/verify",
    "Your PAN is not linked. Update now: pan-link-update.com/urgent",
    "Courier: Package stuck at customs. Pay Rs.750: fedex-customs.cc/pay",
    "Lottery: You won Rs.1,00,000! Contact: +91-9876543210",
    "Account suspended. Reactivate: icici-reactivate.com/login",
    "KYC expired. Update immediately: kyc-update-urgent.in",
    "Transaction failed. Update details: sbi-update.net/verify",
    "Cashback earned Rs.1,000. Scan to claim: [QR_CODE]",
    "Card blocked. Verify now: hdfc-card-verify.com",
    "Refund pending Rs.5,000. Claim: refund-claim.cc",
    "Account locked. Unlock: axis-unlock.net",
    "OTP generated 739284. Share to verify",
    "Payment received Rs.30,000. Confirm: [QR]",
    "PAN update required. Click: pan-update.xyz",
    "Account alert. Verify: bank-verify.in"
]

LEGIT_TEMPLATES = [
    "Dear Customer, your HDFC Bank Credit Card statement for XX is ready. Total amount Rs.35,201 due by 10-FEB.",
    "A/c XX6844 credited Rs.33,270 on 08-08-2021. Available balance Rs.45,890. -HDFC Bank",
    "Rs.500 debited from A/c XX1234 on 15-06-2024 at AMAZON. Bal Rs.12,500. -SBI",
    "Your ICICI Bank statement is ready. Login to view. Never share OTP. -ICICI Bank",
    "Transaction alert: Rs.1,200 paid to ELECTRICITY BOARD. A/c XX5678. -Axis Bank",
    "Dear Customer, your credit card bill of Rs.15,000 is due on 25-Jun. Pay to avoid interest.",
    "Rs.25,000 received in A/c XX9012 from JOHN DOE on 18-06-2024. -HDFC Bank",
    "Your FD of Rs.1,00,000 will mature on 30-06-2024. Contact branch for renewal.",
    "SBI: Online transaction of Rs.750 successful. Ref: 123456789. Bal Rs.8,250.",
    "HDFC Bank will never ask for OTP/PIN. Report suspicious calls to 1800-202-6161.",
    "Your A/c XX3456 has been debited Rs.2,500 for INSURANCE PREMIUM on 15-06-2024.",
    "Dear Customer, minimum amount due on your card is Rs.1,500. Due date: 20-Jun.",
    "Rs.10,000 transferred from A/c XX7890 to A/c XX1234 on 18-06-2024. -ICICI",
    "Your loan EMI of Rs.15,500 is due on 05-07-2024. Ensure sufficient balance.",
    "SBI: Card XX1234 used for Rs.450 at MCDONALDS on 18-06. Bal Rs.5,550.",
    "HDFC: Your statement is ready. View at hdfcbank.com. Never share credentials.",
    "Rs.5,000 credited to A/c XX5678 via NEFT from ABC CORP on 17-06-2024.",
    "Your debit card XX9012 will expire on 30-06-2024. Visit branch for renewal.",
    "Axis Bank: Fixed Deposit of Rs.50,000 matured. Principal + interest credited.",
    "Dear Customer, your total credit card balance is Rs.25,000. Pay by 25-Jun to avoid charges."
]

def create_message_image(text, filename, is_scam=True):
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color='white')
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        label_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        label_font = font
    
    header_color = '#dc2626' if is_scam else '#16a34a'
    header_text = "⚠️ SCAM MESSAGE (Test Data)" if is_scam else "✓ LEGITIMATE MESSAGE (Test Data)"
    
    d.rectangle([(0, 0), (width, 40)], fill=header_color)
    d.text((20, 10), header_text, fill='white', font=label_font)
    
    margin = 40
    current_height = 60
    
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = f"{current_line} {word}".strip()
        if len(test_line) > 85:
            lines.append(current_line)
            current_line = word
        else:
            current_line = word if not current_line else test_line
    
    if current_line:
        lines.append(current_line)
    
    for line in lines[:10]:
        d.text((margin, current_height), line, fill='black', font=font)
        current_height += 28
    
    d.text((margin, height - 40), "Received: 18-06-2024 14:30", fill='gray', font=label_font)
    
    img.save(filename)

def main():
    print("=" * 70)
    print("GENERATING INDIAN BANKING SCAM TEST DATASET")
    print("=" * 70)
    print()
    
    print(f"Creating {len(SCAM_TEMPLATES)} scam test images...")
    for i, template in enumerate(SCAM_TEMPLATES, 1):
        filename = SCAMS_DIR / f"indian_scam_{i:02d}.png"
        create_message_image(template, filename, is_scam=True)
    print(f"✓ Created {len(SCAM_TEMPLATES)} scam images")
    
    print(f"\nCreating {len(LEGIT_TEMPLATES)} legitimate test images...")
    for i, template in enumerate(LEGIT_TEMPLATES, 1):
        filename = LEGIT_DIR / f"indian_legit_{i:02d}.png"
        create_message_image(template, filename, is_scam=False)
    print(f"✓ Created {len(LEGIT_TEMPLATES)} legitimate images")
    
    print()
    print("=" * 70)
    print("DATASET READY")
    print("=" * 70)
    print(f"Total: {len(SCAM_TEMPLATES)} scams + {len(LEGIT_TEMPLATES)} legitimate")
    print()
    print("Run tests:")
    print("  python tests/run_tests.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
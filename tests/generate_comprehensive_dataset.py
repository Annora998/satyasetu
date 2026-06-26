"""
Generate comprehensive test dataset for SatyaSetu.
90 scam messages (10 per category) + 60 legitimate = 150 total test cases.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

TESTS_DIR = Path(__file__).parent
SCAMS_DIR = TESTS_DIR / "scams"
LEGIT_DIR = TESTS_DIR / "legit"

# Clear existing test images
for f in SCAMS_DIR.glob("*.png"): f.unlink()
for f in LEGIT_DIR.glob("*.png"): f.unlink()

# =====================================================================
# 90 SCAM TEMPLATES (10 per Category)
# =====================================================================
SCAM_TEMPLATES = [
    # ========== 1. KYC SCAMS (10) ==========
    "Dear customer, your KYC is pending. Update now to avoid account closure. Click: hdfc-kyc-update.com/verify",
    "Your SBI account will be blocked today. Update PAN details: sbi-pan-update.in/urgent",
    "ICICI Bank: Your KYC has expired. Update immediately: icici-kyc-verify.com",
    "ALERT: KYC update required within 24 hours. Verify: kyc-update-urgent.in",
    "Your KYC verification failed. Complete now: bank-kyc-verify.net/complete",
    "RBI mandate: Update KYC by today. Click: rbi-kyc-mandate.com/update",
    "Your account KYC is incomplete. Update PAN: pan-kyc-update.xyz",
    "KYC reminder: Update before account freeze. Verify: kyc-reminder.in",
    "Your KYC documents rejected. Resubmit: kyc-resubmit.cc/upload",
    "Final KYC notice: Account will be suspended. Update: final-kyc-notice.com",
    
    # ========== 2. BANKING/PHISHING SCAMS (10) ==========
    "ALERT: Suspicious transaction of Rs.25,000 detected. Verify immediately: sbi-secure-login.net/check",
    "ICICI Bank: Your account is locked. Verify identity: icici-verify.com/login",
    "Your HDFC credit card statement is ready. View: hdfc-statement-view.com/login",
    "Axis Bank: OTP is 847291. Never share. Verify: axis-otp-verify.net",
    "Bank Alert: Login from new device. Verify: hdfc-secure.net/verify",
    "Account suspended. Reactivate: icici-reactivate.com/login",
    "Transaction failed. Update details: sbi-update.net/verify",
    "Card blocked. Verify now: hdfc-card-verify.com",
    "Account locked. Unlock: axis-unlock.net",
    "Account alert. Verify: bank-verify.in",
    
    # ========== 3. COURIER/CUSTOMS SCAMS (10) ==========
    "Customs Department: Your package is held. Pay duty Rs.500: customs-duty.cc/pay",
    "Courier: Package stuck at customs. Pay Rs.750: fedex-customs.cc/pay",
    "Your parcel from USA is held at Delhi customs. Pay duty: customs-hold.in/pay",
    "DHL: Import duty pending for your package. Pay Rs.1,200: dhl-duty.cc",
    "BlueDart: Your shipment requires customs clearance. Pay: bluedart-customs.net",
    "India Post: International package held. Pay customs fee: indiapost-customs.xyz",
    "Your courier package is stuck. Clear customs: courier-stuck.cc/clear",
    "Customs notice: Pay import duty for your parcel. Click: customs-notice.in/pay",
    "FedEx: Your package delivery failed. Reschedule: fedex-reschedule.cc",
    "DTDC: Package held at sorting facility. Pay clearance fee: dtdc-clear.xyz",
    
    # ========== 4. REWARD/CASHBACK SCAMS (10) ==========
    "Congratulations! You won Rs.50,000 cashback. Claim now: paytm-reward.xyz/claim",
    "PhonePe: Rs.2,000 cashback credited. Scan to withdraw: phonepe-cashback.xyz",
    "Amazon Pay: Rs.500 reward. Click to claim: amazon-reward.xyz/claim",
    "Flipkart: You've won a gift card worth Rs.5,000. Claim: flipkart-gift.xyz",
    "Google Pay: Cashback of Rs.1,000 pending. Claim now: gpay-cashback.cc",
    "Payment of Rs.15,000 received. Scan QR to confirm: [UPI_QR_CODE]",
    "Your account credited Rs.45,000. Scan QR to pay: [MALICIOUS_QR]",
    "Cashback earned Rs.1,000. Scan to claim: [QR_CODE]",
    "Refund pending Rs.5,000. Claim: refund-claim.cc",
    "Payment received Rs.30,000. Confirm: [QR]",
    
    # ========== 5. GOVERNMENT IMPERSONATION (10) ==========
    "Income Tax: Refund of Rs.12,500 pending. Claim: incometax-refund.cc/claim",
    "EPFO: Your PF withdrawal approved. Verify: epfo-claim.in/verify",
    "Your PAN is not linked. Update now: pan-link-update.com/urgent",
    "PAN update required. Click: pan-update.xyz",
    "Income Tax Department: File ITR now to avoid penalty. File: itr-file-now.cc",
    "EPFO: Your UAN is not verified. Verify: uan-verify-epfo.in",
    "Government subsidy pending. Claim now: govt-subsidy-claim.xyz",
    "Aadhaar verification failed. Update: aadhaar-verify-urgent.in",
    "Ration card update required. Click: ration-card-update.cc",
    "Voter ID verification pending. Verify: voter-id-verify.xyz",
    
    # ========== 6. E-CHALLAN SCAMS (10) ==========
    "Traffic Police: Your challan of Rs.2,000 is pending. Pay: e-challan-pay.cc",
    "Traffic fine: Rs.5,000 for signal jumping. Pay now: traffic-challan.in/pay",
    "Your vehicle challan is overdue. Pay immediately: vehicle-challan.cc",
    "RTO notice: Traffic violation fine pending. Pay: rto-fine-notice.xyz",
    "E-challan: Rs.1,500 fine for no helmet. Pay: e-challan-helmet.in",
    "Delhi Traffic Police: Challan for overspeeding. Pay Rs.3,000: delhi-challan.cc",
    "Mumbai Police: Traffic violation detected. Pay fine: mumbai-traffic.xyz",
    "Your driving license suspended due to pending challan. Pay: dl-suspended.in",
    "Vehicle RC renewal blocked. Clear challan: rc-renewal.cc/pay",
    "E-challan notice: Rs.2,500 for wrong parking. Pay: parking-challan.xyz",
    
    # ========== 7. ELECTRICITY/UTILITY SCAMS (10) ==========
    "Electricity board: Your bill overdue. Disconnection today. Pay: electricity-bill.cc",
    "Power cut notice: Pay outstanding bill immediately: power-cut-notice.in",
    "Your electricity connection will be disconnected. Pay now: electricity-disconnect.xyz",
    "Gas bill overdue: Pay Rs.3,500 to avoid disconnection: gas-bill-pay.cc",
    "Water bill pending: Pay immediately or connection cut: water-bill-urgent.in",
    "BSNL: Your telephone bill overdue. Pay Rs.2,000: bsnl-bill.cc",
    "MTNL: Broadband bill pending. Pay now: mtnl-broadbill.xyz",
    "Your prepaid mobile will be disconnected. Recharge: mobile-recharge-urgent.in",
    "DTH connection blocked. Pay outstanding: dth-blocked.cc/pay",
    "Pipeline gas connection suspended. Pay bill: gas-suspended.xyz",
    
    # ========== 8. JOB SCAMS (10) ==========
    "Work from home opportunity! Earn Rs.50,000/month. Register: wfh-job.xyz",
    "Data entry job: Earn Rs.30,000 weekly. Apply now: dataentry-job.cc",
    "Part-time job: Rs.2,000 daily. No experience needed. Join: parttime-job.in",
    "Online typing job: Earn Rs.15,000/week. Apply: typing-job-urgent.xyz",
    "Amazon hiring: Work from home. Salary Rs.40,000. Apply: amazon-job-fake.cc",
    "Flipkart job opening: Earn Rs.35,000. Register: flipkart-job-scam.in",
    "Government job vacancy: Apply now. Fee Rs.500: govt-job-fake.xyz",
    "Bank job recruitment: Apply online. Pay fee: bank-job-scam.cc",
    "Telecalling job: Earn Rs.25,000/month. Join: telecall-job.xyz",
    "Freelance writing job: Rs.5,000 per article. Apply: writing-job-fake.in",
    
    # ========== 9. LOTTERY SCAMS (10) ==========
    "Lottery: You won Rs.1,00,000! Contact: +91-9876543210",
    "Congratulations! You won a lucky draw prize of Rs.25,000. Claim: lucky-draw-win.in",
    "You've won Rs.5,00,000 in our international lottery. Claim: intl-lottery.cc",
    "Dear winner, you've won Rs.10,00,000. Contact agent: lottery-agent.xyz",
    "Mega lottery winner! Prize Rs.50,00,000. Claim now: mega-lottery.in",
    "You are selected for Rs.2,00,000 prize. Verify: prize-verify.cc",
    "Lottery result: Your ticket won Rs.75,000. Claim: lottery-claim.xyz",
    "You won a car worth Rs.15,00,000! Pay tax to claim: car-lottery.in",
    "International lottery: You won $10,000. Claim: us-lottery-claim.cc",
    "Lucky winner! You won Rs.3,00,000. Contact: lottery-winner.xyz",
]

# =====================================================================
# 60 LEGITIMATE TEMPLATES (Diverse Categories)
# =====================================================================
LEGIT_TEMPLATES = [
    # ========== CREDIT CARD STATEMENTS (15) ==========
    "Dear Customer, your HDFC Bank Credit Card statement for XX is ready. Total amount Rs.35,201 due by 10-FEB.",
    "Dear Customer, your credit card bill of Rs.15,000 is due on 25-Jun. Pay to avoid interest.",
    "Dear Customer, minimum amount due on your card is Rs.1,500. Due date: 20-Jun.",
    "Dear Customer, your total credit card balance is Rs.25,000. Pay by 25-Jun to avoid charges.",
    "Your ICICI Bank credit card statement is ready. Login to view details. -ICICI Bank",
    "SBI Card: Your statement for May 2024 is ready. Total due: Rs.18,500. Due date: 15-Jun.",
    "Axis Bank: Credit card bill generated. Amount: Rs.22,000. Pay by 10-Jul.",
    "Your HDFC Diners Club statement is ready. View at hdfcbank.com.",
    "ICICI Coral Card: Statement ready. Amount due: Rs.8,750. Due: 25-Jun.",
    "Your SBI Card statement is ready. Login to SBI Card app to view.",
    "HDFC: Your credit card EMI of Rs.5,000 is due on 15-Jul.",
    "Axis: Credit card reward points: 12,500 points. Redeem at axisbank.com.",
    "ICICI: Your card limit enhanced to Rs.2,00,000. View details online.",
    "SBI: Cashback of Rs.500 credited to your credit card. Statement: hdfcbank.com.",
    "Your credit card payment of Rs.10,000 received on 15-Jun. Thank you.",
    
    # ========== TRANSACTION ALERTS (25) ==========
    "A/c XX6844 credited Rs.33,270 on 08-08-2021. Available balance Rs.45,890. -HDFC Bank",
    "Rs.500 debited from A/c XX1234 on 15-06-2024 at AMAZON. Bal Rs.12,500. -SBI",
    "Transaction alert: Rs.1,200 paid to ELECTRICITY BOARD. A/c XX5678. -Axis Bank",
    "Rs.25,000 received in A/c XX9012 from JOHN DOE on 18-06-2024. -HDFC Bank",
    "SBI: Online transaction of Rs.750 successful. Ref: 123456789. Bal Rs.8,250.",
    "Your A/c XX3456 has been debited Rs.2,500 for INSURANCE PREMIUM on 15-06-2024.",
    "Rs.10,000 transferred from A/c XX7890 to A/c XX1234 on 18-06-2024. -ICICI",
    "SBI: Card XX1234 used for Rs.450 at MCDONALDS on 18-06. Bal Rs.5,550.",
    "Rs.5,000 credited to A/c XX5678 via NEFT from ABC CORP on 17-06-2024.",
    "HDFC: UPI payment of Rs.200 to SWIGGY successful. Ref: 987654321.",
    "Axis: Rs.1,500 debited for MOBILE RECHARGE. Bal: Rs.23,500.",
    "ICICI: IMPS credit of Rs.8,000 received. Ref: 456789123.",
    "SBI: ATM withdrawal of Rs.5,000 from MG ROAD branch. Bal: Rs.15,000.",
    "HDFC: EMI of Rs.12,500 debited for HOME LOAN. Next EMI: 05-Aug.",
    "Your A/c XX9999 credited Rs.50,000 via RTGS from XYZ LTD on 19-06-2024.",
    "Axis: Standing instruction of Rs.3,000 executed for MUTUAL FUND SIP.",
    "ICICI: Dividend of Rs.2,500 credited to your account. Ref: DIV2024.",
    "SBI: Interest of Rs.1,200 credited to savings account. Bal: Rs.45,000.",
    "HDFC: Auto-debit of Rs.5,000 for INSURANCE PREMIUM successful.",
    "Your A/c XX7777 debited Rs.8,000 for CREDIT CARD BILL payment.",
    "Axis: NACH debit of Rs.2,000 for LOAN EMI processed successfully.",
    "ICICI: Cash deposit of Rs.15,000 at ATM. Available: Rs.25,000.",
    "SBI: Cheque deposit of Rs.50,000 cleared. Bal: Rs.75,000.",
    "HDFC: Forex card transaction of $100 at NEW YORK. Bal: $900.",
    "Your A/c XX8888 credited Rs.3,000 as CASHBACK for card usage.",
    
    # ========== EDUCATIONAL/SECURITY ALERTS (10) ==========
    "Your ICICI Bank statement is ready. Login to view. Never share OTP. -ICICI Bank",
    "HDFC Bank will never ask for OTP/PIN. Report suspicious calls to 1800-202-6161.",
    "HDFC: Your statement is ready. View at hdfcbank.com. Never share credentials.",
    "SBI Alert: Do not share OTP with anyone. Bank officials never ask for OTP.",
    "ICICI: Beware of phishing calls. Never click on links received via SMS.",
    "Axis Bank: Your OTP for login is 847291. Valid for 10 minutes. Never share.",
    "HDFC: New device login detected. If not you, call 1800-202-6161 immediately.",
    "SBI: Your password will expire in 7 days. Change at onlinesbi.com.",
    "ICICI: Suspicious login attempt blocked. If not you, call 1860-123-4567.",
    "HDFC: Your card has been blocked due to suspicious activity. Call to unblock.",
    
    # ========== ACCOUNT/FD/LOAN UPDATES (10) ==========
    "Your FD of Rs.1,00,000 will mature on 30-06-2024. Contact branch for renewal.",
    "Your loan EMI of Rs.15,500 is due on 05-07-2024. Ensure sufficient balance.",
    "Your debit card XX9012 will expire on 30-06-2024. Visit branch for renewal.",
    "Axis Bank: Fixed Deposit of Rs.50,000 matured. Principal + interest credited.",
    "Your savings account XX1111 has been credited with interest of Rs.2,500.",
    "HDFC: Your home loan outstanding is Rs.25,00,000. Next EMI: Rs.22,000 on 10-Jul.",
    "SBI: Your recurring deposit of Rs.5,000/month will mature on 31-Dec-2024.",
    "ICICI: Your car loan EMI of Rs.18,000 is due on 15-Jul. Auto-debit scheduled.",
    "Your account XX2222 minimum balance not maintained. Charges: Rs.500 debited.",
    "Axis: Your salary of Rs.75,000 credited on 01-07-2024. Available: Rs.75,000.",
]

def create_message_image(text, filename, is_scam=True):
    """Creates a realistic-looking message image."""
    width, height = 800, 400
    img = Image.new('RGB', (width, height), color='white')
    d = ImageDraw.Draw(img)
    
    try:
        font = ImageFont.truetype("arial.ttf", 20)
        label_font = ImageFont.truetype("arial.ttf", 14)
    except:
        font = ImageFont.load_default()
        label_font = font
    
    # Add header
    if is_scam:
        header_color = '#dc2626'  # Red
        header_text = "⚠️ SCAM MESSAGE (Test Data)"
    else:
        header_color = '#16a34a'  # Green
        header_text = "✓ LEGITIMATE MESSAGE (Test Data)"
    
    d.rectangle([(0, 0), (width, 40)], fill=header_color)
    d.text((20, 10), header_text, fill='white', font=label_font)
    
    # Add message content
    margin = 40
    current_height = 60
    
    # Word wrap
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
    
    # Draw each line
    for line in lines[:10]:
        d.text((margin, current_height), line, fill='black', font=font)
        current_height += 28
    
    # Add timestamp
    d.text((margin, height - 40), "Received: 18-06-2024 14:30", fill='gray', font=label_font)
    
    img.save(filename)

def main():
    print("=" * 70)
    print("GENERATING COMPREHENSIVE TEST DATASET (150 CASES)")
    print("=" * 70)
    print()
    
    print(f"Creating {len(SCAM_TEMPLATES)} scam test images...")
    for i, template in enumerate(SCAM_TEMPLATES, 1):
        filename = SCAMS_DIR / f"comprehensive_scam_{i:02d}.png"
        create_message_image(template, filename, is_scam=True)
    print(f"✓ Created {len(SCAM_TEMPLATES)} scam images")
    
    print(f"\nCreating {len(LEGIT_TEMPLATES)} legitimate test images...")
    for i, template in enumerate(LEGIT_TEMPLATES, 1):
        filename = LEGIT_DIR / f"comprehensive_legit_{i:02d}.png"
        create_message_image(template, filename, is_scam=False)
    print(f"✓ Created {len(LEGIT_TEMPLATES)} legitimate images")
    
    print()
    print("=" * 70)
    print("COMPREHENSIVE DATASET READY")
    print("=" * 70)
    print(f"Total: {len(SCAM_TEMPLATES)} scams + {len(LEGIT_TEMPLATES)} legitimate = 150 cases")
    print()
    print("Scam Categories (10 each):")
    print("  1. KYC Scams")
    print("  2. Banking/Phishing Scams")
    print("  3. Courier/Customs Scams")
    print("  4. Reward/Cashback Scams")
    print("  5. Government Impersonation")
    print("  6. E-Challan Scams")
    print("  7. Electricity/Utility Scams")
    print("  8. Job Scams")
    print("  9. Lottery Scams")
    print()
    print("Legitimate Categories:")
    print("  - Credit Card Statements: 15")
    print("  - Transaction Alerts: 25")
    print("  - Educational/Security: 10")
    print("  - Account/FD/Loan: 10")
    print()
    print("Run tests:")
    print("  python tests/run_tests.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
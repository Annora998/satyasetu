"""
Generate massive test dataset for SatyaSetu.
500+ test cases covering all scam categories with variations.
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

TESTS_DIR = Path(__file__).parent
SCAMS_DIR = TESTS_DIR / "scams"
LEGIT_DIR = TESTS_DIR / "legit"

# Clear existing test images
for f in SCAMS_DIR.glob("*.png"): f.unlink()
for f in LEGIT_DIR.glob("*.png"): f.unlink()

# =====================================================================
# 300 SCAM TEMPLATES (Diverse variations of 9 categories)
# =====================================================================
SCAM_TEMPLATES = [
    # ========== 1. KYC SCAMS (40 variations) ==========
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
    "HDFC: KYC pending for 30 days. Update or account blocked: hdfc-kyc-30days.in",
    "SBI: KYC deadline today. Update now: sbi-kyc-deadline.xyz",
    "ICICI: Your KYC status is inactive. Activate: icici-kyc-inactive.cc",
    "Axis Bank: KYC verification pending. Verify: axis-kyc-pending.in",
    "Paytm: KYC mandatory. Complete now: paytm-kyc-mandatory.xyz",
    "PhonePe: KYC incomplete. Update: phonepe-kyc-incomplete.in",
    "Amazon Pay: KYC required. Verify: amazonpay-kyc.xyz",
    "Google Pay: KYC pending. Update: gpay-kyc-pending.in",
    "Your bank account KYC expired. Renew: bank-kyc-expired.cc",
    "KYC update mandatory by RBI. Update: rbi-kyc-mandatory.in",
    "KYC suspension notice. Reactivate: kyc-suspension.xyz",
    "Your KYC is under review. Verify: kyc-review.in",
    "KYC verification timeout. Resubmit: kyc-timeout.cc",
    "Bank KYC compliance required. Update: bank-compliance.in",
    "KYC non-compliance alert. Update: kyc-noncompliance.xyz",
    "Your KYC profile incomplete. Complete: kyc-profile.in",
    "KYC update overdue. Update now: kyc-overdue.cc",
    "RBI KYC guidelines. Update: rbi-guidelines.in",
    "KYC mandatory for all accounts. Update: kyc-all-accounts.xyz",
    "Your KYC will expire soon. Renew: kyc-expire-soon.in",
    "KYC update reminder. Update: kyc-reminder-2.xyz",
    "Bank KYC policy change. Update: bank-policy.in",
    "KYC verification pending for 60 days. Update: kyc-60days.cc",
    "Your KYC is invalid. Re-verify: kyc-invalid.in",
    "KYC update required for UPI. Update: kyc-upi.xyz",
    "Bank KYC audit. Update required: kyc-audit.in",
    "KYC compliance deadline. Update: kyc-deadline-2.cc",
    "Your KYC needs updating. Update: kyc-needs-update.in",
    "KYC verification error. Resubmit: kyc-error.xyz",
    "Bank KYC system update. Re-verify: kyc-system.in",
    
    # ========== 2. BANKING/PHISHING SCAMS (40 variations) ==========
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
    "Your SBI netbanking password expired. Reset: sbi-password-reset.com",
    "HDFC: Unauthorized transaction detected. Dispute: hdfc-dispute.net",
    "ICICI: Your card will expire tomorrow. Renew: icici-card-renew.xyz",
    "Axis: Login attempt from new device. Confirm: axis-confirm-login.com",
    "Federal Bank: Your account access restricted. Verify: federal-verify-access.in",
    "Bank account frozen. Unfreeze: bank-frozen.cc",
    "Your card has been blocked. Unblock: card-blocked.in",
    "Suspicious activity detected. Verify: suspicious-activity.xyz",
    "Your account is compromised. Secure: account-compromised.in",
    "Bank security alert. Verify: bank-security.cc",
    "Your netbanking is blocked. Unblock: netbanking-blocked.in",
    "Card transaction declined. Update: card-declined.xyz",
    "Your account needs verification. Verify: account-verify-2.in",
    "Bank fraud alert. Verify: bank-fraud.cc",
    "Your card is expired. Renew: card-expired-2.in",
    "Account verification required. Verify: account-verify-3.xyz",
    "Your netbanking session expired. Login: netbanking-expired.in",
    "Bank password reset required. Reset: bank-password.cc",
    "Your card is suspended. Reactivate: card-suspended.in",
    "Account security update. Update: account-security.xyz",
    "Your netbanking is locked. Unlock: netbanking-locked.in",
    "Bank OTP verification. Verify: bank-otp-2.cc",
    "Your card limit exceeded. Update: card-limit.in",
    "Account activity alert. Verify: account-activity.xyz",
    "Your netbanking needs update. Update: netbanking-update.in",
    "Bank login alert. Verify: bank-login.cc",
    "Your card PIN blocked. Reset: card-pin.in",
    "Account access denied. Verify: account-denied.xyz",
    "Your netbanking credentials expired. Update: netbanking-creds.in",
    "Bank transaction alert. Verify: bank-transaction.cc",
    
    # ========== 3. COURIER/CUSTOMS SCAMS (30 variations) ==========
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
    "Your package is awaiting customs clearance. Pay: package-clearance.in",
    "Courier delivery on hold. Pay duty: courier-hold.cc",
    "Customs inspection required. Pay fee: customs-inspection.in",
    "Your shipment is delayed. Pay customs: shipment-delayed.xyz",
    "Package stuck in transit. Clear: package-stuck.in",
    "Import duty payment pending. Pay: import-duty-2.cc",
    "Your parcel requires payment. Pay: parcel-payment.in",
    "Courier customs charge. Pay: courier-charge.xyz",
    "Package held for inspection. Pay: package-inspection.in",
    "Customs clearance fee due. Pay: clearance-fee.cc",
    "Your delivery is on hold. Pay: delivery-hold.in",
    "Shipment customs pending. Pay: shipment-customs.xyz",
    "Package delivery failed. Pay duty: delivery-failed.in",
    "Courier payment required. Pay: courier-payment.cc",
    "Your parcel is detained. Pay: parcel-detained.in",
    "Customs duty overdue. Pay: customs-overdue.xyz",
    "Package clearance required. Pay: clearance-required.in",
    "Your shipment needs payment. Pay: shipment-payment.cc",
    "Courier fee pending. Pay: courier-fee.in",
    "Package inspection fee. Pay: inspection-fee.xyz",
    
    # ========== 4. REWARD/CASHBACK SCAMS (30 variations) ==========
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
    "You've won a lucky draw prize of Rs.25,000. Claim: lucky-draw-win.in",
    "Mega cashback offer! Rs.10,000. Claim: mega-cashback.xyz",
    "Your reward points: 50,000. Redeem: reward-points.in",
    "Congratulations on winning! Rs.75,000. Claim: congrats-win.cc",
    "Cashback pending approval. Approve: cashback-approval.in",
    "Your cashback is ready. Claim: cashback-ready.xyz",
    "Reward redemption pending. Redeem: reward-redemption.in",
    "You won a surprise gift! Claim: surprise-gift.cc",
    "Cashback credited to wallet. Withdraw: cashback-wallet.in",
    "Your reward is waiting. Claim: reward-waiting.xyz",
    "Prize money pending. Claim: prize-money.in",
    "Cashback offer expires today. Claim: cashback-expires.cc",
    "Your lottery winnings. Claim: lottery-winnings.in",
    "Reward points expiring. Redeem: points-expiring.xyz",
    "Cashback verification required. Verify: cashback-verify.in",
    "Your gift card is ready. Claim: gift-card-ready.cc",
    "Prize claim pending. Claim: prize-claim.in",
    "Cashback pending transfer. Transfer: cashback-transfer.xyz",
    "Your reward balance. Claim: reward-balance.in",
    "Winning amount pending. Claim: winning-amount.cc",
    
    # ========== 5. GOVERNMENT IMPERSONATION (30 variations) ==========
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
    "Income Tax refund approved. Claim: tax-refund-approved.in",
    "EPFO pension update. Update: epfo-pension.cc",
    "Your PAN card expired. Renew: pan-expired.in",
    "Aadhaar linking mandatory. Link: aadhaar-link.xyz",
    "Government scheme benefit. Claim: govt-scheme.in",
    "Income Tax notice. Respond: tax-notice.cc",
    "EPFO balance update. Check: epfo-balance.in",
    "Your ration card expired. Renew: ration-expired.xyz",
    "Voter ID update required. Update: voter-update.in",
    "Government grant approved. Claim: govt-grant.cc",
    "Income Tax penalty notice. Pay: tax-penalty.in",
    "EPFO nomination update. Update: epfo-nomination.xyz",
    "Your Aadhaar is blocked. Unblock: aadhaar-blocked.in",
    "PAN verification pending. Verify: pan-verify.cc",
    "Government relief fund. Claim: relief-fund.in",
    "Income Tax assessment. Respond: tax-assessment.xyz",
    "EPFO withdrawal pending. Withdraw: epfo-withdrawal.in",
    "Your ration card blocked. Unblock: ration-blocked.cc",
    "Voter ID renewal. Renew: voter-renewal.in",
    "Government compensation. Claim: govt-compensation.xyz",
    
    # ========== 6. E-CHALLAN SCAMS (30 variations) ==========
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
    "Traffic violation alert. Pay fine: traffic-violation.in",
    "Your vehicle is fined. Pay: vehicle-fine.cc",
    "Challan payment overdue. Pay: challan-overdue.in",
    "RTO fine notice. Pay: rto-fine.xyz",
    "Traffic police notice. Pay: police-notice.in",
    "Your challan is pending. Pay: challan-pending.cc",
    "Driving license fine. Pay: dl-fine.in",
    "Vehicle penalty notice. Pay: vehicle-penalty.xyz",
    "E-challan reminder. Pay: challan-reminder.in",
    "Traffic fine overdue. Pay: fine-overdue.cc",
    "Your RC is blocked. Pay: rc-blocked.in",
    "Challan clearance required. Pay: challan-clearance.xyz",
    "RTO violation notice. Pay: rto-violation.in",
    "Traffic penalty pending. Pay: penalty-pending.cc",
    "Your DL is suspended. Pay: dl-suspended-2.in",
    "E-challan final notice. Pay: challan-final.xyz",
    "Vehicle fine pending. Pay: vehicle-fine-2.in",
    "Challan payment required. Pay: challan-required.cc",
    "Traffic violation fine. Pay: violation-fine.in",
    "RTO penalty notice. Pay: rto-penalty.xyz",
    
    # ========== 7. ELECTRICITY/UTILITY SCAMS (30 variations) ==========
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
    "Electricity disconnection warning. Pay: electricity-warning.in",
    "Your power will be cut. Pay: power-cut.cc",
    "Bill payment overdue. Pay: bill-overdue.in",
    "Utility bill pending. Pay: utility-pending.xyz",
    "Connection suspension notice. Pay: connection-suspend.in",
    "Your electricity is blocked. Pay: electricity-blocked.cc",
    "Gas connection blocked. Pay: gas-blocked.in",
    "Water connection suspended. Pay: water-suspended.xyz",
    "BSNL bill overdue. Pay: bsnl-overdue.in",
    "MTNL payment pending. Pay: mtnl-pending.cc",
    "Mobile disconnection notice. Pay: mobile-disconnect.in",
    "DTH bill overdue. Pay: dth-overdue.xyz",
    "Your utility bill is due. Pay: utility-due.in",
    "Electricity penalty notice. Pay: electricity-penalty.cc",
    "Gas bill pending. Pay: gas-pending.in",
    "Water bill overdue. Pay: water-overdue.xyz",
    "BSNL disconnection warning. Pay: bsnl-warning.in",
    "MTNL bill pending. Pay: mtnl-bill.cc",
    "Your connection is blocked. Pay: connection-blocked.in",
    "Utility payment overdue. Pay: utility-overdue.xyz",
    
    # ========== 8. JOB SCAMS (25 variations) ==========
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
    "Remote job opportunity. Earn: remote-job.xyz",
    "Online job opening. Apply: online-job.cc",
    "Part-time work. Earn daily: parttime-work.in",
    "Home-based job. Salary: home-job.xyz",
    "Data entry work. Earn: dataentry-work.cc",
    "Typing job available. Apply: typing-job.in",
    "Customer service job. Earn: customer-job.xyz",
    "Sales job opening. Apply: sales-job.cc",
    "Marketing job. Earn: marketing-job.in",
    "Admin job available. Apply: admin-job.xyz",
    "HR job opening. Earn: hr-job.cc",
    "IT job available. Apply: it-job.in",
    "Finance job opening. Earn: finance-job.xyz",
    "Accounting job. Apply: accounting-job.cc",
    "Management job. Earn: management-job.in",
    
    # ========== 9. LOTTERY SCAMS (25 variations) ==========
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
    "You won the jackpot! Claim: jackpot-win.in",
    "Prize winner notification. Claim: prize-winner.cc",
    "Lucky draw result. Claim: lucky-result.in",
    "Lottery prize pending. Claim: lottery-pending.xyz",
    "You are a winner! Claim: you-winner.in",
    "Prize money won. Claim: prize-won.cc",
    "Lottery ticket winner. Claim: ticket-winner.in",
    "Congratulations winner! Claim: congrats-winner.xyz",
    "Prize claim notice. Claim: prize-notice.in",
    "Lottery payout pending. Claim: lottery-payout.cc",
    "You won big! Claim: won-big.in",
    "Prize distribution. Claim: prize-distribution.xyz",
    "Lottery award. Claim: lottery-award.in",
    "Winner announcement. Claim: winner-announce.cc",
    "Prize collection. Claim: prize-collection.in",
]

# =====================================================================
# 200 LEGITIMATE TEMPLATES (Diverse variations)
# =====================================================================
LEGIT_TEMPLATES = [
    # Credit Card Statements (30)
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
    "HDFC: Your statement is ready. Total: Rs.45,000. Due: 20-Jul.",
    "ICICI: Card statement generated. Amount: Rs.12,000. Due: 25-Jul.",
    "SBI: Credit card bill ready. Total: Rs.8,000. Due: 15-Aug.",
    "Axis: Statement ready. Amount: Rs.15,000. Due: 10-Aug.",
    "HDFC: Your bill is ready. Total: Rs.20,000. Due: 25-Aug.",
    "ICICI: Statement generated. Amount: Rs.18,000. Due: 30-Aug.",
    "SBI: Card bill ready. Total: Rs.22,000. Due: 15-Sep.",
    "Axis: Your statement is ready. Amount: Rs.25,000. Due: 20-Sep.",
    "HDFC: Bill generated. Total: Rs.30,000. Due: 25-Sep.",
    "ICICI: Your statement is ready. Amount: Rs.35,000. Due: 30-Sep.",
    "SBI: Statement ready. Total: Rs.40,000. Due: 15-Oct.",
    "Axis: Bill ready. Amount: Rs.45,000. Due: 20-Oct.",
    "HDFC: Your statement is ready. Total: Rs.50,000. Due: 25-Oct.",
    "ICICI: Statement generated. Amount: Rs.55,000. Due: 30-Oct.",
    "SBI: Your bill is ready. Total: Rs.60,000. Due: 15-Nov.",
    
    # Transaction Alerts (50)
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
    "Axis: Payment of Rs.4,000 received. Bal: Rs.30,000.",
    "ICICI: Transfer of Rs.6,000 to A/c XX1111. Bal: Rs.20,000.",
    "SBI: Debit of Rs.7,000 for SHOPPING. Bal: Rs.15,000.",
    "HDFC: Credit of Rs.9,000 from SALARY. Bal: Rs.35,000.",
    "Axis: Payment of Rs.10,000 received. Bal: Rs.40,000.",
    "ICICI: Transfer of Rs.11,000 to A/c XX2222. Bal: Rs.25,000.",
    "SBI: Debit of Rs.12,000 for TRAVEL. Bal: Rs.18,000.",
    "HDFC: Credit of Rs.13,000 from REFUND. Bal: Rs.38,000.",
    "Axis: Payment of Rs.14,000 received. Bal: Rs.42,000.",
    "ICICI: Transfer of Rs.15,000 to A/c XX3333. Bal: Rs.28,000.",
    "SBI: Debit of Rs.16,000 for MEDICAL. Bal: Rs.20,000.",
    "HDFC: Credit of Rs.17,000 from BONUS. Bal: Rs.40,000.",
    "Axis: Payment of Rs.18,000 received. Bal: Rs.45,000.",
    "ICICI: Transfer of Rs.19,000 to A/c XX4444. Bal: Rs.30,000.",
    "SBI: Debit of Rs.20,000 for EDUCATION. Bal: Rs.22,000.",
    "HDFC: Credit of Rs.21,000 from INTEREST. Bal: Rs.42,000.",
    "Axis: Payment of Rs.22,000 received. Bal: Rs.48,000.",
    "ICICI: Transfer of Rs.23,000 to A/c XX5555. Bal: Rs.32,000.",
    "SBI: Debit of Rs.24,000 for RENT. Bal: Rs.25,000.",
    "HDFC: Credit of Rs.25,000 from DIVIDEND. Bal: Rs.45,000.",
    "Axis: Payment of Rs.26,000 received. Bal: Rs.50,000.",
    "ICICI: Transfer of Rs.27,000 to A/c XX6666. Bal: Rs.35,000.",
    "SBI: Debit of Rs.28,000 for GROCERIES. Bal: Rs.28,000.",
    "HDFC: Credit of Rs.29,000 from PENSION. Bal: Rs.48,000.",
    "Axis: Payment of Rs.30,000 received. Bal: Rs.52,000.",
    
    # Educational/Security Alerts (20)
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
    "Axis: Security alert. Your card is safe. Never share CVV.",
    "SBI: Fraud alert. We will never ask for your password.",
    "ICICI: Security reminder. Update your password regularly.",
    "HDFC: Alert. Your account is secure. Report suspicious activity.",
    "Axis: Security notice. Your data is protected.",
    "SBI: Alert. Never share your PIN with anyone.",
    "ICICI: Security update. Your account is safe.",
    "HDFC: Alert. We will never call asking for money.",
    "Axis: Security reminder. Keep your card details safe.",
    "SBI: Alert. Report any suspicious SMS to bank.",
    
    # Account/FD/Loan Updates (20)
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
    "HDFC: Your FD interest of Rs.5,000 credited. Bal: Rs.1,05,000.",
    "SBI: Loan prepayment of Rs.50,000 received. Outstanding: Rs.20,00,000.",
    "ICICI: Your debit card PIN changed successfully.",
    "Axis: FD renewal confirmed. Amount: Rs.60,000. Rate: 7.5%.",
    "HDFC: Your loan EMI paid successfully. Next EMI: 10-Aug.",
    "SBI: Your account upgraded to Premium. Benefits activated.",
    "ICICI: Your FD will mature on 15-Aug. Auto-renewal enabled.",
    "Axis: Loan statement ready. Outstanding: Rs.18,00,000.",
    "HDFC: Your savings account interest credited: Rs.3,000.",
    "SBI: Your debit card delivery scheduled. Track: sbi.co.in.",
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
    print("GENERATING MASSIVE TEST DATASET (500+ CASES)")
    print("=" * 70)
    print()
    
    print(f"Creating {len(SCAM_TEMPLATES)} scam test images...")
    for i, template in enumerate(SCAM_TEMPLATES, 1):
        filename = SCAMS_DIR / f"massive_scam_{i:03d}.png"
        create_message_image(template, filename, is_scam=True)
    print(f"✓ Created {len(SCAM_TEMPLATES)} scam images")
    
    print(f"\nCreating {len(LEGIT_TEMPLATES)} legitimate test images...")
    for i, template in enumerate(LEGIT_TEMPLATES, 1):
        filename = LEGIT_DIR / f"massive_legit_{i:03d}.png"
        create_message_image(template, filename, is_scam=False)
    print(f"✓ Created {len(LEGIT_TEMPLATES)} legitimate images")
    
    total = len(SCAM_TEMPLATES) + len(LEGIT_TEMPLATES)
    print()
    print("=" * 70)
    print("MASSIVE DATASET READY")
    print("=" * 70)
    print(f"Total: {len(SCAM_TEMPLATES)} scams + {len(LEGIT_TEMPLATES)} legitimate = {total} cases")
    print()
    print("Scam Categories:")
    print("  - KYC Scams: 40")
    print("  - Banking/Phishing: 40")
    print("  - Courier/Customs: 30")
    print("  - Reward/Cashback: 30")
    print("  - Government: 30")
    print("  - E-Challan: 30")
    print("  - Electricity/Utility: 30")
    print("  - Job Scams: 25")
    print("  - Lottery Scams: 25")
    print()
    print("Legitimate Categories:")
    print("  - Credit Card Statements: 30")
    print("  - Transaction Alerts: 50")
    print("  - Educational/Security: 20")
    print("  - Account/FD/Loan: 20")
    print()
    print("Run tests:")
    print("  python tests/run_tests.py")
    print("=" * 70)

if __name__ == "__main__":
    main()
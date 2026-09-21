import sys
from pathlib import Path


# Path to the original hackathon bundle
BUNDLE_PATH = Path(
    r"C:\Users\wjwei\averis-hackathon-2026\sdoc-hackathon-bundle"
)

# Import loader.py directly from the bundle without modifying it
sys.path.append(str(BUNDLE_PATH))

from loader import Inbox


# Email categories
BL_COMPARISON = "BL_COMPARISON"
SI_REQUEST = "SI_REQUEST"
INVOICE_QUERY = "INVOICE_QUERY"
GENERAL = "GENERAL"
SPAM = "SPAM"


def classify_email(email):
    """Classify an email into one of the five challenge categories."""

    subject = email.get("subject", "").lower()
    body = email.get("body", "").lower()

    # Keep subject and body since the subject isn't always reliable
    text = subject + "\n" + body

    # --------------------------------------------------
    # Spam
    # --------------------------------------------------

    spam_keywords = [
        "click here",
        "claim your prize",
        "you have won",
        "winner",
        "free money",
        "lottery",
        "casino",
        "crypto investment",
        "limited time offer",
        "earn money fast",
    ]

    spam_score = sum(keyword in text for keyword in spam_keywords)

    if spam_score >= 2:
        return SPAM

    # --------------------------------------------------
    # BL comparison
    # --------------------------------------------------

    bl_terms = [
        "draft bl",
        "draft bill of lading",
        "bill of lading",
    ]

    comparison_terms = [
        "check",
        "compare",
        "verify",
        "review",
        "confirm",
        "validate",
        "cross-check",
        "cross check",
        "discrepancy",
        "discrepancies",
    ]

    si_terms = [
        "shipping instruction",
        "shipping instructions",
        " si ",
    ]

    has_bl = any(term in text for term in bl_terms)
    has_comparison = any(term in text for term in comparison_terms)
    has_si = any(term in text for term in si_terms)

    # BL + check/review/verify usually means they want a comparison
    if has_bl and has_comparison:
        return BL_COMPARISON

    # Attached BL and SI together is another strong hint
    if has_bl and has_si and "attached" in text:
        return BL_COMPARISON

    # --------------------------------------------------
    # SI request
    # --------------------------------------------------

    si_request_phrases = [
        "prepare the si",
        "prepare si",
        "prepare shipping instruction",
        "prepare shipping instructions",

        "send the si",
        "send si",
        "send shipping instruction",
        "send shipping instructions",

        "submit the si",
        "submit si",
        "submit shipping instruction",
        "submit shipping instructions",

        "provide the si",
        "provide si",
        "provide shipping instruction",
        "provide shipping instructions",

        "need the si",
        "need si",
        "need shipping instruction",
        "need shipping instructions",

        "request for si",
        "request for shipping instruction",
        "request for shipping instructions",
    ]

    if any(phrase in text for phrase in si_request_phrases):
        return SI_REQUEST

    # --------------------------------------------------
    # Invoice query
    # --------------------------------------------------

    invoice_terms = [
        "invoice",
        "billing",
        "payment",
        "charged",
        "charge",
    ]

    invoice_query_terms = [
        "query",
        "question",
        "check",
        "clarify",
        "clarification",
        "incorrect",
        "wrong",
        "discrepancy",
        "why",
        "amount",
        "outstanding",
        "payment",
    ]

    has_invoice = any(term in text for term in invoice_terms)
    has_invoice_query = any(
        term in text for term in invoice_query_terms
    )

    if has_invoice and has_invoice_query:
        return INVOICE_QUERY

    # Anything else is treated as a normal operational email
    return GENERAL


def main():
    # Load emails from the original bundle
    inbox = Inbox(str(BUNDLE_PATH))
    emails = inbox.emails()

    print(f"\nLoaded {len(emails)} emails.\n")

    counts = {
        BL_COMPARISON: 0,
        SI_REQUEST: 0,
        INVOICE_QUERY: 0,
        GENERAL: 0,
        SPAM: 0,
    }

    # Classify each email
    for email in emails:
        category = classify_email(email)
        counts[category] += 1

        print(
            f"{email['email_id']:<12} "
            f"-> {category:<16} "
            f"| {email.get('subject', '')}"
        )

    # Print a quick summary so we can sanity-check the results
    print("\n" + "=" * 60)
    print("CLASSIFICATION SUMMARY")
    print("=" * 60)

    for category, count in counts.items():
        print(f"{category:<16}: {count}")

    print("=" * 60)
    print(f"{'TOTAL':<16}: {sum(counts.values())}")


if __name__ == "__main__":
    main()
import json
import sys
import os

sys.path.insert(0, "sdoc-hackathon-bundle")
from loader import Inbox
import classification

def run_pipeline():
    inbox = Inbox("sdoc-hackathon-bundle")
    submission = {}
    
    for email in inbox:
        eid = email['email_id']
        category = classification.classify_email(email)
        
        # We're only doing Part A, so we just stub the rest
        submission[eid] = {
            "category": category,
            "status": "OK",
            "review_reason": None,
            "has_defect": False,
            "defect_fields": []
        }
            
    with open("submission_a.json", "w") as f:
        json.dump(submission, f, indent=2)

if __name__ == "__main__":
    run_pipeline()

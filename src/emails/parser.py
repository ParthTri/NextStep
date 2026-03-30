import json
import re

import requests

from nextstep import models

KEYWORDS = {
    "Applied": [
        "application received",
        "thank you for applying",
        "successfully submitted",
        "received your application",
        "interest in joining",
        "application confirmation",
        "reviewing your resume",
        "application id",
        "thanks for your interest",
    ],
    "Interviewing": [
        "schedule a call",
        "interview invitation",
        "availability for a chat",
        "phone screen",
        "video interview",
        "technical assessment",
        "next steps",
        "zoom link",
        "google meet",
        "calendly",
        "hiring manager",
        "interview process",
    ],
    "Rejected": [
        "not moving forward",
        "pursue other candidates",
        "unfortunately",
        "not be proceeding",
        "position has been filled",
        "regret to inform",
        "decided to pass",
        "keep your resume on file",
        "other applicants",
        "best of luck",
    ],
    "Offer": [
        "offer letter",
        "congratulations",
        "official offer",
        "employment agreement",
        "onboarding",
        "welcome to the team",
        "compensation",
        "package details",
        "verbal offer",
        "sign the attached",
    ],
}


def construct_lookup_table(user) -> dict[int, re.Pattern]:
    applications = models.Application.objects.filter(user=user).exclude(
        tags__name__in=["Rejected", "Withdrawn"]
    )

    patterns = {}

    for application in applications:
        pattern = (
            f"\b({re.escape(application.role)})|({re.escape(application.company)})"
        )

        patterns[application.id] = re.compile(pattern, re.IGNORECASE)

    return patterns


def filter_emails(messages, table: dict[int, re.Pattern]):
    found_applications: dict[int, str] = {}

    for id, pattern in table.items():
        for message in messages:
            if pattern.search(message) is not None:
                found_applications[id] = message

    return found_applications


def classify_with_keywords(text):
    text = text.lower()
    scores = {category: 0 for category in KEYWORDS.keys()}

    for category, keywords in KEYWORDS.items():
        for word in keywords:
            # Use \b for word boundaries to avoid partial matches
            # (e.g., 'offer' matching 'offered' or 'offering')
            if re.search(rf"\b{re.escape(word)}\b", text):
                scores[category] += 1

    # Return the category with the highest hits, or None to trigger the LLM
    best_category = max(scores, key=scores.get)
    return best_category if scores[best_category] > 0 else None


def prompt_ai(message):
    """
    Prompt the ollama AI to categorise the email.
    TODO: Find optimal prompt
    """

    prompt = f"Classify the following email into exactly one of these categories: [APPLIED, INTERVIEWING, REJECTED, OFFER]. If you are unsure, respond with [UNKNOWN]. Email'{message}'"

    prompt_json = {
        "model": "",
        "prompt": prompt,
        "stream": False,
    }
    print(prompt_json)

    response = requests.post(
        "http://ollama_dev:11434/api/generate", data=json.dumps(prompt)
    )

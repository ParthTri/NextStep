import json
import re

import requests

from nextstep import models


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


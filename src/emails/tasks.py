from celery.app import shared_task
from celery.utils.log import get_task_logger

from emails import email_reader, parser
from nextstep import models

logger = get_task_logger(__name__)


# Main task to get all the details
@shared_task
def bg_emails():
    # Get all the users that are connected
    # Limited only using Gmail
    users = models.UserEmailAccount.objects.filter(provider="GMAIL")

    # Loop over all users
    # 1. Pull emails from last 30 minutes
    # 2. Read through all emails
    # 3. Build the look up table for each user
    # 4. Filter out the emails
    # 5. Classify remaining emails
    # 6. Update the statuses on the application
    for user in users:
        user_service = email_reader.get_creds_and_build(user)

        messages = email_reader.get_latest_emails(user_service)

        if len(messages) == 0:
            print("No Emails found")
            continue

        email_content = email_reader.read_emails(user_service, messages)

        applications = models.Application.objects.filter(user=user.user).exclude(
            tags__name__in=["Rejected", "Withdrawn"]
        )

        lookup_table = parser.construct_lookup_table(applications)

        user_categories: models.QuerySet[models.Tag, models.Tag] = (
            models.Tag.objects.filter(user=user.user)
        )

        categories: list[str] = list(map(lambda x: x.name, user_categories))

        found_emails = parser.filter_emails(email_content, lookup_table)

        for application_id, email in found_emails.items():
            category = parser.classify_with_keywords(email, categories)

            if category is not None:
                tag = models.Tag.objects.get(name=category)
                application = models.Application.objects.get(id=application_id)

                if application.get_current_tag() != tag:
                    application = models.ApplicationTag.objects.create(
                        application=application, tag=tag
                    )
                    logger.info(f"{application.id} Updated status to {category}")

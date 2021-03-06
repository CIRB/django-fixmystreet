from django.core.management.base import BaseCommand, CommandError

from optparse import make_option

from apps.fixmystreet.models import ReportAttachment

import logging, datetime

logger = logging.getLogger("fixmystreet")

class Command(BaseCommand):
    help = 'Delete all 30 days old attachments flaggued as logical_deleted'

    option_list = BaseCommand.option_list + (
        make_option('--delete',
            action='store_true',
            dest='delete',
            default=False,
            help='Delete attachments'),
    )

    def handle(self, *args, **options):
        report_attachments = ReportAttachment.objects.filter(logical_deleted=True, modified__lte=datetime.date.today() - datetime.timedelta(days=30))

        for attachment in report_attachments:
            logger.info("Attachment logical_deleted: %s %s %s" %(attachment.modified, attachment.logical_deleted, attachment.id))

            if options['delete']:
                attachment.delete()

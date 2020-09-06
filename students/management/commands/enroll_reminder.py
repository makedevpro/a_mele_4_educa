import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.mail import send_mass_mail
from django.contrib.auth.models import User
from django.db.models import Count


class Command(BaseCommand):
    """
    For use in views and other functions:

    from django.core import management
    management.call_command('enroll_reminder', days=20)

    """

    help = 'Sends an e-mail reminder to users registered more ' \
           'than N days that are not enrolled into any courses yet'

    def add_arguments(self, parser):
        parser.add_argument('--days', dest='days', type=int)

    def handle(self, *args, **options):
        emails = []
        subject = 'Enroll in a course'
        date_joined = datetime.date.today() - \
            datetime.timedelta(days=options['days'])
        users = User.objects.annotate(course_count=Count('courses_joined'))\
                    .filter(course_count=0, date_joined__lte=date_joined)
        for user in users:
            message = 'Dear {},\n\n We noticed that you didn\'t ' \
                      'enroll in any courses yet. What are you waiting' \
                      ' for?'.format(user.username)
            emails.append((subject,
                           message,
                           settings.DEFAULT_FROM_EMAIL,
                           [user.email]))
        send_mass_mail(emails)
        self.stdout.write('Sent {} reminders'.format(len(emails)))

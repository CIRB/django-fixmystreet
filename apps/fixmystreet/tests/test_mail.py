from django.test.client import Client
from django.core.urlresolvers import reverse
from django.core import mail

from apps.fixmystreet.models import (
    Report, ReportCategory, OrganisationEntity, ReportAttachment,
    FMSUser, OrganisationEntitySurface, GroupMailConfig,
    ReportComment)
from apps.fixmystreet.tests import FMSTestCase

from django.contrib.gis.geos import Polygon

from datetime import datetime, timedelta


#class MailTest(FMSTestCase):

#    def setUp(self):
#        self.citizen = FMSUser(
#            telephone="0123456789",
#            last_used_language="fr",
#            first_name="citizen",
#            last_name="citizen",
#            email="citizen@a.com"
#        )
#        self.citizen.save()
#        self.manager = FMSUser(
#            is_active=True,
#            telephone="0123456789",
#            last_used_language="fr",
#            password='test',
#            first_name="manager",
#            last_name="manager",
#            email="manager@a.com",
#            manager=True
#        )
#        self.manager.set_password('test')
#        self.manager.organisation = OrganisationEntity.objects.get(pk=14)
#        self.manager.save()
#
#        self.manager4 = FMSUser(
#            is_active=True,
#            telephone="0123456789",
#            last_used_language="fr",
#            password='test',
#            first_name="manager4",
#            last_name="manager4",
#            email="manager4@a.com",
#            manager=True
#        )
#        self.manager4.set_password('test')
#        self.manager4.organisation = OrganisationEntity.objects.get(pk=14)
#        self.manager4.save()
#
#        self.group = OrganisationEntity(
#            type="D",
#            name_nl="Werken",
#            name_fr="Travaux",
#            phone="090987",
#            dependency=OrganisationEntity.objects.get(pk=14),
#            email="test1@email.com"
#            )
#        self.group.save()
#        self.group.dispatch_categories.add(ReportCategory.objects.get(pk=1))
#
#        # Mail config: notify group and members in real time
#        self.group_mail_config                = GroupMailConfig()
#        self.group_mail_config.group          = self.group
#        self.group_mail_config.notify_group   = True
#        self.group_mail_config.notify_members = True
#        self.group_mail_config.save()
#
#        self.manager.memberships.create(organisation=self.group, contact_user=True)
#        self.manager4.memberships.create(organisation=self.group, contact_user=True)
#
#        self.client = Client()
#
#        self.manager2 = FMSUser(
#            is_active=True,
#            telephone="9876543210",
#            last_used_language="nl",
#            password='test',
#            first_name="manager2",
#            last_name="manager2",
#            email="manager2@a.com",
#            manager=True
#        )
#        self.manager2.set_password('test2')
#        self.manager2.organisation = OrganisationEntity.objects.get(pk=14)
#        self.manager2.save()
#
#        self.group2 = OrganisationEntity(
#            type="D",
#            name_nl="Werken",
#            name_fr="Travaux",
#            phone="090987",
#            dependency=OrganisationEntity.objects.get(pk=21),
#            email="test2@email.com"
#        )
#        self.group2.save()
#        self.group2.dispatch_categories.add(ReportCategory.objects.get(pk=2))
#        self.group2.dispatch_categories.add(ReportCategory.objects.get(pk=1))
#
#        # Mail config: notify group and members in real time
#        self.group_mail_config2                = GroupMailConfig()
#        self.group_mail_config2.group          = self.group2
#        self.group_mail_config2.notify_group   = True
#        self.group_mail_config2.notify_members = True
#        self.group_mail_config2.save()
#
#        p1 = (148776, 171005)
#        p2 = (150776, 171005)
#        p3 = (150776, 169005)
#        p4 = (148776, 169005)
#
#        surface = OrganisationEntitySurface(
#            geom=Polygon([p1, p2, p3, p4, p1]),
#            owner=OrganisationEntity.objects.get(pk=14),
#        )
#        surface.save()
#
#        self.manager2.memberships.create(organisation=self.group2)
#
#        self.manager3 = FMSUser(
#            is_active=True,
#            telephone="000000000",
#            last_used_language="nl",
#            password='test',
#            first_name="manager3",
#            last_name="manager3",
#            email="manager3@a.com",
#            manager=True
#        )
#        self.manager3.set_password('test3')
#        self.manager3.organisation = OrganisationEntity.objects.get(pk=21)
#        self.manager3.save()
#
#        self.manager3.memberships.create(organisation=self.group2)
#
#        self.impetrant = OrganisationEntity(
#            name_nl="MIVB",
#            name_fr="STIB",
#            email="stib@mivb.be")
#
#        self.impetrant.save()
#
#        self.contractor = OrganisationEntity(
#            name_nl="Fabricom GDF",
#            name_fr="Fabricom GDF",
#            email="contractor@email.com")
#        self.contractor.save()
#
#        self.sample_post = {
#            'report-x': '150056.538',
#            'report-y': '170907.56',
#            'report-address_fr': 'Avenue des Arts, 3',
#            'report-address_nl': 'Kunstlaan, 3',
#            'report-address_number': '3',
#            'report-postalcode': '1210',
#            'report-category': '1',
#            'report-secondary_category': '1',
#            'report-subscription': 'on',
#            'citizen-quality': '1',
#            'comment-text': 'test',
#            'files-TOTAL_FORMS': 0,
#            'files-INITIAL_FORMS': 0,
#            'files-MAX_NUM_FORMS': 0,
#            'citizen-email': self.citizen.email,
#            'citizen-firstname': self.citizen.first_name,
#            'citizen-lastname': self.citizen.last_name,
#            'report-terms_of_use_validated': True
#        }
#
#        self.sample_post_pro = {
#            'report-x': '150056.538',
#            'report-y': '170907.56',
#            'report-address_fr': 'Avenue des Arts, 3',
#            'report-address_nl': 'Kunstlaan, 3',
#            'report-address_number': '3',
#            'report-postalcode': '1210',
#            'report-category': '1',
#            'report-secondary_category': '1',
#            'report-subscription': 'on',
#            'comment-text': 'test',
#            'files-TOTAL_FORMS': 0,
#            'files-INITIAL_FORMS': 0,
#            'files-MAX_NUM_FORMS': 0,
#            'report-terms_of_use_validated': True
#        }
#
#        self.sample_post_mail_pdf_pro = {
#            'comments': 'test comment',
#            'visibility': 'private',
#            'to': 'test@test.com,filip@test.com;test@filip.com'
#        }
#
#        self.sample_post_mail_pdf_citzen = {
#            'comments': 'test comment',
#            'visibility': 'public',
#            'to': 'test@test.com,filip@test.com;test@filip.com'
#        }
#
#    def test_create_report_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members
#        expected_recipients = self.group_mail_config.get_manager_recipients()
#
#        # 1 more mail is sent to creator in real time
#        expected_recipients.append(self.citizen.email)
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_close_report_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report = response.context['report']
#
#        report             = response.context['report']
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Close the report
#        self.client.login(username='manager@a.com', password='test')
#        response = self.client.get(reverse('report_close_pro', args=[report.id]), follow=True)
#
#        report = Report.objects.get(id=report.id)
#
#        self.assertEquals(report.status, Report.PROCESSED)
#
#        # One mail is sent in real time to the creator if citizen. All others are digest to subscribers.
#        self.assertEquals(len(mail.outbox), 1)
#        self.assertIn(self.citizen.email, mail.outbox[0].to)
#
#    def test_refuse_report_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Login to access the pro page to create a user
#        self.client.login(username='manager@a.com', password='test')
#
#        # Refuse the created report
#        refused_url    = reverse('report_refuse_pro', args=[report.id])
#        refused_params = {'text': 'more info'}
#        response       = self.client.post(refused_url, refused_params, follow=True)
#
#        report = Report.objects.get(id=report.id)
#
#        # The status of the report must now be REFUSED
#        self.assertEquals(report.status, Report.REFUSED)
#
#        # All mail are sent as digest to subscribers
#        self.assertEquals(len(mail.outbox), 1)
#
#    def test_subscription_for_citizen_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Reset outobox
#        mail.outbox = []
#
#        # Send a post request subscribing a citizen to the just created report
#        subscribe_url    = reverse('subscribe', args=[report.id])
#        subscribe_email  = 'post@test.com'
#        subscribe_params = {'citizen_email': subscribe_email}
#        response         = self.client.post(subscribe_url, subscribe_params, follow=True)
#
#        # 1 mail sent in real-time to subscriber
#        self.assertEquals(len(mail.outbox), 1)
#        self.assertTrue(subscribe_email in mail.outbox[0].to)
#
#    def test_mark_report_as_done_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Send a post request to mark the report as done
#        update_url    = reverse('report_fix_pro', args=[report.id])
#        update_params = {'text':'My comment'}
#        response      = self.client.post(update_url, update_params)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members without the author
#        expected_recipients = self.group_mail_config.get_manager_recipients(self.manager)
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_accept_report_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Reset outbox
#        mail.outbox = []
#
#        self.client.login(username='manager@a.com', password='test')
#
#        url      = reverse('report_accept_pro', args=[report.id])
#        response = self.client.get(url, follow=True)
#
#        # All mails are sent to subscribers as digest
#        self.assertEquals(len(mail.outbox), 0)
#
#    def test_planned_report_mail(self):
#        # Send a post request filling in the form to create a report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#
#        report             = response.context['report']
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Set as planned
#        date_planned = (datetime.now() + timedelta(days=1)).strftime("%m/%Y")
#        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[report.id]), date_planned)
#
#        self.client.login(username='manager@a.com', password='test')
#        response = self.client.get(url,   follow=True)
#        report = response.context['report']
#
#        self.assertTrue(report.is_planned())
#        self.assertEqual(date_planned, report.date_planned.strftime("%m/%Y"))
#
#        # Only digest are sent to subscribers
#        self.assertEquals(len(mail.outbox), 0)
#
#        # Planned another date
#        date_planned = (datetime.now() + timedelta(days=40)).strftime("%m/%Y")
#        url = '%s?date_planned=%s' % (reverse('report_planned_pro', args=[report.id]), date_planned)
#
#        self.client.login(username='manager@a.com', password='test')
#        response = self.client.get(url, follow=True)
#        report = response.context['report']
#
#        self.assertTrue(report.is_planned())
#        self.assertEqual(date_planned, report.date_planned.strftime("%m/%Y"))
#
#        # Only digest are sent to subscribers
#        self.assertEquals(len(mail.outbox), 0)
#
#    def test_create_report_as_pro_mail(self):
#        # Create a report
#        self.client.login(username='manager@a.com', password='test')
#        response = self.client.post(reverse('report_new_pro') + '?x=150056.538&y=170907.56', self.sample_post_pro, follow=True)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members without the author
#        expected_recipients = self.group_mail_config.get_manager_recipients(self.manager)
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_report_resolved_as_pro_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report_id = response.context['report'].id
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report_id]), follow=True)
#        self.assertEquals(response.status_code, 200)
#
#        # Clear outbox
#        mail.outbox = []
#
#        params = {
#            'text' : 'Ceci est un commentaire'
#        }
#        response = self.client.post(reverse('report_fix_pro', args=[report_id]), params, follow=True)
#
#        self.assertEquals(response.status_code, 200)
#        self.assertEquals(Report.objects.get(id=report_id).status, Report.SOLVED)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members without the author
#        expected_recipients = self.group_mail_config.get_manager_recipients(self.manager)
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_assign_to_other_member_of_same_entity_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Restet outbox
#        mail.outbox = []
#
#        # Change manager in the same entity
#        response = self.client.post(reverse('report_change_manager_pro', args=[report.id]), {'man_id' : 'department_' + str(self.group2.id), 'transfer':0}, follow=True)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members
#        expected_recipients = self.group_mail_config2.get_manager_recipients()
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_assign_to_another_entity_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Restet outbox
#        mail.outbox = []
#
#        # Change to another entity
#        response = self.client.post(reverse('report_change_manager_pro', args=[report.id]), {"man_id": "entity_21", "transfer": 0}, follow=True)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members
#        expected_recipients = self.group_mail_config2.get_manager_recipients()
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_assign_to_impetrant_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Add a worker for this entity
#        worker = FMSUser(email="worker@impetrant.be", telephone="0123456789")
#        worker.save()
#        worker.memberships.create(organisation=self.impetrant)
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Assign to another impetrant
#        response = self.client.get(reverse('report_change_contractor_pro', args=[report.id]) + '?contractorId=' + str(self.impetrant.id), {}, follow=True)
#
#        # 1 mail sent in real time to impetrant
#        self.assertEquals(len(mail.outbox), 1)
#        self.assertIn(self.impetrant.email, mail.outbox[0].to)
#
#    def test_assign_to_contractor_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#
#        report             = response.context['report']
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Add a worker for this entity
#        worker = FMSUser(email="worker@contractor.be", telephone="0123456789")
#        worker.save()
#        worker.memberships.create(organisation=self.contractor)
#
#        # Reset outbox
#        mail.outbox = []
#
#        self.client.login(username='manager@a.com', password='test')
#        response = self.client.get(reverse('report_change_contractor_pro', args=[report.id]) + '?contractorId=' + str(self.contractor.id), {}, follow=True)
#
#        # 1 mail sent in real time to contractor
#        self.assertEquals(len(mail.outbox), 1)
#        self.assertIn(self.contractor.email, mail.outbox[0].to)
#
#    def test_citizen_updates_report_mail(self):
#        response = self.client.post(
#            reverse('report_new') + '?x=150056.538&y=170907.56',
#            self.sample_post,
#            follow=True)
#
#        report             = response.context['report']
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Reset outbox
#        mail.outbox = []
#
#        # A citizen documents a report
#        response = self.client.post(reverse('report_document', kwargs={'report_id': report.id, 'slug': 'hello'}), {
#            'comment-text': 'new created comment',
#            'citizen-email': self.citizen.email,
#            'citizen-quality': 1,
#            'files-TOTAL_FORMS': 0,
#            'files-INITIAL_FORMS': 0,
#            'files-MAX_NUM_FORMS': 0
#        }, follow=True)
#
#        report = response.context['report']
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members
#        expected_recipients = self.group_mail_config.get_manager_recipients()
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_pro_updates_report_mail(self):
#        response = self.client.post(
#            reverse('report_new') + '?x=150056.538&y=170907.56',
#            self.sample_post,
#            follow=True)
#
#        report = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Document report as pro
#        response = self.client.post(reverse('report_show_pro', kwargs={'report_id': report.id, 'slug': 'hello'}), {
#            'comment-text': 'new created comment',
#            'files-TOTAL_FORMS': 0,
#            'files-INITIAL_FORMS': 0,
#            'files-MAX_NUM_FORMS': 0
#        }, follow=True)
#
#        # Mails are sent to responsibles according to mail config of the group: 1 for group + members without the author
#        expected_recipients = self.group_mail_config.get_manager_recipients(self.manager)
#
#        self.assertTrue(mail.outbox)
#        self.assertEquals(len(mail.outbox), len(expected_recipients))
#
#        for email in mail.outbox:
#            self.assertIn(email.to[0], expected_recipients)
#
#    def test_publish_comment_mail(self):
#        response  = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Accept and publish the created report
#        report.private     = False
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Assure that comment is private
#        self.assertEqual(ReportAttachment.PRIVATE, report.comments()[0].security_level)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Now make the comment public
#        response = self.client.get(
#            reverse('report_update_attachment', args=[report.id]),
#            {
#                'updateType': 1,
#                'attachmentId': report.comments()[0].id
#            },
#        follow=True)
#
#        self.assertEqual(ReportAttachment.PUBLIC, report.comments()[0].security_level)
#
#        # All notifications are sent to subscribers as digest
#        self.assertEquals(len(mail.outbox), 0)
#
#    def test_subscription_for_pro_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#        self.client.logout()
#
#        # Reset outbox
#        mail.outbox = []
#
#        self.client.login(username='manager2@a.com', password='test2')
#        response = self.client.get(reverse('subscribe_pro', args=[report.id]), {}, follow=True)
#
#        # 1 mail sent in real-time to subscriber
#        self.assertEquals(len(mail.outbox), 1)
#        self.assertTrue(self.manager2.email in mail.outbox[0].to)
#
#    def test_make_report_switch_visibility(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#
#        # Assure that report is public
#        report = response.context['report']
#        self.assertFalse(report.private)
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # 1/ Now make the report private
#        response = self.client.get(reverse('report_change_switch_visibility', args=[report.id]) + '?visibility=true', follow=True)
#
#        report = Report.objects.get(id=report.id)
#        self.assertTrue(report.private)
#
#        # Mails are sent in real time
#        self.assertEquals(len(mail.outbox), 1)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # 2/ Now make the report public
#        response = self.client.get(reverse('report_change_switch_visibility', args=[report.id]) + '?visibility=false', follow=True)
#
#        report = Report.objects.get(id=report.id)
#        self.assertFalse(report.private)
#
#        # Mails are sent in real time
#        self.assertEquals(len(mail.outbox), 1)
#
#    #def testMergeReportMail(self):
#    #    #Login to access the pro page
#    #    self.client.login(username='manager@a.com', password='test')
#    #    #Send a post request filling in the form to create a report
#    #    response = self.client.post(reverse('report_new_pro') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#    #    self.assertEquals(response.status_code, 200)
#    #    self.assertIn('report', response.context)
#
#    #    report_id = response.context['report'].id
#
#    #    self.assertEquals(len(mail.outbox),  1)  # one for creator subscription, one for manager
#
#    #    self.client.logout()
#    #    response = self.client.post(
#    #        reverse('report_new') + '?x=150056.538&y=170907.56',
#    #        self.sample_post,
#    #        follow=True)
#    #    self.assertEquals(response.status_code, 200)
#        # Should send mail only to responsible
#    #    self.assertEquals(len(mail.outbox), 3)
#
#    #    report2_id = response.context['report'].id
#
#    #    self.client.login(username='manager@a.com', password='test')
#        # Publish the created report
#    #    response3 = self.client.post(reverse('report_accept_pro', args=[report2_id]), follow=True)
#    #    self.assertEquals(response3.status_code, 200)
#    #    self.assertEquals(len(mail.outbox), 4)
#
#        # Merge reports
#    #    url2 = reverse('report_do_merge_pro', args=[report_id])
#    #    self.client.post(url2, {"mergeId": report2_id})
#
#    #    self.assertTrue(Report.objects.all().visible().filter(id=report_id).exists())
#    #    self.assertFalse(Report.objects.all().visible().filter(id=report2_id).exists())
#
#        #Reference from merged to kept report
#    #    self.assertEqual(report_id, Report.objects.get(id=report2_id).merged_with.id)
#        #A mail has been sent to the creator of the first report to notify him that his report has been merged
#    #    self.assertEquals(len(mail.outbox), 5)
#
#    def test_send_PDF_to_pro_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report   = response.context['report']
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Publish the created report
#        response = self.client.post(reverse('report_accept_pro', args=[report.id]), follow=True)
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Send Pro PDF
#        response = self.client.post(reverse('send_pdf', args=[report.id]), self.sample_post_mail_pdf_pro)
#
#        # 3 mails should be sent
#        self.assertEquals(len(mail.outbox), 3)
#
#    def test_send_PDF_to_citizen_mail(self):
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#
#        report             = response.context['report']
#        report.accepted_at = datetime.now()
#        report.save()
#
#        # Reset outbox
#        mail.outbox = []
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Now send Pro PDF
#        response = self.client.post(reverse('send_pdf', args=[report.id]), self.sample_post_mail_pdf_citzen)
#
#        # 3 mails should be sent to citizens
#        self.assertEquals(len(mail.outbox), 3)
#
#    def test_reopen_report(self):
#        # New report
#        response = self.client.post(reverse('report_new') + '?x=150056.538&y=170907.56', self.sample_post, follow=True)
#        report = response.context['report']
#
#        comment = ReportComment(report_id=report.id, text='test', type=3)
#        comment.save()
#
#        # Set status to REFUSED
#        report.status = Report.REFUSED
#        report.save()
#
#        # Login to access the pro page
#        self.client.login(username='manager@a.com', password='test')
#
#        # Clear mail outbox
#        mail.outbox = []
#
#        # Reopen reports
#        url      = reverse('report_reopen_pro', args=[report.id])
#        response = self.client.get(url, follow=True)
#        report   = response.context['report']
#
#        # Assert
#        self.assertEquals(Report.MANAGER_ASSIGNED, report.status)
#
#        # No mail sent in real-time
#        self.assertEquals(len(mail.outbox), 0)
#
#    def test_recipient_for_everyone(self):
#        """
#        recipients must contains everyone (group, manager and manager4)
#        """
#        recipients = self.group_mail_config.get_manager_recipients()
#        self.assertEquals(len(recipients), 3)
#        self.assertIn(self.group.email, recipients)
#        self.assertIn(self.manager.email, recipients)
#        self.assertIn(self.manager4.email, recipients)
#
#    def test_recipient_exclude_author(self):
#        """
#        recipients must contains everyone (group, manager and manager4)
#        """
#        recipients = self.group_mail_config.get_manager_recipients(self.manager)
#        self.assertEquals(len(recipients), 2)
#        self.assertIn(self.group.email, recipients)
#        self.assertIn(self.manager4.email, recipients)
#
#    def test_recipient_for_manager_as_group(self):
#        """
#        if email group is same as manager then recipients
#        must contains ony once this email (distinct values)
#        (group email and manager4)
#        """
#        self.group.email = self.manager.email
#        self.group.save()
#        self.group_mail_config.notify_group = False
#        self.group_mail_config.save()
#
#        recipients = self.group_mail_config.get_manager_recipients()
#        self.assertEquals(len(recipients), 2)
#        self.assertIn(self.manager.email, recipients)
#        self.assertIn(self.manager4.email, recipients)
#
#    def test_recipient_for_manager_as_group_author(self):
#        """
#        if email group is same as manager then recipients and also is the author
#        this email must be excluded
#        """
#        self.group.email = self.manager.email
#        recipients = self.group_mail_config.get_manager_recipients(self.manager)
#        self.assertEquals(len(recipients), 2)
#        self.assertIn(self.manager4.email, recipients)
#        self.assertIn(self.group.email, recipients)

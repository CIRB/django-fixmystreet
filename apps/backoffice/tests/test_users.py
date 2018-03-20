from django.core import mail
from django.core.urlresolvers import reverse

from apps.fixmystreet.models import OrganisationEntity, FMSUser
from apps.fixmystreet.tests import FMSTestCase
from apps.backoffice.forms import FmsUserForm

class UsersTest(FMSTestCase):

    def setUp(self):
        self.manager = FMSUser(
            is_active=True,
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="manager",
            last_name="manager",
            email="manager@a.com",
            manager=True
        )
        self.manager.set_password('test')
        self.manager.organisation = OrganisationEntity.objects.get(pk=14)
        self.manager.save()

        self.leader = FMSUser(
            is_active=True,
            telephone="0123456789",
            last_used_language="fr",
            password='test',
            first_name="leader",
            last_name="leader",
            email="leader@a.com",
            manager=True,
            leader=True
        )
        self.leader.set_password('test')
        self.leader.organisation = OrganisationEntity.objects.get(pk=14)
        self.leader.save()
        self.createuser_post = {
            'telephone': '123456',
            'is_active': True,
            'first_name': 'david',
            'last_name': 'hasselhof',
            'email': 'david.hasselhof@baywatch.com'
        }
        self.edituser_post = {
            'telephone': '654321',
            'is_active': True,
            'first_name': 'new_manager',
            'last_name': 'new_manager',
            'email': 'manager2@a.com',
            'manager': True
        }

    def testListUser(self):
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        self.assertFalse(can_create)
        #This user should not be able to create
        users = response.context['users']
        self.assertEquals(users.count(), 2)
        self.assertIn(self.manager, users)
        self.assertIn(self.leader, users)
        #same result for leader
        self.client.logout()
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        self.assertTrue(can_create)
        #This user should not be able to create
        users = response.context['users']
        self.assertEquals(users.count(), 2)
        self.assertIn(self.manager, users)
        self.assertIn(self.leader, users)

    def testCreateUser(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('create_user'), self.createuser_post, follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_users'), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        users = response.context['users']
        self.assertTrue(can_create)
        self.assertEquals(users.count(), 3)
        self.assertContains(response, self.createuser_post["email"])

        new_user = FMSUser.objects.get(email=self.createuser_post['email'])
        self.assertTrue(new_user.password)
        self.assertNotEqual('!', new_user.password)
        #self.assertEquals(len(mail.outbox), 1)

    def testUpdateLeaderAsLeader(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.post(reverse('edit_user', args=[self.leader.id]), self.edituser_post, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('can_edit' in response.context)
        self.assertFalse(response.context['can_edit'])

    def testUpdateUserAsLeader(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.get(reverse('edit_user', args=[self.manager.id]), follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('can_edit' in response.context)
        self.assertTrue(response.context['can_edit'])

        response = self.client.post(reverse('edit_user', args=[self.manager.id]), self.edituser_post, follow=True)

        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)

        can_create = response.context['can_create']
        users = response.context['users']
        self.assertTrue(can_create)

        founduser = False
        for user in users:
            if (user.id == self.manager.id):
                self.assertEquals(user.first_name, self.edituser_post['first_name'])
                self.assertEquals(user.last_name,  self.edituser_post['last_name'])
                self.assertEquals(user.telephone,  self.edituser_post['telephone'])
                self.assertEquals(user.email,      self.edituser_post['email'])
                founduser = True
        self.assertTrue(founduser)

        #now try to update a leader user this should not be allowed
        response = self.client.post(reverse('edit_user', args=[self.leader.id]), self.edituser_post, follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('can_edit' in response.context)
        self.assertFalse(response.context['can_edit'])
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        users = response.context['users']
        self.assertTrue(can_create)
        self.assertNotContains(response, self.manager.email)  # the old one
        self.assertContains(response, self.edituser_post["email"])

        founduser = False

        for user in users:
            if (user.id == self.leader.id):
                self.assertEquals(user.first_name, self.leader.first_name)
                self.assertEquals(user.last_name, self.leader.last_name)
                self.assertEquals(user.telephone, self.leader.telephone)
                self.assertEquals(user.email, self.leader.email)
                founduser = True
        self.assertTrue(founduser)

    def testUpdateUserAsPro(self):
        self.client.login(username='manager@a.com', password='test')
        response = self.client.post(reverse('edit_user', args=[self.manager.id]), self.edituser_post, follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        users = response.context['users']
        self.assertFalse(can_create)
        founduser = False
        for user in users:
            if (user.id == self.manager.id):
                self.assertNotEquals(user.first_name, 'new_manager')
                self.assertNotEquals(user.last_name, 'new_manager')
                self.assertNotEquals(user.telephone, '654321')
                self.assertNotEquals(user.email, 'manager2@a.com')
                founduser = True
        self.assertTrue(founduser)

    def testDeleteUser(self):
        self.client.login(username='leader@a.com', password='test')
        response = self.client.get(reverse('delete_user', args=[self.manager.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        users = response.context['users']
        self.assertEquals(users.count(), 1)
        self.assertTrue(can_create)
        self.assertNotIn(self.manager, users)

    def testDeleteUserAsPro(self):
        self.client.login(username='manager@a.com', password='test')
        response = self.client.get(reverse('delete_user', args=[self.manager.id]), follow=True)
        self.assertEquals(response.status_code, 200)
        response = self.client.post(reverse('list_users'), follow=True)
        self.assertEquals(response.status_code, 200)
        self.assertTrue('users' in response.context)
        self.assertTrue('can_create' in response.context)
        can_create = response.context['can_create']
        users = response.context['users']
        self.assertEquals(users.count(), 2)
        self.assertFalse(can_create)
        self.assertIn(self.manager, users)

    def test_double_pro_case_insensitive(self):
        pro_data = {
            "email"    : "user@fms.be",
            "last_name": "user",
            "telephone": "123456789",
            "quality"  : 1
        }

        # Create first pro
        pro_form = FmsUserForm(pro_data)

        # Form has to be valid
        self.assertTrue(pro_form.is_valid())
        pro_form.save()

        # Create second pro with a caps in email
        pro_data['email'] = pro_data['email'].upper()
        pro_form          = FmsUserForm(pro_data)

        # Form has to be INVALID because the email is already existing
        self.assertFalse(pro_form.is_valid())
        self.assertTrue(pro_form.errors)

    def test_pro_with_citizen_email(self):
        citizen = FMSUser(
            telephone="0123456789",
            first_name="citizen",
            last_name="citizen",
            email="citizen@a.com",
        )
        citizen.save()

        pro_data = {
            "email"    : citizen.email,
            "last_name": "user",
            "telephone": "123456789",
            "quality"  : 1
        }

        # Create a pro user
        pro_form = FmsUserForm(pro_data)

        # Form has to be INVALID because a citizen uses this email
        self.assertFalse(pro_form.is_valid())
        self.assertTrue(pro_form.errors)

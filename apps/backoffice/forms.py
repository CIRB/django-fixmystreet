#-*- coding: utf-8 -*-

import logging

from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

from apps.fixmystreet.models import FMSUser, GroupMailConfig, OrganisationEntity, Report, ReportSubscription, UserOrganisationMembership

#Increase username size
AuthenticationForm.base_fields['username'].max_length = 150
AuthenticationForm.base_fields['username'].widget.attrs['maxlength'] = 150
AuthenticationForm.base_fields['username'].validators[0].limit_value = 150

logger = logging.getLogger("fixmystreet")


class ManagersListForm(forms.Form):
    def __init__(self, user,  *args, **kwargs):
        self.manager = forms.ModelChoiceField(queryset=FMSUser.objects.filter(manager=True, organisation=user.organisation).order_by('last_name', 'first_name'))

        super(ManagersListForm, self).__init__(*args, **kwargs)


class PriorityForm(forms.ModelForm):
    class Meta:
        model = Report
        fields = ('gravity', 'probability',)


class TransferForm(forms.Form):
    NO_SUBSCRIPTION         = 0
    SUBSCRIBE_ME            = 1
    SUBSCRIBE_GROUP_MEMBERS = 2

    TRANSFER_CHOICES=(
        (NO_SUBSCRIPTION        , _("Sans abonnement")),
        (SUBSCRIBE_ME           , _("Je m'abonne personnellement")),
        (SUBSCRIBE_GROUP_MEMBERS, _("J'abonne tous les membres de mon groupe"))
    )

    transfer = forms.ChoiceField(widget=forms.RadioSelect, choices=TRANSFER_CHOICES, required=True, label=_("Are you sure you want to change the responsable manager? This action cannot be undone."), initial=NO_SUBSCRIPTION)
    man_id = forms.CharField(widget=forms.widgets.HiddenInput)

    def save(self, report, user):
        # First manage subscriptions (before that report changes of responsible department)
        subscriber = FMSUser.objects.get(id=user.id)

        if self.SUBSCRIBE_ME == int(self.cleaned_data['transfer']):
            ReportSubscription.objects.get_or_create(report=report, subscriber=subscriber)

        elif self.SUBSCRIBE_GROUP_MEMBERS == int(self.cleaned_data['transfer']):
            members_list = UserOrganisationMembership.objects.filter(organisation=report.responsible_department).values_list('user', flat=True)

            for member in members_list:
                subscriber = FMSUser.objects.get(id=member)
                ReportSubscription.objects.get_or_create(report=report, subscriber=subscriber)

        # Then, manage the transfer
        man_id = self.cleaned_data['man_id']

        if man_id.split("_")[0] == "department":
            newRespMan = OrganisationEntity.objects.get(pk=int(man_id.split("_")[1]))
            report.responsible_department = newRespMan
        elif man_id.split("_")[0] == "entity":
            orgId = int(man_id.split("_")[1])
            report.responsible_entity = OrganisationEntity.objects.get(id=orgId)
            report.responsible_department = None
        else:
            raise Exception('missing department or entity parameter')

        # Contractor reset when transfering from one entity to another.
        report.contractor = None
        # Fix the status
        report.status = Report.MANAGER_ASSIGNED
        report.save()


class FmsUserForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = FMSUser
        fields = (
            'first_name',
            'last_name',
            'telephone',
            'email',
            'is_active',
            # 'leader',
            'manager',
            'agent',
            'contractor'
        )

    first_name = forms.CharField(required=False, label=_("Firstname"))
    last_name = forms.CharField(required=True, label=_("Lastname"))
    email = forms.EmailField(required=True, label=_('Email'))
    telephone = forms.CharField(max_length="20", label=_("Phone"))
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        help_text=_("Only active users can login."),
        label=_("Active")
    )

    # leader = forms.BooleanField(required=False)

    agent = forms.BooleanField(required=False)
    manager = forms.BooleanField(required=False)
    contractor = forms.BooleanField(required=False)

    def clean_email(self):
        # Force and ensure that email is case insensitive
        email = self.cleaned_data["email"].lower()

        try:
            user = FMSUser.objects.get(email__exact=email)

        except FMSUser.DoesNotExist:
            pass
        except FMSUser.MultipleObjectsReturned:
            logger.error("Duplicate user : %s" % email)
            raise ValidationError(_("Duplicate user"))

        return email


class FmsUserCreateForm(FmsUserForm):

    def save(self, commit=True):
        self.instance = self.retrive_user()
        self.password = False

        if not self.instance:
            self.instance.lastUsedLanguage = "FR"

        if self.instance.logical_deleted:
            self.instance.logical_deleted = False

        if not self.instance.is_active:
            self.instance.is_active = True

        if not self.instance.password or self.instance.password == "!":
            self.password = User.objects.make_random_password()
            self.instance.set_password(self.password)
            self.instance.is_active = True

        if not self.instance.username:
            self.instance.username = self.cleaned_data["email"]

        if commit:
            self.instance.save()
            self.notify_user()

        return self.instance

    def retrive_user(self):
        try:
            user = FMSUser.objects.get(email=self.cleaned_data['email'])
            user.__dict__.update(self.cleaned_data)
            print "retrieved"
            self.instance_retrived = True
            return user
        except FMSUser.DoesNotExist:
            self.instance_retrived = False
            return FMSUser(**self.cleaned_data)

    def notify_user(self):
        """
        Send directly an email to the created user
        (do not use the reportnotification class because then the password is saved
        in plain text in the DB)
        """

        if self.password:
            user = self.instance
            recipients = (user.email,)

            data = {
                "user": user,
                "password": self.password,
                "SITE_URL": 'https://{0}'.format(Site.objects.get_current().domain),
            }

            # MAIL SENDING...
            subject, html, text = '', '', ''

            subject = render_to_string('emails/send_created_to_user/subject.txt', data)
            text = render_to_string('emails/send_created_to_user/message.txt', data)
            html = render_to_string('emails/send_created_to_user/message.html', data)

            subject = subject.rstrip(' \n\t').lstrip(' \n\t')

            msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, recipients, headers={"Reply-To": user.modified_by.email})
            if html:
                msg.attach_alternative(html, "text/html")
            # FMX-2466 Deactivate mail sending
            # msg.send()
            # MAIL SENDED


def ownership_choices(current_user_ownership):
    if 'manager' in current_user_ownership:
        if 'contractor' in current_user_ownership:
            return (
                ("entity", _("All reports in my entity")),
                ("responsible", _("My responbsible reports")),
                ("contractor_responsible", _("My responbsible reports as contractor")),
                ("subscribed", _("My subscriptions")),
                ("transfered", _("My transfered reports"))
            )
        else:
            return (
                ("entity", _("All reports in my entity")),
                ("responsible", _("My responbsible reports")),
                ("subscribed", _("My subscriptions")),
                ("transfered", _("My transfered reports"))
            )
    elif 'agent' in current_user_ownership and ('contractor' in current_user_ownership or 'applicant' in current_user_ownership):
        return (
            ("entity", _("All reports in my entity")),
            ("responsible", _("My responbsible reports")),
            ("subscribed", _("My subscriptions"))
        )
    elif 'contractor' in current_user_ownership:
        return (
            ("entity", _("All reports in my entity")),
            ("responsible", _("My responbsible reports")),
            ("subscribed", _("My subscriptions"))
        )
    else:
        return (("entity", _("All reports in my entity")), ("subscribed", _("My subscriptions")))


class SearchIncidentForm(forms.Form):
    status = forms.ChoiceField(choices=(
        ("", _("All Status")),
        ("created", _("Unpublished")),
        ("in_progress", _("In progress")),
        ("in_progress_and_assigned", _("In progress and assigned")),
        ("closed", _("Closed"))
    ), required=False)
    ownership = forms.ChoiceField(choices=(("entity", _("All reports in my entity")), ("subscribed", _("My subscriptions"))), required=False)

    def __init__(self, *args, **kwargs):
        super(SearchIncidentForm, self).__init__(*args, **kwargs)
        self.fields['ownership'].choices = ownership_choices(args[1].get_user_type_list())


class GroupForm(forms.ModelForm):
    required_css_class = 'required'

    class Meta:
        model = OrganisationEntity
        fields = ('name_fr', 'name_nl', 'phone', 'email', 'type')

    name_fr = forms.CharField(label=_("Name FR"))
    name_nl = forms.CharField(label=_("Name NL"))

    phone = forms.CharField(required=True, label=_("Phone"))
    email = forms.EmailField(required=True, label=_('Email'))

    type = forms.ChoiceField(widget=forms.RadioSelect, choices=OrganisationEntity.ENTITY_TYPE_GROUP)

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        if self.instance.id:
            del self.fields['type']  # type is not editable due to possibility contained users

            required_role = OrganisationEntity.ENTITY_GROUP_REQUIRED_ROLE[self.instance.type]
            users_qs = FMSUser.objects.filter(**{required_role: True})
            users_qs = users_qs.filter(organisation=self.instance.dependency)
            users_qs = users_qs.order_by('last_name', 'first_name')

            self.fields['users'] = forms.ModelChoiceField(required=False, queryset=users_qs, label=_("Users"))


class GroupMailConfigForm(forms.ModelForm):

    class Meta:
        model = GroupMailConfig
        fields = "__all__"

    DIGEST_CHOICES = (
        (True, _('Once a day')),
        (False, _('In real time'))
    )
    digest_created    = forms.ChoiceField(widget=forms.RadioSelect, choices=DIGEST_CHOICES, label=_('Digest created'))
    digest_inprogress = forms.ChoiceField(widget=forms.RadioSelect, choices=DIGEST_CHOICES, label=_('Digest in progress'))
    digest_closed     = forms.ChoiceField(widget=forms.RadioSelect, choices=DIGEST_CHOICES, label=_('Digest closed'))
    digest_other      = forms.ChoiceField(widget=forms.RadioSelect, choices=DIGEST_CHOICES, label=_('Digest other'))

    def clean(self):
        """
        Require at least one of notify_group or notify_members (or both)
        """

        if not (self.cleaned_data.get('notify_group') or self.cleaned_data.get('notify_members')):
            raise ValidationError("A notification configuration is required")

        return self.cleaned_data

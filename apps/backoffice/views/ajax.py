import datetime
import re
import json

from django.contrib import messages
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.conf import settings
from django.template import RequestContext

from apps.fixmystreet.models import OrganisationEntity, ReportCategory, Report, ReportMainCategoryClass, ReportSubCategory, ReportEventLog
from apps.fixmystreet.utils import get_current_user, transform_notification_template
from apps.fixmystreet.utils import generate_pdf, JsonHttpResponse


SRID_SPHERICAL_MERCATOR = 3857
SRID_EQUIRECTANGULAR = 4326
SRID_ELLIPTICAL_MERCATOR = 3395
DEFAULT_SRID = SRID_EQUIRECTANGULAR


def saveCategoryConfiguration(request):
    categoriesList = request.REQUEST.getlist("category")
    groupsList = request.REQUEST.getlist("group")

    # Assign new groups to categories. So for each group, add category to dispatch_categories
    for idx, groupParam in enumerate(groupsList):
        newGroup = OrganisationEntity.objects.get(id=groupParam)
        category = ReportCategory.objects.get(pk=categoriesList[idx])

        # Before add, need to remove this category from the old group.
        oldGroups = category.assigned_to_department.filter(dependency=request.user.fmsuser.get_organisation)
        for group in oldGroups:
            group.dispatch_categories.remove(category)

        newGroup.dispatch_categories.add(category)

    return HttpResponseRedirect(reverse("category_gestionnaire_configuration"))


def get_report_popup_details(request):
    report = Report.objects.all().related_fields().visible().transform(DEFAULT_SRID).get(id=request.REQUEST.get("id"))
    response = {
        "id": report.id,
        "type": report.get_status_for_js_map(),
        "latlng": [report.point.x, report.point.y],
        "address": {
            "street": report.address,
            "number": report.address_number,
            "postalCode": report.postalcode,
            "city": report.get_address_commune_name(),
        },
        "categories": report.get_category_path(),
        "photo": report.thumbnail,
        "icons": report.get_icons_for_js_map(pro=True),
        "url": reverse("report_show_pro", args=[report.get_slug(), report.id]),
    }
    response_json = json.dumps(response)
    return HttpResponse(response_json, content_type="application/json")


def secondary_category_for_main_category(request):
    main_category_id = int(request.GET["main_category"])
    secondary_categories = ReportCategory.objects.filter(category_class=main_category_id)
    jsonstring = ReportCategory.listToJSON(secondary_categories)
    return HttpResponse(jsonstring, content_type="application/json")


def sub_category_for_main_category_and_secondary_category(request):
    main_category_id = int(request.GET["main_category"])
    sec_category_id = int(request.GET["sec_category"])

    secondary_categories = ReportCategory.objects.filter(category_class=main_category_id, id=sec_category_id)
    jsonstring = ReportCategory.listToJSON(secondary_categories)
    return HttpResponse(jsonstring, content_type="application/json")


def update_category_for_report(request, report_id):
    main_category_id      = int(request.POST["main_category"])
    secondary_category_id = int(request.POST["secondary_category"])
    sub_category_id       = int(request.POST.get("sub_category", None)) if request.POST.get("sub_category", None) else None

    report             = get_object_or_404(Report, id=report_id)
    secondary_category = ReportCategory.objects.get(id=secondary_category_id)
    sub_category       = None

    if sub_category_id:
        sub_category = secondary_category.sub_categories.get(id=sub_category_id)

    if not report.private and not secondary_category.public:
        messages.add_message(request, messages.ERROR, _("Cannot set a private category to a public report"))
    else:
        report.category = ReportMainCategoryClass.objects.get(id=main_category_id)
        report.secondary_category = secondary_category
        report.sub_category = sub_category
        report.save()

    return HttpResponseRedirect(report.get_absolute_url_pro())

def send_pdf(request, report_id):
    to_return = {
        "status": "success",
        "message": "",
        "logMessages": [],
        "validRecipients": []
    }

    user = get_current_user()
    recipients = request.POST.get('to')
    comments = request.POST.get('comments', '')

    # recipient can't be empty
    if recipients.strip() == '':
        to_return["status"] = "error"
        to_return["message"] = _("Add a valid email address.")
        return JsonHttpResponse(to_return)

    recipients = re.compile("[\\s,;]+").split(recipients)

    valid_recipients = []
    for recipient in recipients:
        recipient = recipient.strip()
        if not recipient:
            continue
        try:
            validate_email(recipient)
            valid_recipients.append(recipient)
        except ValidationError:
            to_return["status"] = "error"
            to_return["message"] = _("There were errors.")
            to_return["logMessages"].append(_("'{email}' is not a valid email address.").format(email=recipient))
            continue
    #if no valid emails, no need to proceed
    if len(valid_recipients) == 0:
        return JsonHttpResponse(to_return)

    # Only set visibility as private if user is auth and visibility POST param is private
    if request.fmsuser.is_pro() and "private" == request.POST.get('visibility'):
        pro_version = True
    else:
        pro_version = False

    report = get_object_or_404(Report, id=report_id)
    #generate the pdf
    pdffile = generate_pdf("reports/pdf.html", {
        'report': report,
        'files': report.files() if pro_version else report.active_files(),
        'comments': report.comments() if pro_version else report.active_comments(),
        'activity_list': report.activities.all(),
        'visibility': 'private' if pro_version else 'public',
        'BACKOFFICE': pro_version,
        'base_url': getattr(settings, 'RENDER_PDF_BASE_URL', None),
    }, context_instance=RequestContext(request))

    subject, html, text = transform_notification_template("mail-pdf", report, user, comment=comments)

    for recipient in valid_recipients:
        msg = EmailMultiAlternatives(subject, text, settings.DEFAULT_FROM_EMAIL, (recipient,))

        if html:
            msg.attach_alternative(html, "text/html")

        #reset the seek to 0 to be able to read multiple times the same file
        pdffile.seek(0)
        name = "export-incident-%s-date-%s.pdf" % (report.id, datetime.date.today().isoformat())
        msg.attach(name, pdffile.read(), 'application/pdf')

        # FMX-2466 Deactivate mail sending
        # msg.send()
        to_return["logMessages"].append(_("Successfully sent to '{email}'.").format(email=recipient))
        to_return["validRecipients"].append(recipient)

    if to_return["status"] == "success":
        to_return["message"] = _("PDF sent by email.")
    else:
        to_return["message"] = _("There were errors.")

    event = ReportEventLog(
                report=report,
                event_type=ReportEventLog.PDF_HISTORY,
                user=user,
                text=", ".join(valid_recipients),
            )
    event.save()

    return JsonHttpResponse(to_return)

def incrementDuplicates(request, report_id):
    report = Report.objects.all().related_fields().visible().transform(DEFAULT_SRID).get(id=report_id)
    report.duplicates = report.duplicates + 1
    report.save()
    to_return = {}
    return JsonHttpResponse(to_return)

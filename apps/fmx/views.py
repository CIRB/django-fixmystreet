import json
from django.shortcuts import render
from django.http import HttpResponse
from apps.fixmystreet.models import Report, FMSUser, ReportFile, Site
from apps.fixmystreet.forms import CitizenForm, ReportCommentForm, ReportFileForm
from django.forms.models import inlineformset_factory
from django.utils.translation import activate, deactivate
from django.core.urlresolvers import reverse
from apps.fixmystreet.utils import hack_multi_file
from django.utils.translation import ugettext as _

def get_response():
    return {
        "_links": {
            "self": {
                # href: "https://api.example.com/api/v1/books/123"
            },
        },
        "response": "OK",
        "exceptions": {
        #   "type":"WARN",
        #   "code":3150300,
        #   "description":"Some warning message"
        },
    }

def return_response(response, status=200):
    del response["exceptions"]

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

def return_exception(exception, status=500):
    response = get_response()

    del response["response"]
    del response["_links"]

    response["exceptions"] = exception

    return HttpResponse(json.dumps(response), content_type="application/json", status=status)

def exit_with_error(description, code=500, type="ERROR"):
    exception = {
      "type": type,
      "code": code,
      "description": description
    }

    return return_exception(exception, code)

def get_translated_value(object, lang, use_uggetext=False):
    activate(lang)

    if use_uggetext:
        value = _(object)
    else:
        if callable(object):
            value = object()
        else:
            value = object

    return value

def ack(request):
    response = get_response()

    return return_response(response)

def attachments(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    if request.method == "POST":
        return add_attachment(request, report)
    else:
        return get_attachments(request, report)

def add_attachment(request, report):
    if request.POST.get('username', None) != None and  request.POST.get('password', None) != None:
        return add_attachment_pro(request, report)
    else:
        return add_attachment_citizen(request, report)

def add_attachment_pro(request, report):
    #Check login and password
    try:
        user_name    = request.POST.get('username')
        user_password = request.POST.get('password')
    except ValueError:
        return exit_with_error("Attachment is not valid", 400)

    if (user_name == None or user_password == None):
        return exit_with_error("Unauthorized", 401)

    try:
        user_object   = FMSUser.objects.get(username=user_name)
        if user_object.check_password(user_password) == False or not user_object.is_active:
            return exit_with_error("Unauthorized", 401)
    except ObjectDoesNotExist:
        return exit_with_error("Unauthorized", 401)
    return add_attachment_for_user(request, report, user_object)

def add_attachment_citizen(request, report):
    citizen_form = CitizenForm(request.POST, request.FILES, prefix='citizen')
    if not citizen_form.is_valid():
        return exit_with_error("Attachment is not valid", 400)

    citizen = citizen_form.save()

    return add_attachment_for_user(request, report, citizen)

def add_attachment_for_user(request, report, user):
    ReportFileFormSet = inlineformset_factory(Report, ReportFile, form=ReportFileForm, extra=0)
    comment_form = ReportCommentForm(request.POST, request.FILES, prefix='comment')
    file_formset = ReportFileFormSet(request.POST, hack_multi_file(request), instance=report, prefix='files', queryset=ReportFile.objects.none())

    response = get_response()
    response['response'] = []
    if comment_form.is_valid():
        comment = comment_form.save(commit=False)
        comment.created_by = user
        comment.report = report
        comment.save()
        response['response'].append(comment.id)
    elif file_formset.is_valid():
        if len(file_formset.files) > 0:
            files = file_formset.save()
            for report_file in files:
                report_file.created_by = user
                report_file.save()
                response['response'].append(report_file.id)
        else:
            return exit_with_error("Attachment is not valid", 400)
    else:
        return exit_with_error("Attachment is not valid", 400)

    return return_response(response)

def get_attachments(request, report):
    response = get_response()
    response['response'] = []
    attachments = report.active_attachments()
    for attachment in attachments:
        res = {
            "id": attachment.id,
            "created": attachment.created.strftime('%d/%m/%Y')
        }


        if attachment.created_by.is_citizen():
            res["created_by"] = {
                "en": get_translated_value("A citizen", "fr", True),
                "fr": get_translated_value("A citizen", "fr", True),
                "nl": get_translated_value("A citizen", "nl", True)
            }
        else:
            res["created_by"] = {
                "en": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
                "fr": get_translated_value(attachment.get_display_name_as_citizen, "fr").name,
                "nl": get_translated_value(attachment.get_display_name_as_citizen, "nl").name,
            }

        if hasattr(attachment, 'reportfile'):
            res["type"] = "attachment"
            if attachment.reportfile.is_pdf():
                res["file-type"] = "PDF"
            elif attachment.reportfile.is_word():
                res["file-type"] = "WORD"
            elif attachment.reportfile.is_excel():
                res["file-type"] = "EXCEL"
            elif attachment.reportfile.is_image():
                res["file-type"] = "IMG"

            if attachment.reportfile.is_image():
                res["url"] = attachment.reportfile.image.url
            else:
                res["url"] = attachment.reportfile.file.url

            res["title"] =  attachment.reportfile.title
        else:
            res["type"] = "comment"
            res["comment"] = attachment.reportcomment.text
        response['response'].append(res)

    return return_response(response)


def categories(request):
    response = get_response()
    response['response'] = "categories"

    return return_response(response)

def generate_report_response(report):
    response = get_response()

    responsible = "%s - %s (%s)" %(report.responsible_department.name,report.responsible_entity.name, report.responsible_department.phone)

    response['response'] = {
        "id": report.get_ticket_number(),
        "created": report.created.strftime('%d/%m/%Y'),
        "status": {
            "value": report.status,
            "en": get_translated_value(report.get_public_status_display, "fr"),
            "fr": get_translated_value(report.get_public_status_display, "fr"),
            "nl": get_translated_value(report.get_public_status_display, "nl"),
        },
        "category": {
            "en": get_translated_value(report.display_category, "fr"),
            "fr": get_translated_value(report.display_category, "fr"),
            "nl": get_translated_value(report.display_category, "nl"),
        },
        "responsible": {
            "en": get_translated_value(responsible, "fr"),
            "fr": get_translated_value(responsible, "fr"),
            "nl": get_translated_value(responsible, "nl"),
        },
        "address": {
            "en": get_translated_value(report.display_address, "fr"),
            "fr": get_translated_value(report.display_address, "fr"),
            "nl": get_translated_value(report.display_address, "nl"),
        },
        "point": {
            "x": report.point.x,
            "y": report.point.y
        },
    }

    # Generate PDF absolute url
    site = Site.objects.get_current()
    base_url = "http://{}".format(site.domain.rstrip("/"))
    relative_pdf_url = reverse("report_pdf", args=[report.id]).lstrip("/")
    absolute_pdf_url = "{}/{}".format(base_url, relative_pdf_url)

    response['_links'] = {
        "self" : "/%s" % report.id,
        "download" : absolute_pdf_url
    }

    return response

def detail(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
        response = generate_report_response(report)

        return return_response(response)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)


from apps.fixmystreet.stats import ReportCountQuery
from apps.fixmystreet.views.main import DEFAULT_SQL_INTERVAL_CITIZEN

def stats(request):
    report_counts = ReportCountQuery(interval=DEFAULT_SQL_INTERVAL_CITIZEN, citizen=True)

    response = get_response()
    response['response'] = {
        "createdCount" : report_counts.recent_new(),
        "inProgressCount": report_counts.recent_updated(),
        "closedCount": report_counts.recent_fixed()
    }

    return return_response(response)

from django.contrib.gis.geos import fromstr
def duplicates(request):

    x = request.GET.get("x", None)
    y = request.GET.get("y", None)

    if x is None or y is None:
        return exit_with_error("Missing coordinates", 400)

    try:
        #Check if coordinates are float
        float(x)
        float(y)
    except ValueError as e:
        return exit_with_error("Invalid coordinates", 400)

    pnt = fromstr("POINT(" + x + " " + y + ")", srid=31370)
    reports_nearby = Report.objects.all().visible().public().near(pnt, 20).related_fields()[0:6]

    response = get_response()
    response["response"] = []
    for report in reports_nearby:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"].append(res.get("response", None))

    return return_response(response)

def history(request, report_id):
    try:
        report = Report.objects.all().public().get(id=report_id)
    except Report.DoesNotExist:
        return exit_with_error("Report does not exist", 404)

    response = get_response()
    response["response"] = []

    activities = report.activities.all().order_by('-event_at')
    for activity in activities:
        if activity.is_public_visible():
            act ={
                "id": activity.id,
                "date": activity.event_at.strftime('%d/%m/%Y'),
                "user":{
                    "en":  get_translated_value(activity.organisation, "fr").name,
                    "fr":  get_translated_value(activity.organisation, "fr").name,
                    "nl":  get_translated_value(activity.organisation, "nl").name
                },
                "event": {
                    "en": get_translated_value(activity.get_public_activity_text, "fr"),
                    "fr": get_translated_value(activity.get_public_activity_text, "fr"),
                    "nl": get_translated_value(activity.get_public_activity_text, "nl")
                }
            }
            response["response"].append(act)
    return return_response(response)

def last_reports(request):
    nbr = request.GET.get('n', None)
    if not nbr:
        nbr = 10
    try:
        nbr = int(nbr)
    except ValueError as e:
        return exit_with_error("Invalid number of reports", 400)

    reports = Report.objects.all().public().order_by('-created')[:nbr]
    response = get_response()
    response["response"] = []
    for report in reports:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"].append(res.get("response", None))
    return return_response(response)

def reports(request):
    #get filters and pagination
    REPORTS_BY_PAGE = 6
    page = request.GET.get('p', None)
    if not page:
        page = 1
    try:
        page = int(page)
    except ValueError as e:
        return exit_with_error("Invalid parameters", 400)

    offset = (page -1) * REPORTS_BY_PAGE
    reports = Report.objects.all().public().order_by('-created')[offset:offset + REPORTS_BY_PAGE]
    response = get_response()
    response["response"] = []
    for report in reports:
        res = generate_report_response(report)
        if res.get("response", None) is not None:
            response["response"].append(res.get("response", None))
    return return_response(response)
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_managers
from django.db import transaction
from django.forms import ChoiceField
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext as _
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, CreateView
from django.views.generic.list import ListView

from events import forms
from events.models import EventInvitation, EventInvitationStatus, Event, \
    EventInvitationAttendance
from student_applications.views import ApplicationBulkOpsMixin
from users.models import PersonalInfo
from utils.base_views import TeamOnlyMixin


class EventMixin(TeamOnlyMixin):
    model = Event
    form_class = forms.EventForm


class EventListView(EventMixin, ListView):
    page_title = _("Events")


class EventCreateView(EventMixin, CreateView):
    page_title = _("Create event")

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class EventUpdateView(EventMixin, UpdateView):
    page_title = _("Update event")


class EventDetailView(TeamOnlyMixin, ApplicationBulkOpsMixin, DetailView):
    model = Event

    @property
    def page_title(self):
        return "{} | {}".format(self.object, _("Events"))

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['event_status'] = ChoiceField(
            (('', "---"),) + EventInvitationStatus.choices,
            False).widget.render(
            'event_status', None)
        d['attendance'] = ChoiceField(
            (('', "---"),) + EventInvitationAttendance.choices,
            False).widget.render(
            'attendance', None)
        return d

    def post(self, request, *args, **kwargs):

        if not request.user.has_perms("student_applications.bulk_application"):
            raise PermissionDenied()

        # if request.POST.get('resend'):
        #     o = self.get_object()
        #     for uid in self.get_user_ids():
        #         a = o.answers.get(user_id=uid)
        #         a.send(self.get_base_url())
        #         messages.success(request, "{} {} <{}>".format(
        #             _("Resent survey to"),
        #             a.user,
        #             a.user.email,
        #         ))

        with transaction.atomic():
            if request.POST.get('event_status'):
                try:
                    code = int(request.POST.get('event_status'))
                except ValueError:
                    return HttpResponseBadRequest("bad invitation status code")
                o = self.get_object()
                for uid in self.get_user_ids():
                    i = o.invitations.get(user_id=uid)
                    if i.status != code:
                        i.status = code
                        messages.info(request, "{}: {}".format(
                            i.user,
                            i.get_status_display()
                        ))
                        i.save()

            if request.POST.get('attendance'):
                try:
                    code = int(request.POST.get('attendance'))
                except ValueError:
                    return HttpResponseBadRequest("bad attendance code")
                o = self.get_object()
                for uid in self.get_user_ids():
                    i = o.invitations.get(user_id=uid)
                    if i.attendance != code:
                        i.attendance = code
                        messages.info(request, "{}: {}".format(
                            i.user,
                            i.get_attendance_display()
                        ))
                        i.save()

            resp = super().post(request, *args, **kwargs)

        return resp


class EventContactsView(TeamOnlyMixin, DetailView):
    model = Event
    template_name = "events/event_contacts.html"

    def get_context_data(self, **kwargs):
        def f(invite):
            assert isinstance(invite, EventInvitation)
            declined = invite.status == EventInvitationStatus.DECLINED
            try:
                info = invite.user.personalinfo
                return (
                    declined, info.hebrew_first_name, info.hebrew_last_name)
            except PersonalInfo.DoesNotExist:
                return (declined, invite.user.email, "")

        d = super().get_context_data(**kwargs)
        qs = self.object.invitations.all()
        d['invites'] = sorted(qs, key=f)
        return d


class InvitationDetailView(DetailView):
    model = EventInvitation

    def post(self, request, *args, **kwargs):

        try:
            status = int(request.POST.get('status', '0'))
        except ValueError:
            status = 0
        if status not in [EventInvitationStatus.APPROVED,
                          EventInvitationStatus.DECLINED,
                          EventInvitationStatus.MAYBE]:
            return HttpResponseBadRequest("Bad status value")

        note = request.POST.get('note')

        o = self.get_object()

        if o.event.ends_at < timezone.now():
            messages.error(request, _("Event already finished."))

        else:
            if status != o.status or note != o.note:
                if o.registration_allowed():
                    o.status = status
                    o.note = note
                    o.save()
                    subject = u"%s: %s - %s" % (
                        o.user, o.get_status_display(), o.event)
                    message = u"%s (%s): %s - %s\n%s" % (o.user, o.user.email,
                                                         o.get_status_display(),
                                                         o.event,
                                                         o.note)
                    mail_managers(subject, message)
                    messages.success(request, _('Thank you!'))
                else:
                    messages.error(request, _('Registration already closed.'))
            else:
                messages.success(request, _('Thank you!'))

        return redirect(o)


class InvitationPreviewView(TeamOnlyMixin, DetailView):
    model = EventInvitation
    template_name = "emails/invitation.html"


class InvitationUpdateView(TeamOnlyMixin, UpdateView):
    model = EventInvitation
    form_class = forms.EventInvitationForm

    def form_valid(self, form):
        d = super().form_valid(form)
        messages.success(self.request, _("Invitation updated successfully"))
        return d

    def get_success_url(self):
        if 'from' in self.request.POST:
            return self.request.POST['from']
        return self.get_object().user.get_absolute_url()

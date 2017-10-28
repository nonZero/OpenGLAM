from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_managers
from django.db import transaction
from django.shortcuts import redirect
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.views.generic.detail import SingleObjectMixin, DetailView, \
    SingleObjectTemplateResponseMixin
from django.views.generic.edit import FormView, CreateView, UpdateView
from django.views.generic.list import ListView

from q13es.forms import get_pretty_answer
from student_applications.views import ApplicationBulkOpsMixin
from . import forms
from surveys.models import SurveyAnswer, Survey
from utils.base_views import TeamOnlyMixin


class SurveyMixin(TeamOnlyMixin):
    model = Survey
    form_class = forms.SurveyForm


class SurveyListView(SurveyMixin, ListView):
    page_title = _("Surveys")


class SurveyCreateView(SurveyMixin, CreateView):
    page_title = _("Create new survey")


class SurveyUpdateView(SurveyMixin, UpdateView):
    def page_title(self):
        return "{}: {} | {}".format(_("Edit"), self.object.email_subject,
                                    _("Surveys"))


class SurveyDetailView(SurveyMixin, ApplicationBulkOpsMixin, DetailView):
    def post(self, request, *args, **kwargs):

        if not request.user.has_perms("student_applications.bulk_application"):
            raise PermissionDenied()

        if request.POST.get('resend'):
            o = self.get_object()
            for uid in self.get_user_ids():
                a = o.answers.get(user_id=uid)
                a.send(self.get_base_url())
                messages.success(request, "{} {} <{}>".format(
                    _("Resent survey to"),
                    a.user,
                    a.user.email,
                ))

        with transaction.atomic():
            if request.POST.get('close'):
                o = self.get_object()
                for uid in self.get_user_ids():
                    a = o.answers.get(user_id=uid)
                    if a.is_open:
                        a.is_open = False
                        a.save()

            resp = super().post(request, *args, **kwargs)

        return resp


class SurveyAnswerView(SingleObjectTemplateResponseMixin,
                       SingleObjectMixin, FormView):
    model = SurveyAnswer

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.answered_at:
            return redirect('sa:dashboard')

        if self.request.user.id and self.object.user != self.request.user:
            messages.warning(request,
                             _(
                                 "Wrong user! Please login with the correct user to continue"))
            return redirect('sa:dashboard')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return super().get_context_data(
            object=self.object,
            **kwargs
        )

    def get_form_class(self):
        return self.get_object().survey.get_form_class()

    def form_valid(self, form):
        data = form.cleaned_data

        o = self.get_object()
        o.data = data
        o.answered_at = timezone.now()
        o.save()

        user_url = self.request.build_absolute_uri(o.user.get_absolute_url())
        message = "{} <{}>\n{}\n\n".format(o.user, o.user.email, user_url)

        message += "\n\n".join(u"{label}:\n  {html}".format(**fld) for fld in
                               get_pretty_answer(form, data)['fields'])

        url = self.request.build_absolute_uri(o.survey.get_absolute_url())
        message += "\n\n%s" % url

        mail_managers("{}: {}".format(o.survey.email_subject, o.user), message)

        messages.success(self.request, _("Thank you!"))

        return redirect('sa:dashboard')

    def form_invalid(self, form):
        messages.warning(self.request,
                         _("Problems detected in form. "
                           "Please fix your errors and try again."))
        return FormView.form_invalid(self, form)

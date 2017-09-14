# coding: utf-8

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import mail_managers
from django.core.urlresolvers import reverse, reverse_lazy
from django.db import transaction
from django.db.models import Count
from django.http import JsonResponse
from django.shortcuts import redirect, get_object_or_404
from django.template import loader
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext as _
from django.views.generic import DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, CreateView
from django.forms import ChoiceField, ModelChoiceField

from events.models import Event
from projects.models import Project
from student_applications.consts import get_user_progress, FORMS, \
    get_user_next_form, FORM_NAMES
from surveys.models import Survey
from users.forms import PersonalInfoForm
from users.models import PersonalInfo, UserLog, UserLogOperation, User, \
    UserNote
from utils.base_views import ProtectedViewMixin, PermissionMixin
from utils.base_views import TeamOnlyMixin
from . import forms
from . import models

logger = logging.getLogger(__name__)


class UserViewMixin(ProtectedViewMixin):
    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)

        d['filled_count'], d['total_count'] = get_user_progress(
            self.request.user)
        d['progress'] = int(100 * (d['filled_count'] + 1) /
                            (d['total_count'] + 1))

        return d


class Dashboard(UserViewMixin, TemplateView):
    template_name = 'dashboard.html'
    page_title = _("Registration")

    def get_note_form(self, data=None):
        return forms.DashboardNoteForm(data)

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['registered'] = get_user_next_form(self.request.user) is None
        d['needs_personal_details'] = not hasattr(self.request.user,
                                                  'personalinfo')
        if d['registered']:
            projects = Project.objects.published().random().with_votes(
                self.request.user)
            d['pending'] = [p for p in projects if not p.vote]
            d['processed'] = sorted([p for p in projects if p.vote],
                                    key=lambda p: p.vote.score,
                                    reverse=True)

        d['note_form'] = self.get_note_form()
        d['notes'] = self.request.user.notes.filter(visible_to_user=True)

        return d

    def get_base_url(self):
        return self.request.build_absolute_uri('/')[:-1]

    def handle_note_form(self):
        form = self.get_note_form(self.request.POST)
        if not form.is_valid():
            return False

        note = form.instance
        assert isinstance(note, UserNote)
        user = self.request.user
        note.user = user
        note.author = user
        note.visible_to_user = True
        note.is_open = True
        form.save()

        UserLog.objects.create(user=user,
                               created_by=user,
                               content_object=note,
                               operation=UserLogOperation.ADD)

        note.notify_managers(self.get_base_url())

        response = render_to_string(
            "student_applications/_dashboard_note.html",
            {'note': note},
            request=self.request)
        return response

    def post(self, request, *args, **kwargs):
        result = self.handle_note_form()

        return JsonResponse({'result': result}, safe=False,
                            status=200 if result else 400)


class PersonalDetailsView(UserViewMixin, CreateView):
    model = PersonalInfo
    form_class = PersonalInfoForm
    page_title = _("Personal Details")
    success_url = reverse_lazy("sa:dashboard")

    def dispatch(self, request, *args, **kwargs):
        """Prevent filling personal information twice"""
        if hasattr(self.request.user, 'personalinfo'):
            return redirect(reverse("sa:dashboard"))

        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = self.request.user
        with transaction.atomic():
            form.instance.user = user
            dirty = False
            if not user.english_display_name:
                user.hebrew_display_name = "{} {}".format(
                    form.cleaned_data['hebrew_first_name'].strip(),
                    form.cleaned_data['hebrew_last_name'].strip(),
                )
                dirty = True
            if not user.english_display_name:
                user.english_display_name = "{} {}".format(
                    form.cleaned_data['english_first_name'].strip().title(),
                    form.cleaned_data['english_last_name'].strip().title(),
                )
                dirty = True
            if dirty:
                user.save()
            resp = super().form_valid(form)

        messages.info(self.request, _("Personal details saved successfully."))

        return resp


class ReviewView(UserViewMixin, TemplateView):
    template_name = 'review.html'
    page_title = _("Registration Details")

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)

        d['registered'] = get_user_next_form(self.request.user) is None

        # if d['registered']:
        #     d['answers'] = get_user_pretty_answers(self.request.user)

        return d


class RegisterView(UserViewMixin, FormView):
    template_name = 'register.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        form = self.get_form_class()
        if form is None:
            return redirect('sa:dashboard')
        self.page_title = "{}: {}".format(_("Registration"), form.form_title)

        return super().dispatch(request, *args, **kwargs)

    def get_form_class(self):
        form_name = get_user_next_form(self.request.user)
        if not form_name:
            return None

        return FORMS[form_name]

    def form_valid(self, form):
        u = self.request.user
        data = form.cleaned_data
        form_name = get_user_next_form(u)

        logger.info("User %s filled %s" % (u, form_name))

        a = models.Answer.objects.create(user=u, q13e_slug=form_name,
                                         data=data)

        try:
            app = u.application
        except models.Application.DoesNotExist:
            app = models.Application(user=u)
        app.forms_filled = u.answers.count()
        app.last_form_filled = a.created_at
        app.save()

        if get_user_next_form(u) is None:
            app.set_and_log_status(app.Status.REGISTERED, None)
            messages.success(self.request,
                             _("Registration completed! Thank you very much!"))
            text, html = self.get_summary_email(u)
            mail_managers(_("User registered: %s") % u.email, text,
                          html_message=html)
            return redirect('sa:dashboard')

        messages.success(self.request, _("'%s' was saved.") % form.form_title)

        return redirect(reverse('sa:register'))

    def get_summary_email(self, u):
        url = self.request.build_absolute_uri(reverse('sa:app_detail',
                                                      args=(
                                                          u.application.id,)))
        html = loader.render_to_string(
            "student_applications/application_summary_email.html", {
                'u': u,
                'url': url
            }, request=self.request)
        return url, html

    def form_invalid(self, form):
        messages.warning(self.request,
                         _("Problems detected in form. "
                           "Please fix your errors and try again."))
        return FormView.form_invalid(self, form)


class AllFormsView(TemplateView, ProtectedViewMixin):
    template_name = 'all-forms.html'

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['forms'] = [(k, FORMS[k]) for k in FORM_NAMES]
        return d


class ApplicationBulkOpsMixin(object):
    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['statuses'] = ChoiceField(
            (('', "---"),) + models.Application.Status.choices,
            False).widget.render(
            'status', None)
        d['surveys'] = ModelChoiceField(Survey.objects.all(),
                                        required=False).widget.render(
            'survey', None)
        d['events'] = ModelChoiceField(Event.objects.all(),
                                       required=False).widget.render(
            'event', None)

        return d

    def get_base_url(self):
        return self.request.build_absolute_uri('/')[:-1]

    def get_user_ids(self):
        return [int(x) for x in self.request.POST.getlist('users')]

    def send_survey(self):
        base_url = self.get_base_url()
        survey = Survey.objects.get(pk=int(self.request.POST['survey']))
        for uid in self.get_user_ids():
            user = User.objects.get(pk=uid)
            o, created = survey.add_user(user)
            if created:
                o.send(base_url)

            msg = "{}: {}".format(user,
                                  _("Sent") if created else _("Already sent"))
            messages.success(self.request, msg)

        return survey

    def send_invites(self):
        event = Event.objects.get(pk=int(self.request.POST['event']))

        for uid in self.get_user_ids():
            user = User.objects.get(pk=uid)
            o, created = event.invite_user(user, self.request.user,
                                           self.get_base_url())
            messages.success(self.request, u"%s: %s" % (user,
                                                        _(
                                                            "Invited") if created else _(
                                                            "Already invited")))

        return event

    def post(self, request, *args, **kwargs):

        if not request.user.has_perms("student_applications.bulk_application"):
            raise PermissionDenied()

        if request.POST.get('status'):
            status = int(request.POST.get('status'))
            for uid in self.get_user_ids():
                user = User.objects.get(pk=uid)
                if user.application.status != status:
                    user.application.set_and_log_status(status,
                                                        self.request.user)
                    messages.success(
                        request, "%s: %s" % (
                            user, user.application.get_status_display())
                    )

        # Send surveys
        if request.POST.get('survey'):
            return redirect(self.send_survey())

        if request.POST.get('event'):
            return redirect(self.send_invites())

        return redirect(request.get_full_path())


class ApplicationListView(TeamOnlyMixin, ApplicationBulkOpsMixin, ListView):
    model = models.Application
    page_title = _("Applications")
    ordering = ('-forms_filled', '-last_form_filled')

    def get_queryset(self):
        qs = super().get_queryset()
        self.status = None
        if 'status' in self.request.GET:
            try:
                self.status = int(self.request.GET['status'])
                qs = qs.filter(status=self.status)
            except ValueError:
                pass
        return qs

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['total'] = models.Application.objects.count()
        d['agg'] = models.Application.objects.values('status').order_by(
            'status').annotate(count=Count('id'))
        for g in d['agg']:
            g['label'] = models.Application.Status.labels[g['status']]

        return d


class ApplicationDetailView(TeamOnlyMixin, DetailView):
    model = models.Application


class ApplicationReviewMixin(TeamOnlyMixin, ProtectedViewMixin):
    model = models.ApplicationReview
    form_class = forms.ApplicationReviewForm

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['application'] = self.application
        return d

    def get_success_url(self):
        return self.application.user.get_absolute_url()


class ApplicationReviewCreateView(ApplicationReviewMixin, CreateView):
    def pre_dispatch(self, request, *args, **kwargs):
        self.application = get_object_or_404(models.Application,
                                             id=int(kwargs['pk']))
        review = self.application.reviews.filter(user=request.user).first()
        if review:
            return redirect('sa:app_review_update', review.id)
        super().pre_dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.user = self.request.user
            form.instance.application = self.application
            resp = super().form_valid(form)
            UserLog.objects.create(user=self.application.user,
                                   created_by=self.request.user,
                                   content_object=form.instance,
                                   operation=UserLogOperation.ADD
                                   )

        return resp


class ApplicationReviewUpdateView(ApplicationReviewMixin, UpdateView):
    def get_success_url(self):
        return self.object.application.user.get_absolute_url()

    def pre_dispatch(self, request, *args, **kwargs):
        self.application = self.get_object().application
        super().pre_dispatch(request, *args, **kwargs)


class ApplicationStatusUpdateView(PermissionMixin, UpdateView):
    permission_required = 'student_applications.change_application'
    model = models.Application
    form_class = forms.ApplicationStatusForm

    def get_success_url(self):
        if 'from' in self.request.POST:
            return self.request.POST['from']
        return self.object.user.get_absolute_url()

    def form_valid(self, form):
        with transaction.atomic():
            form.instance.set_status(form.instance.status, self.request.user)
            log = form.instance.add_status_log()
            UserLog.objects.create(
                user=form.instance.user,
                created_by=self.request.user,
                content_object=log,
                operation=UserLogOperation.CHANGE
            )
            resp = super().form_valid(form)
        return resp

# class CohortDetailView(TeamOnlyMixin, UsersOperationsMixin, DetailView):
#     model = Cohort
#     slug_field = 'code'
#
#     def get_context_data(self, **kwargs):
#         d = super(CohortDetailView, self).get_context_data(**kwargs)
#         d['statuses'] = UserCohortStatus.choices
#         return d
#
#     def post(self, request, *args, **kwargs):
#
#         cohort = self.get_object()
#
#         if request.POST.get('status'):
#             status = int(request.POST.get('status'))
#             for uid in self.get_user_ids():
#                 user = HackitaUser.objects.get(pk=uid)
#                 uc = UserCohort.objects.get(user=user, cohort=cohort)
#                 if uc.status != status:
#                     uc.status = status
#                     uc.save()
#                     messages.success(request, u"%s: %s" %
#                                               (user, uc.get_status_display()))
#                     # fall through.
#
#         # Send surveys
#         if request.POST.get('survey'):
#             return redirect(self.send_survey(request))
#
#         # Send event invitations
#         if request.POST.get('event'):
#             return redirect(self.send_invites(request))
#
#         return redirect(cohort)

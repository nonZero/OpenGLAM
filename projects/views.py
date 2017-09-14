import csv
import io
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import mail_managers
from django.db import transaction
from django.db.models import Sum
from django.http import JsonResponse, HttpResponse
from django.http.response import HttpResponseBadRequest
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.views.generic import CreateView, ListView, DetailView, UpdateView, \
    View
from django.views.generic.detail import SingleObjectMixin

from users.views import CommunityMixin
from utils.base_views import UIMixin, PermissionMixin, TeamOnlyMixin
from . import forms, models

logger = logging.getLogger(__name__)


class ProjectListView(UIMixin, ListView):
    name = 'projects'
    model = models.Project

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        published = self.get_queryset().published().random()
        if self.request.user.is_authenticated():
            for proj in published:
                proj.vote = proj.votes.filter(
                    user=self.request.user,
                ).first()
                proj.bid = proj.bids.filter(
                    user=self.request.user,
                ).first()
        d['published'] = published
        return d


class ProjectBidView(CommunityMixin, ProjectListView):
    TOTAL = 100
    template_name = "projects/project_bid.html"

    def post(self, request, *args, **kwargs):
        try:
            bid = json.loads(self.request.POST['bid'])
            bid = [(models.Project.objects.get(id=k), int(v)) for k, v in bid]
        except (ValueError, KeyError, models.Project.DoesNotExist):
            return HttpResponseBadRequest("bid not found")

        if not all(0 <= n <= self.TOTAL for p, n in bid):
            return HttpResponseBadRequest("bid item not in range")

        if sum(x[1] for x in bid) != self.TOTAL:
            return HttpResponseBadRequest("wrong total")

        with transaction.atomic():
            for p, v in bid:
                o, created = models.ProjectBid.objects.get_or_create(
                    project=p,
                    user=request.user,
                    defaults={'value': v}
                )
                if not created:
                    o.value = v
                    o.save()
            assert models.ProjectBid.objects.filter(user=request.user
                                                    ).aggregate(
                total=Sum('value'))['total'] == self.TOTAL
        messages.success(self.request, _("Thank you!"))
        subject = "{}: {}".format(_("New bid"), request.user.community_name)
        bids = sorted([x for x in bid if x[1]], key=lambda x: x[1],
                      reverse=True)
        html_message = render_to_string("projects/bid_email.html", {
            'base_url': self.request.build_absolute_uri('/')[:-1],
            'bid': bids,
        }, request=self.request)
        message = "\n".join(["{}: {}".format(p, v) for p, v in bids])
        mail_managers(subject, message, html_message=html_message)
        return redirect("projects:list")


class ProjectBidsView(TeamOnlyMixin, View):
    def get(self, request, *args, **kwargs):
        qs = models.ProjectBid.objects.order_by(
            'project__title',
            'user__community_name'
        )
        o = io.StringIO()
        w = csv.writer(o)
        w.writerow((_('project'), _('user'), _('bid')))
        for bid in qs:
            w.writerow((bid.project.title, bid.user.community_name, bid.value))
        o.seek(0)
        return HttpResponse(o, content_type="text/csv")


class ProjectVotesView(TeamOnlyMixin, UIMixin, ListView):
    template_name = "projects/project_list_votes.html"
    model = models.Project


class ProjectDetailView(UIMixin, DetailView):
    name = 'projects'
    model = models.Project

    def get_vote_form(self, data=None):
        if not self.request.user.is_authenticated():
            return None
        o = models.ProjectVote.objects.filter(
            project=self.object,
            user=self.request.user
        ).first()
        form = forms.ProjectVoteForm(data, instance=o)
        form.fields['score'].widget.choices = form.fields[
                                                  'score'].widget.choices[1:]
        return form

    def get_comment_form(self, data=None):
        return forms.ProjectCommentForm(data)

    def get_context_data(self, **kwargs):
        d = super().get_context_data(**kwargs)
        d['vote_form'] = self.get_vote_form()
        d['comment_form'] = self.get_comment_form()
        return d

    def handle_vote_form(self):
        form = self.get_vote_form(self.request.POST)
        if not form.is_valid():
            return False

        form.instance.user = self.request.user
        form.instance.project = self.object
        form.save()
        return True

    def handle_comment_form(self):
        form = self.get_comment_form(self.request.POST)
        if not form.is_valid():
            return False

        form.instance.user = self.request.user
        form.instance.project = self.object
        form.save()
        form.instance.new = True

        url = self.request.build_absolute_uri(form.instance.get_absolute_url())

        subject = "{}: {} -> {}".format(
            _("Comment posted"),
            self.request.user,
            self.object,
        )
        message = "{}\n\n{}\n{}\n\n{} ({})".format(
            url,
            form.instance.get_scope_display(),
            form.instance.content,
            self.request.user,
            self.request.user.email,
        )
        mail_managers(subject, message)

        response = render_to_string("projects/_project_comment.html",
                                    {'c': form.instance, },
                                    request=self.request)
        return response

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()

        form_type = self.request.POST.get('type')

        if form_type == 'vote':
            result = self.handle_vote_form()
        elif form_type == 'comment':
            result = self.handle_comment_form()
        else:
            result = False

        return JsonResponse({'result': result}, safe=False,
                            status=200 if result else 400)


class ProjectCreateView(PermissionMixin, UIMixin, CreateView):
    name = 'projects'
    permission_required = "projects.create_project"
    model = models.Project
    form_class = forms.ProjectForm

    # def get_success_url(self):
    #     return self.object.get_update_url()

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super(ProjectCreateView, self).form_valid(form)


class ProjectUpdateView(PermissionMixin, UIMixin, UpdateView):
    permission_required = "projects.change_project"
    model = models.Project
    form_class = forms.ProjectForm


class ProjectCommentListView(TeamOnlyMixin, UIMixin, ListView):
    model = models.ProjectComment
    paginate_by = 50


class ProjectCommentUpdateView(PermissionMixin, UIMixin, UpdateView):
    permission_required = "projects.projectcomment_change"
    model = models.ProjectComment
    form_class = forms.ProjectCommentEditForm


class ProjectCommentMarkReviewedView(PermissionMixin, SingleObjectMixin, View):
    permission_required = "projects.projectcomment_change"
    model = models.ProjectComment

    def post(self, request, *args, **kwargs):
        o = self.get_object()
        o.is_reviewed = True
        o.reviewed_by = self.request.user
        o.reviewed_at = timezone.now()
        o.save()
        return JsonResponse({})

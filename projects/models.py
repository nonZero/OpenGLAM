import markdown
from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ProjectQuerySet(models.QuerySet):
    def random(self):
        return self.order_by('?')

    def by_title(self):
        return self.order_by('title')

    def published(self):
        return self.filter(is_published=True)

    def unpublished(self):
        return self.filter(is_published=False)

    def with_votes(self, user):
        for proj in self:
            proj.vote = proj.votes.filter(user=user).first()
        return self


class Project(models.Model):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL)
    created_at = models.DateTimeField(auto_now_add=True)
    is_published = models.BooleanField(_('is published'), default=False)
    title = models.CharField(_('title'), max_length=250, blank=False)
    slug = models.CharField(_('slug'), max_length=100, null=True, unique=True)
    summary_markdown = models.TextField(_('summary (markdown)'))
    summary_html = models.TextField(_('summary (html)'), editable=False)
    link = models.URLField(_('link'), null=True, blank=True)
    picture = models.ImageField(upload_to='projects/', null=True, blank=True)

    objects = ProjectQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("project")
        verbose_name_plural = _("projects")

    def __str__(self):
        return self.title

    def natural_key(self):
        return (self.slug,)

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.summary_html = markdown.markdown(self.summary_markdown)
        super().save(force_insert, force_update, using, update_fields)

    def get_absolute_url(self):
        return reverse("projects:detail", args=(self.slug,))

    def get_update_url(self):
        return reverse("projects:update", args=(self.id,))


class ProjectVoteQuerySet(models.QuerySet):
    def desc(self):
        return self.order_by('-score')

    def accepted_users(self):
        from student_applications.models import Application
        return self.filter(
            user__application__status__in=Application.Status.passed_interview,
        )

    def interested(self):
        return self.filter(score__gte=ProjectVote.Score.INTERESTED)


class ProjectVote(models.Model):
    class Score:
        UNINTERESTED = -1
        NEUTRAL = 0
        INTERESTED = 1
        VERY_INTERESTED = 2

        choices = (
            (UNINTERESTED, _('uninterested')),
            (NEUTRAL, _('neutral')),
            (INTERESTED, _('interested')),
            (VERY_INTERESTED, _('very interested')),
        )
        labels = dict((
            (UNINTERESTED, 'warning'),
            (NEUTRAL, 'default'),
            (INTERESTED, 'primary'),
            (VERY_INTERESTED, 'success'),
        ))

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='project_votes')
    project = models.ForeignKey(Project, related_name='votes')
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    score = models.IntegerField(choices=Score.choices)

    objects = ProjectVoteQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        unique_together = (
            ('user', 'project'),
        )

    def __str__(self):
        return "{} - {}: {}".format(
            self.user,
            self.project,
            self.get_score_display(),
        )

    def get_score_label(self):
        return self.Score.labels[self.score]


class ProjectCommentQuerySet(models.QuerySet):
    def asc(self):
        return self.order_by('created_at')

    def desc(self):
        return self.order_by('-created_at')


class ProjectComment(models.Model):
    class Scope:
        PUBLIC = 1
        PRIVATE = 2
        choices = (
            (PUBLIC, _("public")),
            (PRIVATE, _("private")),
        )

    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='project_comments')
    project = models.ForeignKey(Project, related_name='comments')
    in_reply_to = models.ForeignKey('self', null=True, blank=True)
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    scope = models.IntegerField(_('comment view scope'), choices=Scope.choices)
    content = models.TextField(_("content"), blank=False)

    is_published = models.BooleanField(_("is published"), default=True)
    is_reviewed = models.BooleanField(_("is reviewed"), default=False)
    reviewed_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True,
                                    blank=True,
                                    related_name="project_comments_reviewed")
    reviewed_at = models.DateTimeField(_("reviewed at"), null=True, blank=True)

    objects = ProjectCommentQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']
        verbose_name = _("project comment")
        verbose_name_plural = _("project comments")

    def __str__(self):
        return "[#{}] {} - {}: {}".format(
            self.id,
            self.user,
            self.project,
            self.content,
        )

    def is_visible_to(self, user):
        if user.team_member:
            return True
        if not self.is_published:
            return False
        if self.scope == self.Scope.PUBLIC:
            return True
        return self.user == user

    def get_absolute_url(self):
        return "{}#comment-{}".format(
            self.project.get_absolute_url(),
            self.id,
        )


class ProjectBid(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,
                             related_name='project_bids')
    project = models.ForeignKey(Project, related_name='bids')
    created_at = models.DateTimeField(_("created at"), auto_now_add=True)
    updated_at = models.DateTimeField(_("updated at"), auto_now=True)
    value = models.IntegerField()

    class Meta:
        unique_together = (
            ('user', 'project'),
        )
        ordering = ['-created_at']
        verbose_name = _("project bid")
        verbose_name_plural = _("project bids")

    def __str__(self):
        return "{} - {}: {}".format(
            self.project,
            self.user,
            self.value,
        )

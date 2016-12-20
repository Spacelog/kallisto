from django.contrib import admin
from django.utils import timezone
from django.utils.timesince import timeuntil
from django.utils.translation import ugettext_lazy as _
from .models import Mission, Page, Revision


class MissionAdmin(admin.ModelAdmin):
    model = Mission
    list_display = (
        'name',
        'short_name',
        'start',
        'end',
        'n_pages',
        'active',
    )

    def n_pages(self, obj):
        c = obj.pages.count()
        if c == 0 or obj.pages.first().number == 1:
            return c
        else:
            return _(u"%i (pp%i-%i)") % (
                c,
                obj.pages.first().number,
                obj.pages.last().number
            )
    n_pages.short_description = '# pages'


class RevisionInline(admin.StackedInline):
    model = Revision
    max_num = 0
    extra = 0

    readonly_fields = [ 'text', 'by', 'when', ]

class PageAdmin(admin.ModelAdmin):
    model = Page
    list_display = (
        'mission',
        'number',
        'approved',
        'locked_by',
        'locked_for',
        'n_revisions'
    )
    list_display_links = (
        'number',
    )
    inlines = [ RevisionInline, ]
    readonly_fields = [
        'locked_by',
        'locked_until',
        'locked_for',
        'n_revisions',
    ]
    list_filter = (
        'mission',
        'approved',
    )

    def locked_for(self, obj):
        if obj.locked_until is None:
            return u""
        elif obj.locked_until < timezone.now():
            return _(u"(expired)")
        else:
            return timeuntil(obj.locked_until)
    
    def n_revisions(self, obj):
        return obj.revisions.count()
    n_revisions.short_description = _(u'# revisions')

    
admin.site.register(Mission, MissionAdmin)
admin.site.register(Page, PageAdmin)

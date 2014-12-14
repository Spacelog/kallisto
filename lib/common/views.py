from django.core.urlresolvers import reverse


class NextMixin(object):

    def get_next_url(self, default='homepage', *default_args, **default_kwargs):
        """
        Where should we go next?

        Pass default=None if you don't want a default.
        """
        next = self.request.POST.get("next", None)
        if next is None:
            next = self.request.GET.get("next", None)
        if next is None and default is not None:
            next = reverse(default, args=default_args, kwargs=default_kwargs)
        return next

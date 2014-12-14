from django.conf import settings
from django.db import models
import os.path
import time


if hasattr(settings, 'AWS_STORAGE_BUCKET_NAME'):
    import storages.backends.s3boto
    protected_storage = storages.backends.s3boto.S3BotoStorage(
        acl='private',
        querystring_auth=True,
        querystring_expire=600, # 10 minutes, try to ensure people won't/can't share
    )
else:
    from django.core.files.storage import FileSystemStorage
    protected_storage = FileSystemStorage(
        location=os.path.join(settings.MEDIA_ROOT, 'protected'),
        base_url='%s%s/' % (settings.MEDIA_URL, 'protected'),
    )


def core_media_filename(type, instance_unique, filename):
    ts = "%f" % time.time()
    core_len = 3 + len(type) + len(ts)
    instance_unique = unicode(instance_unique)
    if len(instance_unique) + core_len > 60:
        # we want a reasonable amount of the filename in our 100 characters
        instance_unique = instance_unique[:60-core_len]
    base = u"%(type)s/%(instance)s/%(ts)s-" % {
        'type': type,
        'instance': instance_unique,
        'ts': ts
    }
    if len(filename) + len(base) > 100:
        filename = filename[-(100 - len(base)):]
    return base + unicode(filename)


def slugged_media_filename(type, instance, filename):
    """upload_to callable where there's a slug"""
    return core_media_filename(type, instance.slug, filename)


class MigratableFileFieldMixin(object):
    """
    Django 1.7 FieldField isn't serialisable with a lambda as upload_to.

    However this is such a useful pattern that not supporting it makes
    the code a lot more ugly; better to just have a minor custom field type
    that throws away upload_to in migrations. (This isn't strictly how
    migrations are supposed to work, but will do for us here.)
    """

    def deconstruct(self):
        name, path, args, kwargs = super(
            MigratableFileFieldMixin,
            self
        ).deconstruct()
        del kwargs['upload_to']
        return name, path, args, kwargs


class MigratableImageField(MigratableFileFieldMixin, models.ImageField):
    pass

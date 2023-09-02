import django.db.models as m


class BaseModel(m.Model):
    class Meta:
        abstract = True

    date_created = m.DateTimeField(auto_now_add=True)
    date_updated = m.DateTimeField(auto_now=True)


date_created: str = BaseModel._meta.fields[0].column
date_updated: str = BaseModel._meta.fields[1].column

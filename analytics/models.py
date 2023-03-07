from django.db import models as m

class Funnel(m.Model):

    stage = m.CharField(max_length = 1)
    ip = m.TextField()

    def __str__(self):

        return self.stage
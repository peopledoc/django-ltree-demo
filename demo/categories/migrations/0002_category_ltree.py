# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations
from django.contrib.postgres.operations import CreateExtension

import demo.categories.ltree


def get_sql(filename):
    with open('demo/categories/sql/' + filename) as f:
        return f.read()


class Migration(migrations.Migration):

    dependencies = [
        ('categories', '0001_initial'),
    ]

    operations = [
        # Add the 'ltree' extension to PostgreSQL. Only needed once.
        CreateExtension('ltree'),
        # Add the 'path' field to the Category model
        migrations.AddField(
            model_name='category',
            name='path',
            field=demo.categories.ltree.LtreeField(
                editable=False, null=True, default=None
            ),
        ),
        # Create some indexes
        migrations.RunSQL(get_sql('index.sql')),
        # Add a constraint for recursivity
        migrations.RunSQL(get_sql('constraint.sql')),
        # Add a PostgreSQL trigger to manage the path automatically
        migrations.RunSQL(get_sql('triggers.sql')),
    ]

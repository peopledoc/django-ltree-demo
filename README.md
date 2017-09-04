# How to store trees with Django & PostgreSQL


## Rationale

If you ever had the need to store hierarchical data (trees) with Django, you
probably had to use a library like
[django-mptt](https://github.com/django-mptt/django-mptt) or
[django-treebeard](https://github.com/django-treebeard/django-treebeard).
Those libraries work fine at a small scale, but here at PeopleDoc we have
encountered a lot of issues when using them at a bigger scale (tables with
hundreds of thousands of rows and quite a lot of writings).

It turns out that storing trees in a database a solved problem since a long
time, at least with PostgreSQL. The
[ltree](https://www.postgresql.org/docs/9.6/static/ltree.html) extension
provides a convenient data structure, which is very fast on reads, and quite
fast on writing. The algorithm used is very close to django-treebeard's
materialized paths, but with all the power of PostgreSQL.

The main downside of using ltree is that you have to maintain the materialized
path yourself. It doesn't come with any tool to do it automatically.
But fortunately, it's actually quite simple to maintain this path using
PostgreSQL triggers!


## Integration with Django

In [`demo/categories/ltree.py`](/demo/categories/ltree.py) you will find a very
simple Django field for the ltree data type. This field can be used in any
Django model, and adds two lookups: `descendant` and `ancestor`. Those lookups
allow you to query the descendants or the ancestors of any object with a very
simple SQL query.

For example, let's say you have the following model:
```python
from django.db import models

from project.ltree import LtreeField


class Category(models.Model):
  parent = models.ForeignKey('self', null=True)
  code = models.CharField(maxlength=32, unique=True)
  path = LtreeField()
```

The `path` field represents the path from the root to the node, where each
node is represented by its code (it could also be its id, but using the code
is more readable when debugging). For example, if you have a `genetic`
category, under a `science` category, under a `top` category, its path would be
`top.science.category`.

Thanks to the `descendant` and `ancestor` lookups, the `get_descendants`
method in django-mptt can be rewritten as:
```python
def get_descendants(self):
    return Category.objects.filter(path__descendant=self.path)
```

This would generate a SQL query close to:
```sql
SELECT * FROM category WHERE path <@ 'science.biology'
```

## The magic part: PostgreSQL triggers

If you just add a ltree field to your model, you will have to keep the field
up-to-date when inserting or updating instances.  We could do that with Django
signals, but it turns out that PostgreSQL is far better for maintaining
integrity & writing efficient code.

Every time we insert or update a row, we can reconstruct its path by appending
its code to the path of its parent. If the path changed, we'll also need to
update the path of the children, which is a simple `UPDATE`.

This can be done easily with [PostgreSQL
triggers](https://www.postgresql.org/docs/current/static/sql-createtrigger.html).
You can find an implementation of those triggers in the file
[`demo/categories/sql/triggers.sql`](/demo/categories/sql/triggers.sql).


## The demo

In the demo, the following files are the most important:
- [`demo/categories/models.py`](/demo/categories/models.py): The definition of
  a model using ltree
- [`demo/categories/ltree.py`](/demo/categories/ltree.py): A very simple Django
  field for ltree. More lookups could be added (one for `~` for instance).
- [`demo/categories/migrations/0002_category_ltree.py`](/demo/categories/migrations/0002_category_ltree.py):
  The Django migration for creating the ltree field with the SQL triggers.
- [`demo/categories/sql/index.sql`](/demo/categories/sql/index.sql): The indexes recommended for the ltree
  field
- [`demo/categories/sql/constraint.sql`](/demo/categories/sql/constraint.sql): A
  SQL constraint to make sure that we never have loops in our trees.
- [`demo/categories/sql/triggers.sql`](/demo/categories/sql/triggers.sql): The
  implementation of the triggers for maintaining the integrity of the trees.
- [`tests/test_ltree.py`](/tests/test_ltree.py): Some tests to be sure that
  everything works as expected.

### How to install the demo

- Create & activate a virtualenv
- Install the dependencies with `pip install -r requirements.txt`
- Install PostgreSQL with your favorite way
- Export the `PGHOST` and `PGUSER` variables accordingly
- Create the `django_ltree_demo` table
- Run `python manage.py migrate`
- Launch the test with `pytest -v`

## Conclusion

With a few lines a declarative, idiomatic Django code and ~50 lines of SQL we
have implemented a fast and consistent solution for storing and querying trees.
Sometimes it's good to delegate complicated data manipulation to the database
instead of doing everything in Python :) .

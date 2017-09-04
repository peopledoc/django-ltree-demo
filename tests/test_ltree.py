import pytest

from django.db import IntegrityError

from demo.categories.models import Category


pytestmark = pytest.mark.django_db


def test_create_category():
    category = Category.objects.create(name='Foo', code='bar')
    # we need to do a full refresh to get the value of the path
    category.refresh_from_db()

    assert category.id > 0
    assert category.name == 'Foo'
    assert category.code == 'bar'
    assert category.path == 'bar'


def test_direct_children():
    top = Category.objects.create(code='top')
    science = Category.objects.create(code='science', parent=top)
    sport = Category.objects.create(code='sport', parent=top)
    news = Category.objects.create(code='news', parent=top)
    Category.objects.create(code='politics', parent=news)

    # we can acess direct children using the `children` property
    assert list(top.children.order_by('code')) == [news, science, sport]


def test_descendants():
    top = Category.objects.create(code='top')
    top.refresh_from_db()

    science = Category.objects.create(code='science', parent=top)
    Category.objects.create(code='maths', parent=science)
    biology = Category.objects.create(code='biology', parent=science)
    Category.objects.create(code='genetics', parent=biology)
    Category.objects.create(code='neuroscience', parent=biology)

    sport = Category.objects.create(code='sport', parent=top)
    Category.objects.create(code='rugby', parent=sport)
    football = Category.objects.create(code='football', parent=sport)
    Category.objects.create(code='champions_league', parent=football)
    Category.objects.create(code='world_cup', parent=football)

    # we can get all the ancestors of a category (including itself)
    assert list(
        Category.objects
        .filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.science',
        'top.science.biology',
        'top.science.biology.genetics',
        'top.science.biology.neuroscience',
        'top.science.maths',
        'top.sport',
        'top.sport.football',
        'top.sport.football.champions_league',
        'top.sport.football.world_cup',
        'top.sport.rugby',
    ]


def test_ancestors():
    top = Category.objects.create(code='top')
    top.refresh_from_db()

    Category.objects.create(code='sport', parent=top)
    science = Category.objects.create(code='science', parent=top)
    Category.objects.create(code='maths', parent=science)
    biology = Category.objects.create(code='biology', parent=science)
    Category.objects.create(code='genetics', parent=biology)
    neuroscience = Category.objects.create(code='neuroscience', parent=biology)
    neuroscience.refresh_from_db()

    # we can get all the ancestors of a category (including itself)
    assert list(
        Category.objects
        .filter(path__ancestor=neuroscience.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.science',
        'top.science.biology',
        'top.science.biology.neuroscience',
    ]


def test_update_code():
    top = Category.objects.create(code='top')
    top.refresh_from_db()

    Category.objects.create(code='sport', parent=top)
    science = Category.objects.create(code='science', parent=top)
    biology = Category.objects.create(code='biology', parent=science)
    Category.objects.create(code='genetics', parent=biology)
    Category.objects.create(code='neuroscience', parent=biology)

    # update the code of a category, it should update its path as well as
    # the path of all of its descendants
    science.code = 'magic'
    science.save()

    assert list(
        Category.objects
        .filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.magic',
        'top.magic.biology',
        'top.magic.biology.genetics',
        'top.magic.biology.neuroscience',
        'top.sport',
    ]


def test_update_parent():
    top = Category.objects.create(code='top')
    top.refresh_from_db()

    Category.objects.create(code='sport', parent=top)
    science = Category.objects.create(code='science', parent=top)
    biology = Category.objects.create(code='biology', parent=science)
    Category.objects.create(code='genetics', parent=biology)
    Category.objects.create(code='neuroscience', parent=biology)

    # update the parent of a category, it should update its path as well as
    # the path of all of its descendants
    biology.parent = top
    biology.save()

    assert list(
        Category.objects
        .filter(path__descendant=top.path)
        .values_list('path', flat=True)
        .order_by('path')
    ) == [
        'top',
        'top.biology',
        'top.biology.genetics',
        'top.biology.neuroscience',
        'top.science',
        'top.sport',
    ]


def test_simple_recursion():
    foo = Category.objects.create(code='foo')

    # we cannot be our own parent...
    foo.parent = foo
    with pytest.raises(IntegrityError):
        foo.save()


def test_nested_recursion():
    foo = Category.objects.create(code='foo')
    bar = Category.objects.create(code='bar', parent=foo)
    baz = Category.objects.create(code='baz', parent=bar)

    # we cannot be the descendant of one of our parent
    foo.parent = baz
    with pytest.raises(IntegrityError):
        foo.save()

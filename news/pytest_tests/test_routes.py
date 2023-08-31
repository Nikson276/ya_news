from http import HTTPStatus
import pytest
from pytest_django.asserts import assertRedirects
from django.urls import reverse



@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_pk_for_args')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),            
    )
)
# Указываем имя изменяемого параметра в сигнатуре теста.
def test_pages_availability_for_anonymous_user(client, name, args):
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (pytest.lazy_fixture('admin_client'),
         HTTPStatus.NOT_FOUND
        ),
        (pytest.lazy_fixture('author_client'),
         HTTPStatus.OK
        )
    ),    
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_availability_for_comment_edit_and_delete(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.pk,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.pk,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)

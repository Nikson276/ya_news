import pytest
from http import HTTPStatus

from news.models import Comment

from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING, BAD_WORDS



@pytest.mark.parametrize(
    'parametrized_client, comments',
    (
        (pytest.lazy_fixture('client'), 0),
        (pytest.lazy_fixture('author_client'), 1),
    )
)
def test_user_create_comment(
    parametrized_client, comments, form_data, detail_url, news
):
    response = parametrized_client.post(detail_url, data=form_data)
    comments_count = Comment.objects.count()
    assert comments_count == comments
    if comments == 1:
        assertRedirects(response, f'{detail_url}#comments')
        comment = Comment.objects.get()
        assert comment.text == form_data['text']
        assert comment.news == news
        assert comment.author == response.wsgi_request.user           


def test_user_cant_use_bad_words(admin_client, detail_url):
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = admin_client.post(detail_url, data=bad_words_data)
    assertFormError(
        response,
        form='form',
        field='text',
        errors=WARNING
    )
    comments_count = Comment.objects.count()
    assert comments_count == 0



@pytest.mark.parametrize(
    'parametrized_client, access_allowed, comments',
    (
        (pytest.lazy_fixture('author_client'), True, 0),
        (pytest.lazy_fixture('admin_client'), False, 1)
    )
)
def test_delete_permissions(
    parametrized_client, access_allowed, comments, comment_urls
):
    response = parametrized_client.delete(comment_urls['delete'])
    if access_allowed:
        assertRedirects(response, comment_urls['comment'])
    else:
        assert response.status_code == HTTPStatus.NOT_FOUND
    comments_count = Comment.objects.count()
    assert comments_count == comments      
    
@pytest.mark.parametrize(
    'parametrized_client, access_allowed',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('admin_client'), False)
    )
)
def test_edit_permissions(
    parametrized_client, access_allowed, form_data, comment, comment_urls
):
    NEW_COMMENT = 'Новый комментирий'
    url = comment_urls['edit']
    response = parametrized_client.post(url, data={'text': NEW_COMMENT})
    
    if access_allowed:
        assertRedirects(response, comment_urls['comment'])
        comment.refresh_from_db()
        assert comment.text == NEW_COMMENT
    else:
        assert response.status_code == HTTPStatus.NOT_FOUND
        comment.refresh_from_db()
        assert comment.text == form_data['text']

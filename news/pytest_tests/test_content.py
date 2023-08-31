import pytest
from django.urls import reverse
from django.conf import settings


HOME_URL = reverse('news:home')

def test_news_count(client, homepage_news):
    news_count = len(homepage_news)
    assert news_count == settings.NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, homepage_news):
    all_dates = [news.date for news in homepage_news]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates



def test_comments_order(several_comments, client, detail_url):
    response = client.get(detail_url)
    assert 'news' in response.context
    
    news = response.context['news']
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created

    
@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (pytest.lazy_fixture('client'), False),
        (pytest.lazy_fixture('admin_client'), True),
    )    
)
def test_client_has_no_form(
    several_comments, parametrized_client,
    form_in_context, detail_url
):
    response = parametrized_client.get(detail_url)
    assert ('form' in response.context) is form_in_context
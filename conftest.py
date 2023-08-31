import pytest
from django.urls import reverse
from django.conf import settings
from django.db.models.query import QuerySet
from django.utils import timezone
from news.models import Comment, News
from datetime import datetime, timedelta 

COMMENT_TEXT = 'Текст комментария'

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    pass

@pytest.fixture
def author(django_user_model):  
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):  # Вызываем фикстуру автора и клиента.
    client.force_login(author)  # Логиним автора в клиенте.
    return client

@pytest.fixture
# Создаем объект новости
def news() -> News():
    news = News.objects.create(title='Заголовок', text='Текст')
    return news

@pytest.fixture
# Создаем комментарий
def comment(author, news) -> Comment():
    comment = Comment.objects.create(
            news=news,
            author=author,
            text='Текст комментария'
        )
    return comment

@pytest.fixture
# Вытаскиваем pk для новости
def news_pk_for_args(news) -> tuple:
    return news.pk,

@pytest.fixture
# Вытаскиваем pk для комментария
def comment_pk_for_args(comment) -> tuple:
    return comment.pk,


@pytest.fixture
def bulk_news(author, news) -> None:
    ''' Создаем сразу пачку записей через bulk_create()'''
    today = datetime.today()
    all_news = [
        News(title=f'Новость {index}',
                text='Просто текст.',                
                date=today - timedelta(days=index))
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]    
    News.objects.bulk_create(all_news)
    return None

@pytest.fixture
def homepage_news(client, bulk_news) -> QuerySet:
    HOME_URL = reverse('news:home')
    response = client.get(HOME_URL)
    object_list = response.context['object_list']
    return object_list

@pytest.fixture
# Создаем несколько комментариев
def several_comments(author, news) -> None:
    now = timezone.now()
    for index in range(2):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Tекст {index}',
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    return None

@pytest.fixture
# Получим url для страницы детального просмотра
def detail_url(news_pk_for_args) -> str():
    return reverse('news:detail', args=news_pk_for_args)

@pytest.fixture
# Создадим словарь url-ов для тестов
def comment_urls(detail_url, comment_pk_for_args) -> dict:
    urls = {
        'delete': reverse('news:delete', args=comment_pk_for_args),
        'edit': reverse('news:edit', args=comment_pk_for_args),
        'comment': detail_url + '#comments',
    }
    return urls

@pytest.fixture
def form_data():
    return {'text': COMMENT_TEXT}
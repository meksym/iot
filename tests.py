import pytest
from main import get_app
from models import DATABASE, ApiUser
from aiohttp.test_utils import TestClient


@pytest.fixture()
async def client(aiohttp_client):
    client: TestClient = await aiohttp_client(get_app())
    yield client
    await client.close()


@pytest.fixture()
def users():
    """
    Fixture that creates users in the database and removes them after tests.
    This fixture is used to provide a list of users for test functions.
    """
    users = [
        {'name': 'John Doe', 'email': 'john.doe@example.com'},
        {'name': 'Jane Smith', 'email': 'jane.smith@example.com'},
        {'name': 'Bob Johnson', 'email': 'bob.johnson@example.com'},
    ]
    with DATABASE:
        objs = [ApiUser(**user, password='password') for user in users]
        ApiUser.bulk_create(objs)

        for obj, user in zip(objs, users):
            user['id'] = obj.id  # type: ignore

    yield users

    with DATABASE:
        ids = [user['id'] for user in users]
        ApiUser.delete().where(ApiUser.id.in_(ids)).execute()  # type: ignore


class TestUserView:
    # Wrote a test specifically for checking user endpoints. Since the
    # implementation for other models is identical, a positive result
    # for this test indicates correct functionality for the other
    # models as well.

    async def test_retrieve(self, users: list[dict], client: TestClient):
        for user in users:
            response = await client.get('/api/apiuser/%s' % user['id'])
            body = await response.json()

            assert response.status == 200
            assert user == body

    async def test_list(self, users: list[dict], client: TestClient):
        response = await client.get('/api/apiuser')
        body = await response.json()

        assert response.status == 200
        assert len(body['data']) >= len(users)

    async def test_create(self, client: TestClient):
        user = {
            'name': 'test',
            'email': 'test@example.com',
            'password': 'password'
        }
        response = await client.post('/api/apiuser', data=user)
        body = await response.json()

        assert response.status == 201
        assert body['name'] == user['name']
        assert body['email'] == user['email']

        with DATABASE:
            user_filter = ApiUser.id == body['id']

            exists = ApiUser.select().where(user_filter).exists()
            if exists:
                ApiUser.delete().where(user_filter).execute()

            assert exists

    async def test_update(self, users: list[dict], client: TestClient):
        pk = users[0]['id']
        await client.put('/api/apiuser/%s' % pk, data={'name': 'Updated Name'})

        with DATABASE:
            user = ApiUser.get_by_id(pk)
            assert user.name == 'Updated Name'

    async def test_delete(self, users: list[dict], client: TestClient):
        pk = users[0]['id']
        query = ApiUser.select().where(ApiUser.id == pk)

        with DATABASE:
            assert query.exists()
            await client.delete('/api/apiuser/%s' % pk)
            assert not query.exists()

# pyright: reportAssignmentType=false

# Type annotations for the model fields are provided to
# ensure proper functioning of the static code analyzer.

import sys
import peewee
import string
import base64
import secrets
import settings
from hashlib import pbkdf2_hmac


DATABASE = peewee.PostgresqlDatabase(
    settings.DB_NAME,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    host=settings.DB_HOST,
    autoconnect=False
)


def init(option: str):
    if option in ('storage', 'all'):
        default_db = peewee.PostgresqlDatabase(
            'postgres',
            user='postgres',
            autoconnect=False
        )
        default_db.connect()
        default_db.execute_sql(
            "CREATE DATABASE %s" % settings.DB_NAME
        )
        default_db.execute_sql(
            "CREATE USER %s WITH PASSWORD '%s' SUPERUSER" %
            (settings.DB_USER, settings.DB_PASSWORD)
        )
        default_db.close()

    if option in ('schema', 'all'):
        with DATABASE:
            DATABASE.create_tables(
                [ApiUser, Location, Device]
            )


def get_salt():
    characters = string.ascii_letters + string.digits + string.punctuation
    return ''.join(
        secrets.choice(characters) for _ in range(16)
    )


def make_password(password: str, salt: str) -> str:
    raw_hash = pbkdf2_hmac('sha256', password.encode(), salt.encode(), 100000)
    b64hash = base64.b64encode(raw_hash).decode('ascii').strip()

    return '%s$%s' % (salt, b64hash)


class BaseModel(peewee.Model):
    def to_dict(self):
        meta = getattr(self, '_meta')
        assert isinstance(meta, peewee.Metadata), 'Unsupported model type'

        result = {}
        for field in meta.fields:
            value = getattr(self, field, None)
            if isinstance(value, BaseModel):
                value = value.to_dict()

            result[field] = value

        return result


class ApiUser(BaseModel):
    name = peewee.CharField()
    email = peewee.CharField(unique=True)
    password = peewee.CharField()

    id: int
    name: str
    email: str
    password: str
    devices: peewee.ModelSelect

    @classmethod
    def create(cls, *, password, **query):
        instance = cls(
            **query,
            password=make_password(password, get_salt())
        )
        instance.save(force_insert=True)
        return instance

    def check_password(self, password: str) -> bool:
        salt = self.password.split('$')[0]
        return self.password == make_password(password, salt)

    def to_dict(self):
        result = super().to_dict()
        result.pop('password')
        return result

    class Meta:
        database = DATABASE
        table_name = 'api_user'


class Location(BaseModel):
    name = peewee.CharField(unique=True)

    id: int
    name: str
    devices: peewee.ModelSelect

    class Meta:
        database = DATABASE
        table_name = 'location'


class Device(BaseModel):
    name = peewee.CharField(unique=True)
    type = peewee.CharField()
    login = peewee.CharField()
    password = peewee.CharField()

    location = peewee.ForeignKeyField(
        Location,
        on_delete='RESTRICT',
        backref='devices'
    )
    api_user = peewee.ForeignKeyField(
        ApiUser,
        on_delete='RESTRICT',
        backref='devices'
    )

    id: int
    name: str
    type: str
    login: str
    password: str
    location_id: int
    location: Location
    api_user_id: int
    api_user: ApiUser

    class Meta:
        database = DATABASE
        table_name = 'device'


if __name__ == '__main__':
    option = sys.argv[-1]
    init(option)

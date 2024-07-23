from peewee import DoesNotExist
from models import DATABASE, BaseModel
from aiohttp.web import Application, View, json_response


def normalize_int(value, max: int) -> int:
    '''
    If the value is within the range from 1 to max,
    return this value; otherwise, return 1.
    '''
    if not isinstance(value, int):
        return 1
    if 1 <= value <= max:
        return value
    else:
        return 1


class ModelView(View):
    model: type[BaseModel]

    async def list(self):
        with DATABASE:
            total = self.model.select().count()

            page_size = self.request.query.get('page_size', 100)
            page_size = normalize_int(page_size, 200)

            max_page = total // page_size + 1 if total % page_size else 0
            page = self.request.query.get('page', 1)
            page = normalize_int(page, max_page)

            offset = (page - 1) * page_size
            limit = page_size

            objs = self.model.select().offset(offset).limit(limit)
            result = {
                'page': page,
                'page_size': page_size,
                'max_page': max_page,
                'total': total,
                'data': [obj.to_dict() for obj in objs]
            }

        return json_response(result)

    async def retrieve(self):
        pk = self.request.match_info['id']

        try:
            with DATABASE:
                result = self.model.get_by_id(pk).to_dict()
        except DoesNotExist:
            return json_response({'message': 'Not Found'}, status=404)

        return json_response(result)

    async def create(self):
        data = await self.request.post()
        try:
            with DATABASE:
                result = self.model.create(**data).to_dict()
        except Exception as e:
            return json_response({'message': str(e)}, status=400)

        return json_response(result, status=201)

    async def update(self):
        pk = self.request.match_info['id']

        with DATABASE:
            try:
                obj = self.model.get_by_id(pk)
            except DoesNotExist:
                return json_response({'message': 'Not Found'}, status=404)

            data = await self.request.post()

            for key, value in data.items():
                setattr(obj, key, value)
            obj.save()

            return json_response(obj.to_dict())

    async def remove(self):
        pk = self.request.match_info['id']

        with DATABASE:
            try:
                self.model.get_by_id(pk).delete_instance()
            except DoesNotExist:
                return json_response({'message': 'Not Found'}, status=404)

        return json_response({'message': 'OK'})


class DetailView(ModelView):
    async def get(self):
        return await self.retrieve()

    async def put(self):
        return await self.update()

    async def delete(self):
        return await self.remove()


class NotDetailView(ModelView):
    async def get(self):
        return await self.list()

    async def post(self):
        return await self.create()


def register_model(prefix: str, model: type[BaseModel], app: Application):
    '''
    The function creates the necessary view types for implementing
    CRUD operations and adds them to the specified application.

    GET, POST /prefix/model - retrieve a list and create new model records
    GET, PUT, DELETE /prefix/model/id - retrieve, update, and delete an
                                        existing model record by id
    '''
    attrs = {'model': model}
    name = model.__name__

    detail_view = type(name + 'DetailView', (DetailView,), attrs)
    not_detail_view = type(name + 'NotDetailView', (NotDetailView,), attrs)

    base_url = '/%s/%s' % (prefix.lstrip('/').rstrip('/'), name.lower())

    app.router.add_view(base_url, not_detail_view)
    app.router.add_view(base_url + r'/{id:\d+}', detail_view)

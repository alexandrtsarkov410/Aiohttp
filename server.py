import json
from aiohttp import web
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from models import Session, Advertisement, engine, init_orm
from schema import AdCreateSchema, AdUpdateSchema


def validate(incoming_json: dict, schema: type[AdCreateSchema | AdUpdateSchema]):
    try:
        return schema(**incoming_json).model_dump(exclude_unset=True)
    except ValueError as e:
        raise web.HTTPBadRequest(text=str(e))

app = web.Application()


async def orm_context(app: web.Application):
    print("START")
    await init_orm()
    yield
    await engine.dispose()
    print("SHUTDOWN")


@web.middleware
async def session_middleware(request: web.Request, handler):
    # код до каждого запроса
    async with Session() as session:
        request.session = session
        response = await handler(request)
        # код после каждого запросы
        return response


app.cleanup_ctx.append(orm_context)
app.middlewares.append(session_middleware)

def get_http_error(error_class, message):
    return error_class(text = json.dumps({"status": "error", "message": message}),
                        content_type = "application/json"
                        )


async def get_advertisement(session: AsyncSession, advertisement_id: int) -> Advertisement:
    advertisement = await session.get(Advertisement, advertisement_id)
    if advertisement is None:
        raise get_http_error(web.HTTPNotFound, "Advertisement not found")
    return advertisement


async def add_advertisement(session: AsyncSession, advertisement: Advertisement):
    try:
        session.add(advertisement)
        await session.commit()
    except IntegrityError:
        raise get_http_error(web.HTTPConflict, "Advertisement already exists")
    return advertisement


class AdvertisementView(web.View):

    @property
    def session(self) -> AsyncSession:
        return self.request.session

    @property
    def advertisement_id(self):
        return int(self.request.match_info["advertisement_id"])

    async def get(self):
        advertisement = await get_advertisement(self.session, self.advertisement_id)
        return web.json_response (advertisement.json)

    async def post(self):
        json_data = await self.request.json()
        advertisement = Advertisement(**json_data)
        await add_advertisement(self.session, advertisement)
        return web.json_response(advertisement.json)

    async def patch(self):
        json_data = await self.request.json()
        advertisement = await get_advertisement(self.session, self.advertisement_id)
        for field, value in json_data.items():
            setattr(advertisement, field, value)
        await self.session.commit()
        return web.json_response(advertisement.json)

    async def delete(self):
        advertisement = await get_advertisement(self.session, self.advertisement_id)
        await self.session.delete(advertisement)
        await self.session.commit()
        return web.json_response({"status": "deleted"})


app.add_routes(
    [
        web.post("/advertisement", AdvertisementView),
        web.get("/advertisement/{advertisement_id:\d+}", AdvertisementView),
        web.patch("/advertisement/{advertisement_id:\d+}", AdvertisementView),
        web.delete("/advertisement/{advertisement_id:\d+}", AdvertisementView),
    ]
)

web.run_app(app)
import asyncio
import aiohttp


async def main():


    session = aiohttp.ClientSession()


    response = await session.post(
        "http://127.0.0.1:8080/advertisement",
        json = {
            "title": "Первое объявление",
            "description": "Описание первого объявления",
            "owner": "user_1"}
            )
    print(await response.json())
    await session.close()



    response = await session.post(
        "http://127.0.0.1:8080/advertisement",
        json = {
            "title": "Второе объявление",
            "description": "Описание второго объявления",
            "owner": "user_2"}
            )
    print(await response.json())
    await session.close()



    response = await session.get(
        "http://127.0.0.1:8080/advertisement/1"    )
    print(await response.json())
    await session.close()



    response = await session.patch(
        "http://127.0.0.1:8080/advertisement/1",
        json = {
            "title": "Первое объявление",
            "description": "Измененное описание первого объявления"}
            )
    print(await response.json())
    await session.close()



    response = await session.delete("http://127.0.0.1:8080/advertisement/1")
    print(await response.json())
    await session.close()



    response = await session.get("http://127.0.0.1:8080/advertisement/1")
    print(await response.json())
    await session.close()

asyncio.run(main())
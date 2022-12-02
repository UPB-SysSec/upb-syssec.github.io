import asyncio
import json
import os.path
import sys

import aiohttp


async def _get_thing(session, thing_id):
    """Get thing from thingiverse"""
    url_path = f"https://api.thingiverse.com/things/{thing_id}/"
    file_path = f"data/{thing_id}.json"
    result = {}
    if not os.path.isfile(file_path):
        async with session.get(url_path) as request:
            json_body = await request.json()
            if request.status != 200:
                return
            result.update(json_body)

        if result.get("files_url") is not None:
            async with session.get(result.get("files_url")) as request:
                file_list = await request.json()
                result["files"] = file_list

        if result:
            with open(file_path, "w") as file:  # no idea why, but async open didn't work properly
                json.dump(result, file)
            print(f"wrote {file_path}")


async def _get_object(session, object_id):
    """Get object from MMF"""
    url_path = f"https://www.myminifactory.com/api/v2/objects/{object_id}/"
    file_path = f"../mmf_data/{object_id}.json"
    result = {}
    if not os.path.isfile(file_path):
        async with session.get(url_path) as request:
            json_body = await request.json()
            if request.status != 200:
                return
            result.update(json_body)

        if result:
            with open(file_path, "w") as file:  # no idea why, but async open didn't work properly
                json.dump(result, file)
            print(f"wrote {file_path}")


async def _worker(session, getter_func, queue):
    while True:
        _id = await queue.get()
        await getter_func(session, _id)
        queue.task_done()


async def main():

    site = sys.argv[1]
    token = sys.argv[2]
    start_id = int(sys.argv[3])
    max_id = int(sys.argv[4])

    session = aiohttp.ClientSession(
        headers={
            "authorization": f"Bearer {token}",
            "accept": "application/json",
        }
    )

    if site == "thingiverse":
        getter_func = _get_thing
    elif site == "myminifactory":
        getter_func = _get_object

    queue = asyncio.Queue()
    for i in range(start_id, max_id):
        queue.put_nowait(i)

    # Create three worker tasks to process the queue concurrently.
    tasks = [asyncio.create_task(_worker(session, getter_func, queue)) for _ in range(500)]

    await queue.join()

    for task in tasks:
        task.cancel()
    await asyncio.gather(*tasks, return_exceptions=True)
    await session.close()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

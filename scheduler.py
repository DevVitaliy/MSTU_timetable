import asyncio
import bot
import timetable_parser


async def scheduler():
    while True:
        await asyncio.sleep(1800)

        changes = timetable_parser.check_update()
        if changes:
            await bot.send_notification(changes)
        else:
            pass
    return

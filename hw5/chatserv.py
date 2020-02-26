# Implement the server here.
import asyncio
import time

writers = {}
channel_writer = {}
channel_message = {}


class Message:
    def __init__(self, timestamp, message):
        self.timestamp = timestamp
        self.message = message


def timestamp():
    return int(time.time())

async def broadcast(nick, channel, text):
    message = f"message {channel} {timestamp()} {nick} {text}"
    channel_message[channel].append(Message(timestamp(), message))
    for w in channel_writer[channel]:
        await send(w, message)

async def send(writer, message):
    writer.write(f"{message}\n".encode("utf-8"))
    try:
        await writer.drain()
    except (BrokenPipeError, ConnectionResetError):
        return


def isTimestamp(string):
    try:
        int(string)
        if int(string) > timestamp():
            return False
        else:
            return True
    except ValueError:
        return False


def isChannel(channel):
    if isinstance(channel, str):
        if channel[0] == "#":
            if channel[1:].isalnum():
                return True

    return False

async def on_connection(reader, writer):
    # nick
    nick = ""
    loggedIn = False
    while not loggedIn:
        try:
            data = await reader.readline()
        except (BrokenPipeError, ConnectionResetError):
            return
        command = data.decode("utf-8").split()
        if len(command) == 2 and command[0] == "nick":
            if command[1].isalnum():
                if command[1] not in writers:
                    await send(writer, "ok")
                    loggedIn = True
                    nick = command[1]
                    writers[nick] = writer
                else:
                    await send(writer, f"error {nick} is already taken")
            else:
                await send(writer, f"error invalid nick format")
        else:
            await send(writer, f"error unknown command")

    # commands
    while True:
        try:
            data = await reader.readline()
        except (BrokenPipeError, ConnectionResetError):
            writers.pop(nick, None)
            return

        data = data.decode("utf-8")
        command = data.split()

        # nick
        if len(command) == 2 and command[0] == "nick":
            if command[1].isalnum():
                if command[1] not in writers:
                    await send(writer, "ok")
                    writers.pop(nick, None)
                    nick = command[1]
                    writers[nick] = writer
                else:
                    await send(writer, f"error {nick} is already taken")
            else:
                await send(writer, f"error invalid nick format")

        # join
        elif len(command) == 2 and command[0] == "join":
            if isChannel(command[1]):
                if command[1] in channel_writer:
                    if writer not in channel_writer[command[1]]:
                        channel_writer[command[1]].append(writer)
                        await send(writer, "ok")
                    else:
                        await send(writer, f"error {command[1]} already joined")
                else:
                    channel_message[command[1]] = []
                    channel_writer[command[1]] = [writer]
                    await send(writer, "ok")
            else:
                await send(writer, f"error invalid channel format")

        # part
        elif len(command) == 2 and command[0] == "part":
            if isChannel(command[1]):
                if command[1] in channel_writer:
                    if writer in channel_writer[command[1]]:
                        channel_writer[command[1]].remove(writer)
                        await send(writer, "ok")
                    else:
                        await send(writer, f"error {nick} is not subscribed to {command[1]}")
                else:
                    await send(writer, f"error {command[1]} does not exist")
            else:
                await send(writer, f"error invalid channel format")

        # replay
        elif len(command) == 3 and command[0] == "replay":
            if isChannel(command[1]):
                if command[1] in channel_writer:
                    if writer in channel_writer[command[1]]:
                        if isTimestamp(command[2]):
                            timestamp = int(command[2])
                            await send(writer, "ok")
                            for m in channel_message[command[1]]:
                                if m.timestamp >= timestamp:
                                    await send(writer, m.message)
                        else:
                            await send(writer, f"error invalid timestamp")
                    else:
                        await send(writer, f"error you ({nick}) are not in {command[1]}")
                else:
                    await send(writer, f"error {command[1]} does not exist")
            else:
                await send(writer, f"error invalid channel format")

        # message
        elif len(command) >= 3 and command[0] == "message":
            if isChannel(command[1]):
                if command[1] in channel_writer:
                    if writer in channel_writer[command[1]]:
                        message = data.split(None, 2)[2].strip()
                        await broadcast(nick, command[1], message)
                    else:
                        await send(writer, f"error you ({nick}) are not in {command[1]}")
                else:
                    await send(writer, f"error {command[1]} does not exist")
            else:
                await send(writer, f"error invalid channel format")
        else:
            await send(writer, f"error unknown command")


async def main():
    path = "chatsock"
    server_task = await asyncio.start_unix_server(on_connection, path=path)
    async with server_task:
        await server_task.serve_forever()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        exit()

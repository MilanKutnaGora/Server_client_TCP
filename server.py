import asyncio
import random
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='server.log', level=logging.INFO, format='%(message)s')

class EchoServerProtocol(asyncio.Protocol):
    def __init__(self):
        self.clients = []
        self.response_counter = 0
        self.keepalive_task = None

    def connection_made(self, transport):
        self.transport = transport
        self.clients.append(self)
        logging.info(f"Client connected: {transport.get_extra_info('peername')}")

        if len(self.clients) == 1:
            self.keepalive_task = asyncio.create_task(self.send_keepalive())

    def connection_lost(self, exc):
        self.clients.remove(self)
        logging.info(f"Client disconnected: {self.transport.get_extra_info('peername')}")

    async def send_keepalive(self):
        while True:
            await asyncio.sleep(5)
            for client in self.clients:
                response = f"[{self.response_counter}] keepalive"
                self.response_counter += 1
                client.transport.write(response.encode('ascii') + b'\n')

    def data_received(self, data):
        message = data.decode('ascii').strip()
        logging.info(f"Received: {message}")

        if random.random() < 0.1:  # 10% вероятность игнорирования
            self.log_request(message, ignored=True)
            return

        request_number = int(message.split('[')[1].split(']')[0])
        response_delay = random.randint(100, 1000) / 1000.0
        asyncio.get_event_loop().call_later(response_delay, self.send_response, request_number)

    def send_response(self, request_number):
        response = f"[{self.response_counter}] PONG {request_number} ({len(self.clients)})"
        self.log_request(f"[{request_number}] PING", response)
        self.transport.write(response.encode('ascii') + b'\n')
        self.response_counter += 1

    def log_request(self, request, response=None, ignored=False):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S.%f")[:-3]

        if ignored:
            response_str = "(проигнорировано)"
            logging.info(f"{date_str}; {time_str}; {request}; {response_str}")
        else:
            response_time_str = now.strftime("%H:%M:%S.%f")[:-3]
            logging.info(f"{date_str}; {time_str}; {request}; {response_time_str}; {response}")

async def main():
    loop = asyncio.get_running_loop()
    server = await loop.create_server(EchoServerProtocol, '127.0.0.1', 8888)
    print("Server started.")
    try:
        await server.serve_forever()
    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        await server.wait_closed()

if __name__ == '__main__':
    asyncio.run(main())



import asyncio
import random
import logging
from datetime import datetime

# Настройка логирования
logging.basicConfig(filename='client.log', level=logging.INFO, format='%(message)s')

class ClientProtocol(asyncio.Protocol):
    def __init__(self, client_id):
        self.client_id = client_id
        self.request_number = 0
        self.transport = None
        self.keepalive_task = None

    def connection_made(self, transport):
        self.transport = transport
        self.keepalive_task = asyncio.create_task(self.send_requests())

    def connection_lost(self, exc):
        if self.keepalive_task:
            self.keepalive_task.cancel()

    async def send_requests(self):
        while True:
            await asyncio.sleep(random.uniform(0.3, 3.0))
            request = f"[{self.request_number}] PING"
            self.log_request(request)
            self.transport.write(request.encode('ascii') + b'\n')
            self.request_number += 1

    def data_received(self, data):
        message = data.decode('ascii').strip()
        self.log_response(message)

    def log_request(self, request):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S.%f")[:-3]
        logging.info(f"{date_str}; {time_str}; {request}; ; ")

    def log_response(self, response):
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S.%f")[:-3]
        if "keepalive" in response:
            logging.info(f"{date_str}; ; ; ; ")
        else:
            request_number = int(response.split('[')[1].split(']')[0])
            logging.info(f"{date_str}; ; [{request_number}] PONG; ; ")

async def main(client_id):
    loop = asyncio.get_running_loop()
    connection = loop.create_connection(lambda: ClientProtocol(client_id), '127.0.0.1', 8888)
    await connection

# Запустите два процесса для двух клиентов
if __name__ == '__main__':
    asyncio.run(main(1))
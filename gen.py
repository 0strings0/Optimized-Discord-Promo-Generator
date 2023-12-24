import requests
import concurrent.futures
import time
import ctypes
import os
import uuid
from random import choice

os.system('cls' if os.name == 'nt' else 'clear')

class Counter:
    count = 0

class PromoGenerator:
    red = '\x1b[31m(-)\x1b[0m'
    blue = '\x1b[34m(+)\x1b[0m'
    green = '\x1b[32m(+)\x1b[0m'
    yellow = '\x1b[33m(!)\x1b[0m'

    def __init__(self, session=None, proxy=None):
        self.session = session or requests.Session()
        self.proxy = proxy

    def generate_promo(self):
        url = "https://api.discord.gx.games/v1/direct-fulfillment"
        headers = {
            "Content-Type": "application/json",
            "Sec-Ch-Ua": '"Opera GX";v="105", "Chromium";v="119", "Not?A_Brand";v="24"',
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 OPR/105.0.0.0",
        }

        data = {
            "partnerUserId": str(uuid.uuid4())
        }

        retry_attempts = 2

        for _ in range(retry_attempts):
            try:
                if self.proxy:
                    credentials, host = self.proxy.split('@')
                    user, password = credentials.split(':')
                    host, port = host.split(':')
                    formatted_proxy = f"http://{user}:{password}@{host}:{port}"
                    response = self.session.post(url, json=data, headers=headers, proxies={'http': formatted_proxy, 'https': formatted_proxy}, timeout=5)
                else:
                    response = self.session.post(url, json=data, headers=headers, timeout=5)

                if response.status_code == 200:
                    token = response.json().get('token')
                    if token:
                        Counter.count += 1
                        if hasattr(ctypes, 'windll'):
                            ctypes.windll.kernel32.SetConsoleTitleW(
                                f"Nitro Promo Generator | By Strings"
                                f" | Generated : {Counter.count}")
                        link = f"https://discord.com/billing/partner-promotions/1180231712274387115/{token}"
                        return link
                elif response.status_code == 429:
                    return "rate-limited"
                elif response.status_code == 504:
                    continue
                else:
                    continue
            except requests.exceptions.ReadTimeout:
                # Hide the specific timeout error
                continue
            except requests.exceptions.RequestException as e:
                time.sleep(0.5)

        return "Max Retries"

    @staticmethod
    def get_timestamp():
        time_idk = time.strftime('%H:%M:%S')
        return f'[\x1b[90m{time_idk}\x1b[0m]'

class PromoManager:
    def __init__(self):
        self.num_threads = int(input(f"{PromoGenerator.get_timestamp()} {PromoGenerator.blue} Enter Number Of Threads : "))
        with open("proxies.txt") as f:
            self.proxies = f.read().splitlines()

        self.set_window_icon("icon.ico")

    def start_promo_generation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = {executor.submit(self.generate_promo, choice(self.proxies) if self.proxies else None): i for i in range(self.num_threads)}
            try:
                chunk_size = 10  # Adjust chunk size as needed
                results_buffer = []

                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    results_buffer.append(result)

                    if len(results_buffer) >= chunk_size:
                        self.process_results(results_buffer)
                        results_buffer = []

                # Process any remaining results
                if results_buffer:
                    self.process_results(results_buffer)
            except KeyboardInterrupt:
                pass

    def process_results(self, results):
        for result in results:
            if "rate-limited" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.yellow} You are being rate-limited!")
                quit()
            elif "Request failed" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.red} {result}")
            elif "Max Retries" not in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.green} Generated Promo Link : {result}")
                with open("promos.txt", "a") as f:
                    f.write(f"{result}\n")

    def generate_promo(self, proxy):
        generator = PromoGenerator(proxy=proxy)
        while True:
            result = generator.generate_promo()
            if "rate-limited" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.yellow} You are being rate-limited!")
                quit()
            elif "Request failed" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.red} {result}")
            elif "Max Retries" not in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.green} Generated Promo Link : {result}")
                with open("promos.txt", "a") as f:
                    f.write(f"{result}\n")

    def set_window_icon(self, icon_filename):
        icon_path = os.path.abspath(icon_filename)
        if os.name == 'nt' and os.path.isfile(icon_path):
            try:
                ctypes.windll.kernel32.SetConsoleIcon(ctypes.windll.shell32.ExtractIconW(0, icon_path, 0))
            except Exception as e:
                print(f"Failed to set the window icon: {e}")

if __name__ == "__main__":
    manager = PromoManager()
    manager.start_promo_generation()

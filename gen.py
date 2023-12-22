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

    def __init__(self, proxy=None):
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

        retry_attempts = 3  # You can adjust the number of retry attempts

        for _ in range(retry_attempts):
            try:
                with requests.Session() as session:
                    if self.proxy:
                        # ... (proxy setup remains unchanged)
                        response = session.post(url, json=data, headers=headers, proxies={'http': formatted_proxy, 'https': formatted_proxy}, timeout=5)
                    else:
                        response = session.post(url, json=data, headers=headers, timeout=5)

                if response.status_code == 200:
                    token = response.json().get('token')
                    if token:
                        Counter.count += 1
                        ctypes.windll.kernel32.SetConsoleTitleW(
                            f"Nitro Promo Generator | By Strings"
                            f" | Generated : {Counter.count}")
                        link = f"https://discord.com/billing/partner-promotions/1180231712274387115/{token}"
                        return link
                elif response.status_code == 429:
                    return "rate-limited"
                elif response.status_code == 504:  # Skip handling 504 errors
                    continue
                else:
                    return f"Request failed : {response.status_code}"
            except requests.exceptions.ReadTimeout:
                # Hide the specific timeout error
                continue
            except requests.exceptions.RequestException as e:
                print(f"{self.get_timestamp()} {self.red} Request Failed : {e}")
                time.sleep(1)  # Add a small delay before retrying

        return f"Max retry attempts reached"

    @staticmethod
    def get_timestamp():
        time_idk = time.strftime('%H:%M:%S')
        return f'[\x1b[90m{time_idk}\x1b[0m]'

class PromoManager:
    def __init__(self):
        self.num_threads = int(input(f"{PromoGenerator.get_timestamp()} {PromoGenerator.blue} Enter Number Of Threads : "))
        with open("proxies.txt") as f:
            self.proxies = f.read().splitlines()

    def start_promo_generation(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.num_threads) as executor:
            futures = {executor.submit(self.generate_promo): i for i in range(self.num_threads)}
            try:
                for future in concurrent.futures.as_completed(futures):
                    result = future.result()
                    if "rate-limited" in result:
                        print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.yellow} You are being rate-limited!")
                    elif "Request failed" in result:
                        print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.red} {result}")
                    else:
                        print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.green} Generated Promo Link : {result}")
                        with open("promos.txt", "a") as f:
                            f.write(f"{result}\n")
            except KeyboardInterrupt:
                pass

    def generate_promo(self):
        proxy = choice(self.proxies) if self.proxies else None
        generator = PromoGenerator(proxy)
        while True:
            result = generator.generate_promo()
            if "rate-limited" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.yellow} You are being rate-limited!")
            elif "Request failed" in result:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.red} {result}")
            else:
                print(f"{PromoGenerator.get_timestamp()} {PromoGenerator.green} Generated Promo Link : {result}")
                with open("promos.txt", "a") as f:
                    f.write(f"{result}\n")

if __name__ == "__main__":
    manager = PromoManager()
    manager.start_promo_generation()

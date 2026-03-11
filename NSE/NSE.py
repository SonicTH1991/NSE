import requests
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(category=InsecureRequestWarning)

class NginxAutoAuditor:
    def __init__(self):
        self.target = None
        self.threads = 20
        self.wordlists_dir = "wordlists"
        self.output_file = "valid_results.txt"
        self.headers = {'User-Agent': 'Mozilla/5.0 (NSA-Auditor-v1.4)'}
        self.current_wordlist = ""

    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log_result(self, message):
        with open(self.output_file, "a", encoding="utf-8") as f:
            f.write(f"[{time.strftime('%H:%M:%S')}] [Dict: {self.current_wordlist}] {message}\n")

    def request_worker(self, path):
        if not self.target: return
        url = f"{self.target}/{path.lstrip('/')}"
        try:
            # allow_redirects=False помогает ловить именно 200/401/403, а не редиректы на главную
            r = requests.get(url, verify=False, timeout=3, headers=self.headers, allow_redirects=False)
            
            if r.status_code == 200:
                print(f"\n[+] [200 OK] {url}")
                self.log_result(f"FOUND: {url}")
            elif r.status_code == 401:
                print(f"\n[!] [401 Auth] {url}")
                self.log_result(f"ADMIN PANEL: {url}")
            elif r.status_code == 403:
                # 403 часто интересны, но их может быть много, выводим кратко
                print(f"\n[-] [403 Forbidden] {url}")
            else:
                # Индикатор работы для 404
                print(f"[Scanning {self.current_wordlist}] Testing: {path[:20]}...", end='\r')
        except:
            pass

    def run_all_wordlists(self):
        if not self.target:
            print("[!] Сначала укажите цель (пункт 1)!"); time.sleep(2); return

        if not os.path.exists(self.wordlists_dir):
            os.makedirs(self.wordlists_dir)
            print(f"[!] Папка '{self.wordlists_dir}' была пуста. Положите туда .txt файлы.")
            input("Нажмите Enter..."); return

        files = [f for f in os.listdir(self.wordlists_dir) if f.endswith('.txt')]
        
        if not files:
            print(f"[!] В папке '{self.wordlists_dir}' нет .txt файлов!")
            input("Нажмите Enter..."); return

        print(f"[*] Найдено словарей: {len(files)}")
        self.log_result(f"--- ЗАПУСК СКАНИРОВАНИЯ ЦЕЛИ: {self.target} ---")

        for wordlist in files:
            self.current_wordlist = wordlist
            path_to_file = os.path.join(self.wordlists_dir, wordlist)
            
            with open(path_to_file, 'r', encoding='utf-8', errors='ignore') as f:
                paths = f.read().splitlines()

            print(f"\n\n>>> Текущий словарь: {wordlist} ({len(paths)} записей)")
            
            with ThreadPoolExecutor(max_workers=self.threads) as executor:
                executor.map(self.request_worker, paths)

        print(f"\n\n[+++] ВСЕ СЛОВАРИ ПРОВЕРЕНЫ. Результаты в {self.output_file}")
        input("Нажмите Enter...")

    def main_menu(self):
        while True:
            self.clear_screen()
            print("="*50)
            print(f" NGINX BATCH AUDITOR v1.4")
            print(f" Target: {self.target if self.target else 'Not set'}")
            print(f" Threads: {self.threads} | Folder: /{self.wordlists_dir}")
            print("="*50)
            print("1. Указать цель (URL)")
            print("2. Настроить потоки (Threads)")
            print("3. ЗАПУСТИТЬ ПРОВЕРКУ ВСЕХ СЛОВАРЕЙ")
            print("0. Выход")
            
            choice = input("\nВыбор > ")

            if choice == '1':
                self.target = input("Введите URL (например, http://192.168.1.1): ").strip().rstrip('/')
            elif choice == '2':
                try: self.threads = int(input("Потоков (1-100): "))
                except: print("Ошибка ввода")
            elif choice == '3':
                self.run_all_wordlists()
            elif choice == '0':
                break

if __name__ == "__main__":
    app = NginxAutoAuditor()
    app.main_menu()
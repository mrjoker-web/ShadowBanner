#!/usr/bin/env python3
# ============================================================
#   ShadowBanner — Banner Grabber Tool
#   Author  : Mr Joker
#   Version : 1.0
#   GitHub  : https://github.com/mrjoker-web
#   Usage   : python shadowbanner.py -t host
#             python shadowbanner.py -l hosts.txt
# ============================================================

import socket
import ssl
import json
import argparse
import threading
import time
import sys
import os
import requests
from datetime import datetime
from queue import Queue

# ─── Colorama (fallback seguro para Termux) ──────────────────
try:
    from colorama import init, Fore, Style
    init(autoreset=True)
    RED     = Fore.RED
    GREEN   = Fore.GREEN
    YELLOW  = Fore.YELLOW
    CYAN    = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    WHITE   = Fore.WHITE
    BOLD    = Style.BRIGHT
    RESET   = Style.RESET_ALL
except ImportError:
    RED = GREEN = YELLOW = CYAN = MAGENTA = WHITE = BOLD = RESET = ""

# ─── Configuração ────────────────────────────────────────────
VERSION   = "1.0"
TIMEOUT   = 3       # segundos por ligação
MAX_RECV  = 1024    # bytes do banner

# Portas alvo com nome do serviço
PORTS = {
    21:    "FTP",
    22:    "SSH",
    23:    "Telnet",
    25:    "SMTP",
    80:    "HTTP",
    110:   "POP3",
    143:   "IMAP",
    443:   "HTTPS",
    3306:  "MySQL",
    5432:  "PostgreSQL",
    6379:  "Redis",
    8080:  "HTTP-Alt",
    8443:  "HTTPS-Alt",
    27017: "MongoDB",
}

# ─── Banner ASCII ─────────────────────────────────────────────
def print_banner():
    os.system("clear" if os.name == "posix" else "cls")
    print(f"""
{CYAN}{BOLD}
 ███████╗██╗  ██╗ █████╗ ██████╗  ██████╗ ██╗    ██╗
 ██╔════╝██║  ██║██╔══██╗██╔══██╗██╔═══██╗██║    ██║
 ███████╗███████║███████║██║  ██║██║   ██║██║ █╗ ██║
 ╚════██║██╔══██║██╔══██║██║  ██║██║   ██║██║███╗██║
 ███████║██║  ██║██║  ██║██████╔╝╚██████╔╝╚███╔███╔╝
 ╚══════╝╚═╝  ╚═╝╚═╝  ╚═╝╚═════╝  ╚═════╝  ╚══╝╚══╝
{RESET}
{MAGENTA}{BOLD}  ██████╗  █████╗ ███╗   ██╗███╗   ██╗███████╗██████╗
  ██╔══██╗██╔══██╗████╗  ██║████╗  ██║██╔════╝██╔══██╗
  ██████╔╝███████║██╔██╗ ██║██╔██╗ ██║█████╗  ██████╔╝
  ██╔══██╗██╔══██║██║╚██╗██║██║╚██╗██║██╔══╝  ██╔══██╗
  ██████╔╝██║  ██║██║ ╚████║██║ ╚████║███████╗██║  ██║
  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
{RESET}
{WHITE}{'─'*55}
  {CYAN}Version:{RESET} {VERSION}    {CYAN}Author:{RESET} Mr Joker
  {CYAN}GitHub:{RESET}  github.com/mrjoker-web
  {CYAN}Mode:{RESET}    Banner Grabber | Service Detection
{WHITE}{'─'*55}{RESET}
""")

# ─── Progress bar simples ─────────────────────────────────────
def progress_bar(current, total, prefix=""):
    bar_len = 30
    filled  = int(bar_len * current / total)
    bar     = "█" * filled + "░" * (bar_len - filled)
    pct     = current / total * 100
    sys.stdout.write(f"\r  {CYAN}{prefix}[{bar}] {pct:.1f}%{RESET}")
    sys.stdout.flush()
    if current == total:
        print()

# ─── Grab via socket (FTP, SSH, SMTP, etc.) ───────────────────
def grab_socket_banner(host: str, port: int) -> str | None:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(TIMEOUT)
        s.connect((host, port))
        banner = s.recv(MAX_RECV).decode("utf-8", errors="ignore").strip()
        s.close()
        return banner if banner else None
    except Exception:
        return None

# ─── Grab via HTTP/HTTPS (headers) ────────────────────────────
def grab_http_banner(host: str, port: int) -> dict | None:
    scheme = "https" if port in (443, 8443) else "http"
    url    = f"{scheme}://{host}:{port}" if port not in (80, 443) else f"{scheme}://{host}"
    try:
        r = requests.get(url, timeout=TIMEOUT, verify=False,
                         headers={"User-Agent": "ShadowBanner/1.0"})
        info = {}
        for key in ["Server", "X-Powered-By", "X-Generator",
                    "X-AspNet-Version", "Via", "X-Backend-Server"]:
            val = r.headers.get(key)
            if val:
                info[key] = val
        info["Status-Code"] = str(r.status_code)
        # Título da página
        title = ""
        if "<title>" in r.text.lower():
            start = r.text.lower().find("<title>") + 7
            end   = r.text.lower().find("</title>", start)
            title = r.text[start:end].strip()[:80]
        if title:
            info["Page-Title"] = title
        return info if info else None
    except Exception:
        return None

# ─── Scan de um host ──────────────────────────────────────────
def scan_host(host: str) -> dict:
    result = {
        "host"      : host,
        "ip"        : None,
        "timestamp" : datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "services"  : []
    }

    # Resolver IP
    try:
        result["ip"] = socket.gethostbyname(host)
    except Exception:
        result["ip"] = "N/A"

    for port, service in PORTS.items():
        banner_data = {}

        if service in ("HTTP", "HTTPS", "HTTP-Alt", "HTTPS-Alt"):
            data = grab_http_banner(host, port)
            if data:
                banner_data = data
        else:
            raw = grab_socket_banner(host, port)
            if raw:
                banner_data = {"Banner": raw}

        if banner_data:
            result["services"].append({
                "port"    : port,
                "service" : service,
                "info"    : banner_data
            })

    return result

# ─── Print resultado de um host ───────────────────────────────
def print_result(result: dict):
    host = result["host"]
    ip   = result["ip"]
    svcs = result["services"]

    print(f"\n{WHITE}{'═'*55}{RESET}")
    print(f"  {BOLD}{CYAN}Target:{RESET} {host}  {YELLOW}({ip}){RESET}")
    print(f"  {CYAN}Time:{RESET}   {result['timestamp']}")
    print(f"{WHITE}{'─'*55}{RESET}")

    if not svcs:
        print(f"  {RED}[!] Sem banners encontrados.{RESET}")
    else:
        for svc in svcs:
            port    = svc["port"]
            service = svc["service"]
            info    = svc["info"]
            print(f"\n  {GREEN}[+]{RESET} {BOLD}Porta {port}{RESET} — {MAGENTA}{service}{RESET}")
            for k, v in info.items():
                print(f"      {CYAN}{k:<18}{RESET} {v}")

    print(f"{WHITE}{'═'*55}{RESET}")

# ─── Guardar outputs ──────────────────────────────────────────
def save_txt(results: list, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"ShadowBanner — Results\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 55 + "\n\n")
        for r in results:
            f.write(f"Host    : {r['host']}\n")
            f.write(f"IP      : {r['ip']}\n")
            f.write(f"Time    : {r['timestamp']}\n")
            if r["services"]:
                for svc in r["services"]:
                    f.write(f"\n  [{svc['port']}] {svc['service']}\n")
                    for k, v in svc["info"].items():
                        f.write(f"    {k}: {v}\n")
            else:
                f.write("  No banners found.\n")
            f.write("\n" + "=" * 55 + "\n\n")

def save_json(results: list, filename: str):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

# ─── Worker multi-thread ──────────────────────────────────────
_lock    = threading.Lock()
_results = []

def worker(queue: Queue, total: int, done_counter: list):
    while not queue.empty():
        host = queue.get()
        result = scan_host(host)
        with _lock:
            _results.append(result)
            done_counter[0] += 1
            progress_bar(done_counter[0], total, prefix=" Scanning ")
            print_result(result)
        queue.task_done()

# ─── Main ─────────────────────────────────────────────────────
def main():
    print_banner()

    parser = argparse.ArgumentParser(
        description="ShadowBanner — Banner Grabber for Ethical Hackers",
        formatter_class=argparse.RawTextHelpFormatter
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-t", "--target",
                       help="Host único  (ex: example.com ou 192.168.1.1)")
    group.add_argument("-l", "--list",
                       help="Ficheiro com lista de hosts (um por linha)")
    parser.add_argument("--threads", type=int, default=10,
                        help="Número de threads (default: 10)")
    parser.add_argument("-o", "--output", default="shadow_banners",
                        help="Nome base dos ficheiros de output (default: shadow_banners)")
    args = parser.parse_args()

    # Montar lista de hosts
    hosts = []
    if args.target:
        hosts = [args.target.strip()]
    else:
        try:
            with open(args.list, "r") as f:
                hosts = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            print(f"\n  {RED}[!] Ficheiro '{args.list}' não encontrado.{RESET}\n")
            sys.exit(1)

    if not hosts:
        print(f"\n  {RED}[!] Nenhum host para escanear.{RESET}\n")
        sys.exit(1)

    print(f"\n  {CYAN}[*]{RESET} Targets carregados : {BOLD}{len(hosts)}{RESET}")
    print(f"  {CYAN}[*]{RESET} Threads            : {BOLD}{args.threads}{RESET}")
    print(f"  {CYAN}[*]{RESET} Portas monitoradas : {BOLD}{len(PORTS)}{RESET}")
    print(f"  {CYAN}[*]{RESET} Timeout            : {BOLD}{TIMEOUT}s{RESET}")
    print(f"\n  {YELLOW}[~]{RESET} A iniciar scan...\n")
    time.sleep(0.5)

    # Queue + threads
    queue        = Queue()
    done_counter = [0]
    for h in hosts:
        queue.put(h)

    threads = []
    for _ in range(min(args.threads, len(hosts))):
        t = threading.Thread(target=worker, args=(queue, len(hosts), done_counter))
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    # Guardar resultados
    txt_file  = f"{args.output}.txt"
    json_file = f"{args.output}.json"
    save_txt(_results, txt_file)
    save_json(_results, json_file)

    # Resumo final
    total_svcs = sum(len(r["services"]) for r in _results)
    print(f"\n{WHITE}{'═'*55}{RESET}")
    print(f"  {GREEN}{BOLD}[✓] Scan concluído!{RESET}")
    print(f"  {CYAN}Hosts scaneados :{RESET} {len(_results)}")
    print(f"  {CYAN}Banners obtidos :{RESET} {total_svcs}")
    print(f"  {CYAN}Output TXT      :{RESET} {txt_file}")
    print(f"  {CYAN}Output JSON     :{RESET} {json_file}")
    print(f"{WHITE}{'═'*55}{RESET}\n")

# Suprimir avisos SSL (certificados self-signed)
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

if __name__ == "__main__":
    main()

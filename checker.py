#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
========================================================================================
           ███╗   ███╗██╗  ██╗██████╗ ██╗    ██╗   ██╗ ██████╗██╗██╗  ██╗██╗  ██╗
           ████╗ ████║██║  ██║██╔══██╗██║    ██║   ██║██╔════╝██║██║  ██║██║  ██║
           ██╔████╔██║███████║██║  ██║██║    ██║   ██║██║     ██║███████║███████║
           ██║╚██╔╝██║╚════██║██║  ██║██║    ██║   ██║██║     ██║██╔══██║╚════██║
           ██║ ╚═╝ ██║     ██║██████╔╝██║    ╚██████╔╝╚██████╗██║██║  ██║     ██║
           ╚═╝     ╚═╝     ╚═╝╚═════╝ ╚═╝     ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝     ╚═╝
========================================================================================
                 ⚡ M 4 D I ~ U c i H 4  P R O X Y  C H E C K E R  E L I T E ⚡
                    [ CYBER SHARINGAN MULTI-PROTOCOL AUDITOR v4.0 ]
========================================================================================
 Developed with High Accuracy & Performance by: M4DI~UciH4
 Supported Protocols: HTTP, HTTPS, SOCKS4, SOCKS4A, SOCKS5, SOCKS5H
 Features:
   - High-precision Latency Benchmark (ms)
   - Triple-Tier Anonymity Detection (Elite / Anonymous / Transparent)
   - Real SSL / HTTPS CONNECT Tunneling Verification
   - Deep GeoIP & ISP Intelligence (Country, City, Region, ASN, ISP)
   - Multi-stage False-Positive Filtering (Pre-flight TCP Ping + Content Validation)
   - Thread-Safe Real-time Streaming & File Exports (results.txt, json, csv)
   - Auto-Detection Mode for Unspecified IP:Port inputs
   - Built-in Harvester / Scraper for Live Public Proxies
========================================================================================
"""

import sys
import os
import re
import time
import json
import csv
import socket
import argparse
import threading
import shutil
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Check and import required libraries
try:
    import requests
    from requests.adapters import HTTPAdapter
except ImportError:
    print("[!] Critical Error: 'requests' is not installed. Run: pip install requests[socks]")
    sys.exit(1)

try:
    import socks
except ImportError:
    print("[!] Critical Error: 'PySocks' is not installed. Run: pip install PySocks")
    sys.exit(1)

# Rich terminal formatting
try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, BarColumn, TextColumn, TimeElapsedColumn, TimeRemainingColumn
    HAVE_RICH = True
except ImportError:
    HAVE_RICH = False

# Enable ANSI colors for Windows CMD / PowerShell if Rich is absent
if sys.platform == "win32":
    os.system("color")
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

console = Console() if HAVE_RICH else None

# ============================================================================
# BRANDING & ASCII ART
# ============================================================================
BANNER_ART = r"""[bold red]
  ███╗   ███╗██╗  ██╗██████╗ ██╗    ██╗   ██╗ ██████╗██╗██╗  ██╗██╗  ██╗
  ████╗ ████║██║  ██║██╔══██╗██║    ██║   ██║██╔════╝██║██║  ██║██║  ██║
  ██╔████╔██║███████║██║  ██║██║    ██║   ██║██║     ██║███████║███████║
  ██║╚██╔╝██║╚════██║██║  ██║██║    ██║   ██║██║     ██║██╔══██║╚════██║
  ██║ ╚═╝ ██║     ██║██████╔╝██║    ╚██████╔╝╚██████╗██║██║  ██║     ██║
  ╚═╝     ╚═╝     ╚═╝╚═════╝ ╚═╝     ╚═════╝  ╚═════╝╚═╝╚═╝  ╚═╝     ╚═╝[/bold red]
[bold cyan]               >>> CYBER SHARINGAN PROXY ENGINE v4.0 <<<[/bold cyan]
[bold yellow]                    Coded with Pride by: M4DI~UciH4[/bold yellow]
[dim white]      [ Multi-Protocol: HTTP | HTTPS | SOCKS4 | SOCKS5 | Auto-Detection ][/dim white]
"""

# ============================================================================
# DATA STRUCTURES
# ============================================================================
@dataclass
class ProxyItem:
    raw: str
    ip: str
    port: int
    protocol: str = "auto"
    user: Optional[str] = None
    password: Optional[str] = None

@dataclass
class CheckResult:
    proxy: str
    protocol: str
    ip: str
    port: int
    alive: bool
    latency_ms: int = 0
    anonymity: str = "Unknown"  # Elite, Anonymous, Transparent, Dead
    ssl_support: bool = False
    egress_ip: str = ""
    country: str = "Unknown"
    country_code: str = "--"
    city: str = "Unknown"
    isp: str = "Unknown"
    asn: str = "Unknown"
    error: str = ""

    def formatted_line(self) -> str:
        proto_prefix = f"{self.protocol.lower()}://"
        return f"{proto_prefix}{self.proxy}"

# ============================================================================
# PROXY PARSER
# ============================================================================
class ProxyParser:
    REGEX_FULL = re.compile(
        r'^(?:(?P<proto>[a-zA-Z0-9]+)://)?'
        r'(?:(?P<user1>[^:@\s]+):(?P<pass1>[^@\s]+)@)?'
        r'(?P<ip>(?:\d{1,3}\.){3}\d{1,3}):(?P<port>\d{2,5})'
        r'(?::(?P<user2>[^:\s]+):(?P<pass2>[^\s]+))?$'
    )

    @classmethod
    def parse_line(cls, line: str, default_proto: str = "auto") -> Optional[ProxyItem]:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('//'):
            return None

        line = line.strip('",;\'')
        match = cls.REGEX_FULL.match(line)
        if not match:
            return None

        data = match.groupdict()
        ip = data['ip']
        try:
            port = int(data['port'])
        except ValueError:
            return None

        try:
            octets = [int(x) for x in ip.split('.')]
            if not (all(0 <= o <= 255 for o in octets) and 1 <= port <= 65535):
                return None
        except Exception:
            return None

        proto = (data['proto'] or default_proto).lower()
        user = data['user1'] or data['user2']
        password = data['pass1'] or data['pass2']

        return ProxyItem(
            raw=f"{ip}:{port}",
            ip=ip,
            port=port,
            protocol=proto,
            user=user,
            password=password
        )

# ============================================================================
# GEOIP & THREAD-SAFE CACHE
# ============================================================================
class GeoIPResolver:
    _cache: Dict[str, Dict[str, str]] = {}
    _lock = threading.Lock()

    @classmethod
    def lookup(cls, ip: str) -> Dict[str, str]:
        with cls._lock:
            if ip in cls._cache:
                return cls._cache[ip]

        info = {
            "country": "Unknown",
            "country_code": "--",
            "city": "Unknown",
            "isp": "Unknown",
            "asn": "Unknown"
        }

        # Service 1: ip-api.com
        try:
            url = f"http://ip-api.com/json/{ip}?fields=status,country,countryCode,city,isp,as"
            r = requests.get(url, timeout=3.0)
            if r.status_code == 200:
                data = r.json()
                if data.get("status") == "success":
                    info["country"] = data.get("country", "Unknown")
                    info["country_code"] = data.get("countryCode", "--")
                    info["city"] = data.get("city", "Unknown")
                    info["isp"] = data.get("isp", "Unknown")
                    info["asn"] = data.get("as", "Unknown").split(' ')[0]
                    with cls._lock:
                        cls._cache[ip] = info
                    return info
        except Exception:
            pass

        # Service 2: ipwho.is (Fallback)
        try:
            url = f"https://ipwho.is/{ip}"
            r = requests.get(url, timeout=3.0)
            if r.status_code == 200:
                data = r.json()
                if data.get("success"):
                    info["country"] = data.get("country", "Unknown")
                    info["country_code"] = data.get("country_code", "--")
                    info["city"] = data.get("city", "Unknown")
                    conn = data.get("connection", {})
                    info["isp"] = conn.get("isp", "Unknown")
                    info["asn"] = f"AS{conn.get('asn', '')}"
                    with cls._lock:
                        cls._cache[ip] = info
                    return info
        except Exception:
            pass

        with cls._lock:
            cls._cache[ip] = info
        return info

# ============================================================================
# CORE CHECKER ENGINE
# ============================================================================
class ProxyCheckerEngine:
    ANONYMITY_HEADERS = [
        'x-forwarded-for', 'x-real-ip', 'client-ip', 'forwarded',
        'via', 'proxy-connection', 'x-proxy-id', 'x-forwarded-host',
        'x-forwarded-proto', 'x-forwarded-server', 'proxy-agent'
    ]

    def __init__(self, timeout: int = 5, pre_ping: bool = True):
        self.timeout = timeout
        self.pre_ping = pre_ping
        self.my_real_ip = self._get_my_real_ip()

    def _get_my_real_ip(self) -> str:
        """Fetch local public IP once to accurately calculate anonymity level."""
        endpoints = [
            "https://api.ipify.org?format=json",
            "http://api.ipify.org?format=json",
            "http://ip-api.com/json",
            "https://ifconfig.me/all.json"
        ]
        for ep in endpoints:
            try:
                r = requests.get(ep, timeout=3.0)
                if r.status_code == 200:
                    data = r.json()
                    ip = data.get("ip") or data.get("query")
                    if ip:
                        return ip.strip()
            except Exception:
                continue
        return "127.0.0.1"

    def _quick_tcp_ping(self, ip: str, port: int, timeout: float = 1.5) -> bool:
        """Fast TCP handshake pre-test to instantly filter out dead ports without HTTP overhead."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(timeout)
        try:
            s.connect((ip, port))
            return True
        except Exception:
            return False
        finally:
            try:
                s.close()
            except Exception:
                pass

    def _build_proxy_url(self, proto: str, item: ProxyItem) -> str:
        auth_str = ""
        if item.user and item.password:
            auth_str = f"{item.user}:{item.password}@"
        prefix = proto
        if proto == "socks5":
            prefix = "socks5h"
        elif proto == "socks4":
            prefix = "socks4a"
        return f"{prefix}://{auth_str}{item.ip}:{item.port}"

    def test_single_protocol(self, item: ProxyItem, proto: str) -> Optional[CheckResult]:
        """Verify proxy through a specific protocol with high accuracy."""
        proxy_url = self._build_proxy_url(proto, item)
        proxies = {
            "http": proxy_url,
            "https": proxy_url
        }

        session = requests.Session()
        session.proxies.update(proxies)
        adapter = HTTPAdapter(max_retries=0)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) M4DI~UciH4-Auditor/4.0"
        }

        egress_ip = ""
        latency_ms = 0
        verified = False

        test_endpoints = [
            ("http://api.ipify.org?format=json", "ip"),
            ("http://ip-api.com/json", "query"),
        ]

        for endpoint, key in test_endpoints:
            try:
                t_start = time.perf_counter()
                resp = session.get(endpoint, headers=headers, timeout=self.timeout)
                t_end = time.perf_counter()

                if resp.status_code == 200:
                    try:
                        data = resp.json()
                        reported_ip = data.get(key)
                        if reported_ip and re.match(r'^(?:\d{1,3}\.){3}\d{1,3}$', reported_ip):
                            egress_ip = reported_ip.strip()
                            latency_ms = int((t_end - t_start) * 1000)
                            verified = True
                            break
                    except Exception:
                        pass
            except Exception:
                pass

        if not verified:
            return None

        # Step 2: SSL / HTTPS Support Test (Snappy sub-timeout)
        ssl_support = False
        sub_to = min(2.5, float(self.timeout))
        try:
            r_ssl = session.get("https://api.ipify.org?format=json", headers=headers, timeout=sub_to)
            if r_ssl.status_code == 200:
                ssl_support = True
        except Exception:
            ssl_support = False

        # Step 3: Anonymity Header Inspection (Snappy sub-timeout)
        anonymity = "Elite"
        try:
            r_judge = session.get("http://httpbin.org/get", headers=headers, timeout=sub_to)
            if r_judge.status_code == 200:
                judge_data = r_judge.json()
                req_headers = {k.lower(): str(v) for k, v in judge_data.get("headers", {}).items()}
                origin = judge_data.get("origin", "")

                if self.my_real_ip and (self.my_real_ip in origin or any(self.my_real_ip in v for v in req_headers.values())):
                    anonymity = "Transparent"
                else:
                    found_proxy_headers = any(h in req_headers for h in self.ANONYMITY_HEADERS)
                    anonymity = "Anonymous" if found_proxy_headers else "Elite"
        except Exception:
            if egress_ip and egress_ip != self.my_real_ip:
                anonymity = "Elite"
            else:
                anonymity = "Transparent"

        # Step 4: Geolocation Metadata
        geo = GeoIPResolver.lookup(egress_ip or item.ip)

        display_proto = proto.upper()
        if display_proto == "HTTP" and ssl_support:
            display_proto = "HTTPS"

        return CheckResult(
            proxy=item.raw,
            protocol=display_proto,
            ip=item.ip,
            port=item.port,
            alive=True,
            latency_ms=latency_ms,
            anonymity=anonymity,
            ssl_support=ssl_support,
            egress_ip=egress_ip,
            country=geo["country"],
            country_code=geo["country_code"],
            city=geo["city"],
            isp=geo["isp"],
            asn=geo["asn"]
        )

    def check_proxy(self, item: ProxyItem, force_proto: Optional[str] = None) -> CheckResult:
        if self.pre_ping:
            if not self._quick_tcp_ping(item.ip, item.port):
                return CheckResult(
                    proxy=item.raw,
                    protocol="UNKNOWN",
                    ip=item.ip,
                    port=item.port,
                    alive=False,
                    error="Port unreachable / connection refused"
                )

        target_proto = force_proto or item.protocol

        if target_proto in ["socks5", "socks4", "http", "https"]:
            test_p = "http" if target_proto == "https" else target_proto
            res = self.test_single_protocol(item, test_p)
            if res:
                return res
            return CheckResult(
                proxy=item.raw,
                protocol=target_proto.upper(),
                ip=item.ip,
                port=item.port,
                alive=False,
                error="Handshake failed / timeout"
            )

        # Smart Auto-Detection Mode: Probe SOCKS5, SOCKS4, then HTTP
        test_order = ["socks5", "socks4", "http"]
        if item.port in [80, 8080, 3128, 8888, 8000]:
            test_order = ["http", "socks5", "socks4"]
        elif item.port in [1080, 1081, 9050, 4145]:
            test_order = ["socks5", "socks4", "http"]

        for proto in test_order:
            res = self.test_single_protocol(item, proto)
            if res:
                return res

        return CheckResult(
            proxy=item.raw,
            protocol="ALL",
            ip=item.ip,
            port=item.port,
            alive=False,
            error="All protocols failed"
        )

# ============================================================================
# RESULTS PERSISTENCE & FILE EXPORTER
# ============================================================================
class ResultsManager:
    def __init__(self, output_dir: str = "."):
        self.output_dir = output_dir
        self.lock = threading.Lock()
        self.results_txt_path = os.path.join(output_dir, "results.txt")
        self.root_results_path = "C:\\Users\\qwert\\results.txt"
        self.alive_results: List[CheckResult] = []

        # Initialize results.txt
        with self.lock:
            with open(self.results_txt_path, "w", encoding="utf-8") as f:
                f.write("# =====================================================================\n")
                f.write("# ⚡ M4DI~UciH4 PROXY CHECKER ELITE - LIVE RESULTS ⚡\n")
                f.write("# Branded by: M4DI~UciH4 // CYBER SHARINGAN ENGINE\n")
                f.write(f"# Started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("# =====================================================================\n\n")

    def record_alive(self, res: CheckResult):
        with self.lock:
            self.alive_results.append(res)
            with open(self.results_txt_path, "a", encoding="utf-8") as f:
                f.write(f"{res.formatted_line()} | {res.anonymity.upper()} | {res.latency_ms}ms | SSL:{'YES' if res.ssl_support else 'NO'} | {res.country_code} ({res.country}) | {res.isp}\n")

    def finalize_reports(self, total_checked: int, elapsed_sec: float):
        with self.lock:
            # 1. Update results.txt with complete, versatile layout
            with open(self.results_txt_path, "w", encoding="utf-8") as f:
                f.write("# =====================================================================\n")
                f.write("#       ⚡ M4DI~UciH4 PROXY CHECKER ELITE v4.0 - FINAL AUDIT REPORT ⚡\n")
                f.write("#                      Coded with Pride by: M4DI~UciH4\n")
                f.write("# =====================================================================\n")
                f.write(f"#  Scan Date        : {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"#  Total Checked    : {total_checked}\n")
                f.write(f"#  Alive Proxies    : {len(self.alive_results)}\n")
                dead_count = total_checked - len(self.alive_results)
                f.write(f"#  Dead / Timeout   : {dead_count}\n")
                success_rate = (len(self.alive_results) / total_checked * 100) if total_checked > 0 else 0
                f.write(f"#  Success Rate     : {success_rate:.2f}%\n")
                f.write(f"#  Total Scan Time  : {elapsed_sec:.2f}s\n")
                f.write("# =====================================================================\n\n")

                f.write("# [ 1. DETAILED PROXY AUDIT LIST ]\n")
                f.write("# FORMAT: PROTOCOL://IP:PORT | ANONYMITY | SPEED | SSL | COUNTRY | ISP\n")
                f.write("# ---------------------------------------------------------------------\n")
                for r in self.alive_results:
                    f.write(f"{r.formatted_line()} | {r.anonymity.upper()} | {r.latency_ms}ms | SSL:{'YES' if r.ssl_support else 'NO'} | {r.country_code} ({r.country}) | {r.isp}\n")
                f.write("\n")

                f.write("# [ 2. READY-TO-USE PROXY URLS (FOR SWITCHYOMEGA / CURL / PYTHON) ]\n")
                f.write("# ---------------------------------------------------------------------\n")
                for r in self.alive_results:
                    f.write(f"{r.formatted_line()}\n")
                f.write("\n")

                f.write("# [ 3. PURE IP:PORT LIST (STANDARD INPUT FORMAT) ]\n")
                f.write("# ---------------------------------------------------------------------\n")
                for r in self.alive_results:
                    f.write(f"{r.proxy}\n")
                f.write("\n")

                f.write("# =====================================================================\n")
                f.write("# End of Report - M4DI~UciH4 Proxy Engine\n")

            # 2. Categorized Protocol Files
            socks5_list = [r.formatted_line() for r in self.alive_results if "SOCKS5" in r.protocol]
            socks4_list = [r.formatted_line() for r in self.alive_results if "SOCKS4" in r.protocol]
            http_list = [r.formatted_line() for r in self.alive_results if "HTTP" in r.protocol]

            if socks5_list:
                with open(os.path.join(self.output_dir, "results_socks5.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(socks5_list) + "\n")

            if socks4_list:
                with open(os.path.join(self.output_dir, "results_socks4.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(socks4_list) + "\n")

            if http_list:
                with open(os.path.join(self.output_dir, "results_http.txt"), "w", encoding="utf-8") as f:
                    f.write("\n".join(http_list) + "\n")

            # 3. Export JSON
            json_data = [asdict(r) for r in self.alive_results]
            with open(os.path.join(self.output_dir, "results.json"), "w", encoding="utf-8") as f:
                json.dump(json_data, f, indent=2)

            # 4. Export CSV
            with open(os.path.join(self.output_dir, "results.csv"), "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Proxy", "Protocol", "IP", "Port", "Latency_ms", "Anonymity", "SSL", "Country", "CountryCode", "City", "ISP", "ASN", "EgressIP"])
                for r in self.alive_results:
                    writer.writerow([r.proxy, r.protocol, r.ip, r.port, r.latency_ms, r.anonymity, r.ssl_support, r.country, r.country_code, r.city, r.isp, r.asn, r.egress_ip])

            # 5. Mirror to C:\Users\qwert\results.txt
            try:
                if os.path.abspath(self.results_txt_path) != os.path.abspath(self.root_results_path):
                    shutil.copy2(self.results_txt_path, self.root_results_path)
            except Exception:
                pass

# ============================================================================
# CONTROLLER & MULTI-THREAD RUNNER
# ============================================================================
def run_proxy_checker(
    proxies: List[ProxyItem],
    mode: str = "auto",
    threads: int = 50,
    timeout: int = 5,
    pre_ping: bool = True,
    output_dir: str = "."
) -> List[CheckResult]:
    if not proxies:
        if HAVE_RICH:
            console.print("[bold red][!] No valid proxies provided to check.[/bold red]")
        else:
            print("[!] No valid proxies provided to check.")
        return []

    engine = ProxyCheckerEngine(timeout=timeout, pre_ping=pre_ping)
    res_manager = ResultsManager(output_dir=output_dir)

    total_proxies = len(proxies)
    checked_count = 0
    alive_count = 0
    dead_count = 0

    stats_lock = threading.Lock()
    start_time = time.time()

    if HAVE_RICH:
        console.print(Panel(
            f"[bold green]Starting M4DI~UciH4 Multi-Thread Engine[/bold green]\n"
            f"[cyan]Total Proxies:[/cyan] {total_proxies} | [cyan]Threads:[/cyan] {threads} | [cyan]Timeout:[/cyan] {timeout}s | [cyan]Mode:[/cyan] {mode.upper()}\n"
            f"[yellow]Real IP Detected:[/yellow] {engine.my_real_ip} (Anonymity Baseline)\n"
            f"[white]Results will be saved to: [bold green]results.txt[/bold green][/white]",
            title="[bold red]⚡ CYBER SHARINGAN INITIALIZED ⚡[/bold red]",
            border_style="red"
        ))

        progress = Progress(
            TextColumn("[bold cyan]{task.description}"),
            BarColumn(bar_width=40, style="red", complete_style="bold green"),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TextColumn("• [bold green]{task.fields[alive]} Alive[/bold green]"),
            TextColumn("• [bold red]{task.fields[dead]} Dead[/bold red]"),
            TimeElapsedColumn(),
            TimeRemainingColumn(),
            console=console
        )
        task_id = progress.add_task("Checking Proxies...", total=total_proxies, alive=0, dead=0)
    else:
        print(f"\n[+] Starting M4DI~UciH4 Checker on {total_proxies} proxies (Threads: {threads}, Mode: {mode.upper()})...")
        progress = None

    def worker(item: ProxyItem) -> CheckResult:
        nonlocal checked_count, alive_count, dead_count
        force_p = None if mode == "auto" else mode
        res = engine.check_proxy(item, force_proto=force_p)

        with stats_lock:
            checked_count += 1
            if res.alive:
                alive_count += 1
                res_manager.record_alive(res)
                if HAVE_RICH:
                    lat_color = "green" if res.latency_ms < 400 else "yellow" if res.latency_ms < 1000 else "red"
                    anon_color = "bold magenta" if res.anonymity == "Elite" else "bold blue" if res.anonymity == "Anonymous" else "dim"
                    proto_color = "bold cyan" if "SOCKS5" in res.protocol else "bold yellow" if "SOCKS4" in res.protocol else "bold green"

                    console.print(
                        f"  [bold green][+ ALIVE][/bold green] "
                        f"[{proto_color}]{res.protocol:<6}[/{proto_color}] "
                        f"[bold white]{res.proxy:<21}[/bold white] "
                        f"[{lat_color}]{res.latency_ms:>4}ms[/{lat_color}] "
                        f"[{anon_color}]{res.anonymity:<11}[/{anon_color}] "
                        f"[cyan]{res.country_code} ({res.country})[/cyan] "
                        f"[dim]{res.isp[:25]}[/dim]"
                    )
                else:
                    print(f"  [+ ALIVE] [{res.protocol}] {res.proxy} | {res.latency_ms}ms | {res.anonymity} | {res.country} | {res.isp}")
            else:
                dead_count += 1

            if progress:
                progress.update(task_id, advance=1, alive=alive_count, dead=dead_count)

        return res

    all_results: List[CheckResult] = []
    try:
        if progress:
            with progress:
                with ThreadPoolExecutor(max_workers=threads) as executor:
                    futures = [executor.submit(worker, p) for p in proxies]
                    for f in as_completed(futures):
                        all_results.append(f.result())
        else:
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [executor.submit(worker, p) for p in proxies]
                for f in as_completed(futures):
                    all_results.append(f.result())
    except KeyboardInterrupt:
        if HAVE_RICH:
            console.print("\n[bold yellow][!] Scan aborted by user (Ctrl+C). Saving current findings...[/bold yellow]")
        else:
            print("\n[!] Scan aborted by user. Saving current findings...")

    elapsed = time.time() - start_time
    res_manager.finalize_reports(total_checked=checked_count, elapsed_sec=elapsed)

    if HAVE_RICH:
        table = Table(title="⚡ M4DI~UciH4 PROXY AUDIT SUMMARY ⚡", style="red")
        table.add_column("Metric", style="bold cyan")
        table.add_column("Value", style="bold white")

        table.add_row("Total Scanned", str(checked_count))
        table.add_row("Alive Proxies", f"[bold green]{len(res_manager.alive_results)}[/bold green]")
        table.add_row("Dead / Timed Out", f"[bold red]{dead_count}[/bold red]")
        rate = (len(res_manager.alive_results) / checked_count * 100) if checked_count > 0 else 0
        table.add_row("Success Ratio", f"{rate:.1f}%")
        table.add_row("Elapsed Time", f"{elapsed:.2f} seconds")
        table.add_row("Results Saved In", f"[bold green]{os.path.abspath(res_manager.results_txt_path)}[/bold green]")

        console.print("\n")
        console.print(table)
        console.print(f"[bold yellow]Branded by M4DI~UciH4 — Scan complete without bugs![/bold yellow]\n")
    else:
        print("\n" + "=" * 50)
        print("⚡ M4DI~UciH4 PROXY AUDIT SUMMARY ⚡")
        print("=" * 50)
        print(f"Total Scanned   : {checked_count}")
        print(f"Alive Proxies   : {len(res_manager.alive_results)}")
        print(f"Dead Proxies    : {dead_count}")
        print(f"Elapsed Time    : {elapsed:.2f}s")
        print(f"Results Saved In: {os.path.abspath(res_manager.results_txt_path)}")
        print("=" * 50)

    return res_manager.alive_results

# ============================================================================
# INTERACTIVE CLI & ENTRY POINT
# ============================================================================
def show_banner():
    if HAVE_RICH:
        console.print(BANNER_ART)
    else:
        print("""
====================================================================
           M4DI~UciH4 PROXY CHECKER & SOCKS AUDITOR v4.0
                Coded by: M4DI~UciH4 (Cyber Sharingan)
====================================================================
        """)

def interactive_menu(script_dir: str):
    show_banner()
    default_file = os.path.join(script_dir, "proxies.txt")

    print("[ MENU SELECTION ]")
    print("  [1] Check Proxies from File (Default: proxies.txt)")
    print("  [2] Check Single Proxy (e.g. 167.99.3.26:9050)")
    print("  [3] Auto-Scrape & Check Fresh Live Proxies (SOCKS5, SOCKS4, HTTP)")
    print("  [4] Exit")
    print("-" * 50)

    choice = input("Select option [1-4] (Default: 1): ").strip() or "1"

    if choice == "4":
        print("[*] Goodbye! - M4DI~UciH4")
        sys.exit(0)

    proxies_to_check: List[ProxyItem] = []

    if choice == "1":
        file_path = input(f"Enter proxy file path (Press Enter for '{default_file}'): ").strip() or default_file
        if not os.path.exists(file_path):
            print(f"[!] Error: File '{file_path}' does not exist.")
            sys.exit(1)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                item = ProxyParser.parse_line(line)
                if item:
                    proxies_to_check.append(item)
        print(f"[+] Loaded {len(proxies_to_check)} valid proxy entries from file.")

    elif choice == "2":
        raw_p = input("Enter proxy (Format: IP:PORT or socks5://IP:PORT): ").strip()
        item = ProxyParser.parse_line(raw_p)
        if not item:
            print("[!] Invalid proxy format.")
            sys.exit(1)
        proxies_to_check.append(item)

    elif choice == "3":
        print("\n[+] Scraping fresh public proxies from multiple high-uptime sources...")
        try:
            import scraper
            data = scraper.scrape_proxies("all")
            all_scraped = data.get("socks5", []) + data.get("socks4", []) + data.get("http", [])
            print(f"[+] Total Scraped: {len(all_scraped)} proxies (SOCKS5: {len(data.get('socks5', []))}, SOCKS4: {len(data.get('socks4', []))}, HTTP: {len(data.get('http', []))})")
            limit_str = input(f"How many to check? (Enter for 100, 'all' for {len(all_scraped)}): ").strip() or "100"
            limit = len(all_scraped) if limit_str.lower() == "all" else int(limit_str)
            for raw in all_scraped[:limit]:
                item = ProxyParser.parse_line(raw)
                if item:
                    proxies_to_check.append(item)
        except Exception as e:
            print(f"[!] Scraper failed: {e}")
            sys.exit(1)

    print("\n[ SELECT PROTOCOL MODE ]")
    print("  [1] Auto-Detect Protocol (Smart Probe: HTTP, SOCKS5, SOCKS4) [RECOMMENDED]")
    print("  [2] SOCKS5 Only")
    print("  [3] SOCKS4 Only")
    print("  [4] HTTP / HTTPS Only")
    proto_choice = input("Select mode [1-4] (Default: 1): ").strip() or "1"
    mode_map = {"1": "auto", "2": "socks5", "3": "socks4", "4": "http"}
    mode = mode_map.get(proto_choice, "auto")

    threads_str = input("Threads (Default: 50): ").strip() or "50"
    try:
        threads = int(threads_str)
    except ValueError:
        threads = 50

    run_proxy_checker(
        proxies=proxies_to_check,
        mode=mode,
        threads=threads,
        timeout=5,
        output_dir=script_dir
    )

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    parser = argparse.ArgumentParser(
        description="M4DI~UciH4 PROXY CHECKER ELITE - High-Accuracy Multi-Protocol Proxy Auditor",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-f", "--file", help="Path to proxy list file (e.g. proxies.txt)")
    parser.add_argument("-p", "--proxy", help="Check a single proxy (e.g. 167.99.3.26:9050)")
    parser.add_argument("-t", "--threads", type=int, default=50, help="Number of concurrent threads (default: 50)")
    parser.add_argument("--timeout", type=int, default=5, help="Timeout in seconds for each request (default: 5)")
    parser.add_argument("-m", "--mode", choices=["auto", "socks5", "socks4", "http"], default="auto",
                        help="Protocol mode: auto (default), socks5, socks4, http")
    parser.add_argument("--scrape", action="store_true", help="Auto-scrape public proxies and check them immediately")
    parser.add_argument("--scrape-limit", type=int, default=100, help="Maximum scraped proxies to test (default: 100)")
    parser.add_argument("--no-ping", action="store_true", help="Disable pre-flight TCP port socket ping")
    parser.add_argument("-o", "--output-dir", default=script_dir, help="Directory to save results (default: current script dir)")

    args = parser.parse_args()

    if len(sys.argv) == 1:
        interactive_menu(script_dir)
        return

    show_banner()
    proxies_to_check: List[ProxyItem] = []

    if args.scrape:
        print("[+] Harvesting proxies via M4DI~UciH4 Harvester...")
        try:
            import scraper
            data = scraper.scrape_proxies(args.mode if args.mode != "auto" else "all")
            all_scraped = data.get("socks5", []) + data.get("socks4", []) + data.get("http", [])
            for raw in all_scraped[:args.scrape_limit]:
                item = ProxyParser.parse_line(raw)
                if item:
                    proxies_to_check.append(item)
            print(f"[+] Harvested {len(proxies_to_check)} proxies ready for auditing.")
        except Exception as e:
            print(f"[!] Error in scraper: {e}")
            sys.exit(1)

    elif args.proxy:
        item = ProxyParser.parse_line(args.proxy)
        if not item:
            print(f"[!] Invalid proxy syntax: {args.proxy}")
            sys.exit(1)
        proxies_to_check.append(item)

    elif args.file:
        if not os.path.exists(args.file):
            print(f"[!] Proxy file not found: {args.file}")
            sys.exit(1)
        with open(args.file, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                item = ProxyParser.parse_line(line)
                if item:
                    proxies_to_check.append(item)
        print(f"[+] Loaded {len(proxies_to_check)} proxies from {args.file}")

    run_proxy_checker(
        proxies=proxies_to_check,
        mode=args.mode,
        threads=args.threads,
        timeout=args.timeout,
        pre_ping=not args.no_ping,
        output_dir=args.output_dir
    )

if __name__ == "__main__":
    main()

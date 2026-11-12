"""
=============================================================================
 M4DI~UciH4 PROXY HARVESTER & SCRAPER ENGINE
 Coded with Passion by: M4DI~UciH4
 High-Speed Multi-Source Public Proxy Scraper (HTTP, SOCKS4, SOCKS5)
=============================================================================
"""

import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Set, Dict

# High-uptime curated proxy endpoints
SCRAPE_SOURCES: Dict[str, List[str]] = {
    "socks5": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks5.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks5.txt",
        "https://raw.githubusercontent.com/hookzof/socks5_list/master/proxy.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS5_RAW.txt",
    ],
    "socks4": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/socks4.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/socks4.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/SOCKS4_RAW.txt",
    ],
    "http": [
        "https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
        "https://raw.githubusercontent.com/monosans/proxy-list/main/proxies/http.txt",
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all",
        "https://raw.githubusercontent.com/roosterkid/openproxylist/main/HTTPS_RAW.txt",
    ]
}

IP_PORT_REGEX = re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}:\d{2,5}\b')

def fetch_url(url: str, timeout: int = 8) -> Set[str]:
    """Fetch URL and extract all valid IP:PORT strings."""
    found: Set[str] = set()
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) M4DI~UciH4-Scraper/3.0"}
        resp = requests.get(url, headers=headers, timeout=timeout)
        if resp.status_code == 200:
            matches = IP_PORT_REGEX.findall(resp.text)
            for m in matches:
                ip, port_str = m.split(':')
                port = int(port_str)
                # Filter valid port range and valid IP octets
                if 1 <= port <= 65535:
                    octets = [int(x) for x in ip.split('.')]
                    if all(0 <= o <= 255 for o in octets):
                        found.add(m)
    except Exception:
        pass
    return found

def scrape_proxies(protocol: str = "all", max_threads: int = 15) -> Dict[str, List[str]]:
    """
    Scrape proxies categorized by protocol.
    protocol can be 'all', 'socks5', 'socks4', or 'http'.
    """
    tasks = []
    results: Dict[str, Set[str]] = {"socks5": set(), "socks4": set(), "http": set()}

    categories = ["socks5", "socks4", "http"] if protocol == "all" else [protocol]

    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        future_to_meta = {}
        for cat in categories:
            for url in SCRAPE_SOURCES.get(cat, []):
                future = executor.submit(fetch_url, url)
                future_to_meta[future] = cat

        for future in as_completed(future_to_meta):
            cat = future_to_meta[future]
            try:
                proxies = future.result()
                results[cat].update(proxies)
            except Exception:
                pass

    return {k: sorted(list(v)) for k, v in results.items()}

if __name__ == "__main__":
    print("[+] M4DI~UciH4 Harvester Testing...")
    data = scrape_proxies("socks5")
    print(f"[+] Total SOCKS5 Scraped: {len(data['socks5'])}")
    if data['socks5']:
        print("[+] First 5 proxies:", data['socks5'][:5])

import requests
import json
from config import Protocols, check_node
import base64
from os import path, makedirs


class CheckHost(Protocols):
    def __init__(self, network: Protocols) -> None:
        self.network = network
        self.error_count = 0
        Protocols.__init__(self)
        self._check_links()

    @staticmethod
    def remove_combined_strings(text: str):
        for i in text:
            if not i.isdigit():
                return text[:text.find(i)-1]

    @staticmethod
    def _is_b64(data: str) -> bool:
        try:
            decoded = base64.b64decode(data).decode()
            return True
        except Exception:
            return False

    @staticmethod
    def _vmess_get_host_port(link: str) -> tuple:
        if CheckHost._is_b64(link[8:]):
            link = base64.b64decode(link)
            link = json.loads(link)
            return (link.get('add'), link.get('port'))
        return tuple(link[link.find('@')+1:link.find('?')].split(':'))

    @staticmethod  
    def _outline_get_host_port(link: str) -> tuple:
        try:
            return tuple(link.split('@')[1].split('/')[0].split(':'))
        except:
            print(f'Error to get host and port for outline {link}')
    
    @staticmethod
    def _check_access(host: str, port:int = 443):
        headers = {
            'Accept': 'application/json',
        }

        response = requests.get(f'{check_node}?host={host}&port={port}&timeout=1', headers=headers)
        
        if response.status_code == 200:
            return response.json()['result']['ok']
        return False

    @staticmethod
    def _trojan_get_host_port(link: str):
        return tuple(link[link.find('@')+1:link.find('?')].split(':'))

    def _check_links(self):
        ## Vless
        for link in self.network.vless:
            try:
                _ = self._vmess_get_host_port(link)
                if self._check_access(_[0], _[1]):
                    self.vless = link
            except Exception as er:
                self.error_count += 1
                print(f'Check Error: {link} > {_}')

        ## Vmess
        for link in self.network.vmess:
            try:
                _ = self._vmess_get_host_port(link)
                if self._check_access(_[0], _[1]):
                    self.vmess = link
            except Exception as er:
                self.error_count += 1
                print(f'Check Error: {link} > {_}')

        ## ShadowSocks
        for link in self.network.ss:
            try:
                _ = self._outline_get_host_port(link)
                if self._check_access(_[0], _[1]):
                    self.ss = link
            except:
                self.error_count += 1
                print(f'Check Error: {link} > {_}')
                
        ## Trojan
        for link in self.network.trojan:
            try:
                _ = self._trojan_get_host_port(link)
                if self._check_access(_[0], _[1]):
                    self.trojan = link
            except:
                self.error_count += 1
                print(f'Check Error: {link} > {_}')

        print(f'Tested Links: {len(self.vless)+len(self.vmess)+len(self.ss)+len(self.trojan)}')
        print(f'Error Encounter During Test Link: {self.error_count}')


def save(network: Protocols, save_path: str = None) -> bool:
    save_path = save_path if save_path is not None else './hub/'
    makedirs(save_path, exist_ok=True)  # ایجاد پوشه اگه وجود نداره
    
    with open(path.join(save_path, 'ss.txt'), 'w') as fli:
        for link in network.ss:
            fli.write(f'{link}\n')
        
    with open(path.join(save_path, 'vmess.txt'), 'w') as fli:
        for link in network.vmess:
            fli.write(f'{link}\n')
        
    with open(path.join(save_path, 'vless.txt'), 'w') as fli:
        for link in network.vless:
            fli.write(f'{link}\n')
        
    with open(path.join(save_path, 'trojan.txt'), 'w') as fli:
        for link in network.trojan:
            fli.write(f'{link}\n')

    with open(path.join(save_path, 'merged.txt'), 'w') as fli:
        mrg = []
        mrg.extend(network.ss)
        mrg.extend(network.vmess)
        mrg.extend(network.vless)
        mrg.extend(network.trojan)
        for link in mrg:
            fli.write(f'{link}\n')


def save_b64(network: Protocols, save_path: str = None) -> bool:
    save_path = save_path if save_path is not None else './hub/'
    makedirs(save_path, exist_ok=True)  # ایجاد پوشه اگه وجود نداره

    ss_b64 = ''
    vmess_b64 = ''
    vless_b64 = ''
    trojan_b64 = ''
    mrg = ''
    
    for link in network.ss:
        ss_b64 += link + '\n'
        
    for link in network.vmess:
        vmess_b64 += link + '\n'

    for link in network.vless:
        vless_b64 += link + '\n'
        
    for link in network.trojan:
        trojan_b64 += link + '\n'

    mrg = ss_b64 + vmess_b64 + vless_b64 + trojan_b64

    with open(path.join(save_path, 'ss.txt'), 'w') as fli:
        ss_b64 = base64.b64encode(bytes(ss_b64, 'utf-8')).decode()
        fli.write(ss_b64)
        
    with open(path.join(save_path, 'vmess.txt'), 'w') as fli:
        vmess_b64 = base64.b64encode(bytes(vmess_b64, 'utf-8')).decode()
        fli.write(vmess_b64)
        
    with open(path.join(save_path, 'vless.txt'), 'w') as fli:
        vless_b64 = base64.b64encode(bytes(vless_b64, 'utf-8')).decode()
        fli.write(vless_b64)
        
    with open(path.join(save_path, 'trojan.txt'), 'w') as fli:
        trojan_b64 = base64.b64encode(bytes(trojan_b64, 'utf-8')).decode()
        fli.write(trojan_b64)

    with open(path.join(save_path, 'merged.txt'), 'w') as fli:
        mrg = base64.b64encode(bytes(mrg, 'utf-8')).decode()
        fli.write(mrg)


def resolve_domain_to_ip(domain: str):
    try:
        ip_address = socket.gethostbyname(domain)
        return ip_address
    except:
        print(f"# Error resolving {domain}")
        return None


def get_country(network: Protocols):
    # نگاشت کد کشور به پرچم emoji
    country_flags = {
        'US': '🇺🇸',
        'DE': '🇩🇪',
        'FR': '🇫🇷',
        'GB': '🇬🇧',
        'CA': '🇨🇦',
        'JP': '🇯🇵',
        'CN': '🇨🇳',
        'IR': '🇮🇷',
        'RU': '🇷🇺',
        'UnResolvedDomains': '❓'
    }

    countries = {}

    def _get_country(ip: str, base_api: str = 'https://ipinfo.io/{ip}/json') -> str:
        res = requests.get(base_api.replace('{ip}', ip)).json()
        return res.get('country')

    def _add_to_dict(link: str, country: str):
        if countries.get(country):
            countries[country].append(link)
        else:
            countries[country] = [link]

    # ss
    if network.ss:
        for conf_link in network.ss:
            try:
                ip = resolve_domain_to_ip(CheckHost._outline_get_host_port(conf_link)[0])
                if ip:
                    country = _get_country(ip)
                    _add_to_dict(conf_link, country if country else "UnResolvedDomains")
                else:
                    _add_to_dict(conf_link, "UnResolvedDomains")
            except Exception as err:
                print(f"# {err}")
                _add_to_dict(conf_link, "UnResolvedDomains")

    # vmess
    if network.vmess:
        for conf_link in network.vmess:
            try:
                ip = resolve_domain_to_ip(CheckHost._vmess_get_host_port(conf_link)[0])
                if ip:
                    country = _get_country(ip)
                    _add_to_dict(conf_link, country if country else "UnResolvedDomains")
                else:
                    _add_to_dict(conf_link, "UnResolvedDomains")
            except Exception as err:
                print(f"# {err}")
                _add_to_dict(conf_link, "UnResolvedDomains")

    # vless
    if network.vless:
        for conf_link in network.vless:
            try:
                ip = resolve_domain_to_ip(CheckHost._outline_get_host_port(conf_link)[0])
                if ip:
                    country = _get_country(ip)
                    _add_to_dict(conf_link, country if country else "UnResolvedDomains")
                else:
                    _add_to_dict(conf_link, "UnResolvedDomains")
            except Exception as err:
                print(f"# {err}")
                _add_to_dict(conf_link, "UnResolvedDomains")

    # trojan
    if network.trojan:
        for conf_link in network.trojan:
            try:
                ip = resolve_domain_to_ip(CheckHost._trojan_get_host_port(conf_link)[0])
                if ip:
                    country = _get_country(ip)
                    _add_to_dict(conf_link, country if country else "UnResolvedDomains")
                else:
                    _add_to_dict(conf_link, "UnResolvedDomains")
            except Exception as err:
                print(f"# {err}")
                _add_to_dict(conf_link, "UnResolvedDomains")

    class meta:
        def __init__(self, data: dict):
            self.data = data

        def save(self, save_path: str = './hub/'):
            makedirs(save_path, exist_ok=True)  # ایجاد پوشه اگه وجود نداره
            for _country in self.data.keys():
                flag = country_flags.get(_country, '❓')  # پرچم پیش‌فرض
                file_name = f'{flag}_{_country}.txt'  # اضافه کردن پرچم به نام فایل
                with open(path.join(save_path, file_name), 'w') as fli:
                    for link in self.data.get(_country):
                        fli.write(f'{link}\n\n')

        def print(self):
            """چاپ کد کشورها با پرچم"""
            return [f'{country_flags.get(color, "❓")} {color}' for color in self.data.keys()]

        def count(self):
            return len(self.data.keys())

    return meta(countries)


class CheckSelf(Protocols):
    def __init__(self, network: Protocols):
        Protocols.__init__(self)
        self.error_count = 0
        self.network = network
        self._check_links()

    @staticmethod
    def tcp_test(ip: str, port: str, timeout: int = 2.5):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            port = int(CheckHost.remove_combined_strings(port))
            result = sock.connect_ex((ip, port))
            if result == 0:
                return True
            else:
                return False
        except Exception as err:
            print(f"# Error on TCP test [{ip}:{port}] -> {err}")
            return False

    def _check_links(self):
        # vless
        for link in self.network.vless:
            try:
                _ = CheckHost._vmess_get_host_port(link)
                if self.tcp_test(_[0], _[1]):
                    self.vless = link
            except Exception as err:
                self.error_count += 1
                print(f'# Check Error -> {link} > {_}')

        # vmess
        for link in self.network.vmess:
            try:
                _ = CheckHost._vmess_get_host_port(link)
                if self.tcp_test(_[0], _[1]):
                    self.vmess = link
            except Exception as err:
                self.error_count += 1
                print(f'# Check Error -> {link} > {_}')

        # ShadowSocks
        for link in self.network.ss:
            try:
                _ = CheckHost._outline_get_host_port(link)
                if self.tcp_test(_[0], _[1]):
                    self.ss = link
            except:
                self.error_count += 1
                print(f'# Check Error -> {link} > {_}')

        # Trojan
        for link in self.network.trojan:
            try:
                _ = CheckHost._trojan_get_host_port(link)
                if self.tcp_test(_[0], _[1]):
                    self.trojan = link
            except:
                self.error_count += 1
                print(f'# Check Error -> {link} > {_}')

        print(f'Tested Links: {len(self.vless) + len(self.vmess) + len(self.ss) + len(self.trojan)}')
        print(f'Error Encounter During Test Link: {self.error_count}')

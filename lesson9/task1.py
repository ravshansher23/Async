from ipaddress import ip_address
from subprocess import Popen, PIPE

def host_ping(ip_list: list):
    results = {'Доступные узлы': "", 'Недоступные узлы': ""}
    for ip in ip_list:
        try:
            address = ip_address(ip)
            proc = Popen(f"ping {address} -w 500 -n 1", shell=False, stdout=PIPE)
            proc.wait()

            if proc.returncode == 0:
                results['Доступные узлы'] += f"{str(address)}\n"
                res_string = f'{address} - Узел доступен'
            else:
                results['Недоступные узлы'] += f"{str(address)}\n"
                res_string = f'{address} - Узел недоступен'
            print(res_string)
        except Exception as err:
            print(err)
    return results

if __name__ == '__main__':
    ip_addresses = ['gb.ru', '8.8.8.8', '192.168.0.103', '192.168.0.104']
    host_ping(ip_addresses)
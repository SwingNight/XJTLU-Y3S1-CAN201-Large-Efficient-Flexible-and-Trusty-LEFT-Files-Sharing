import argparse
import threading
from Server import run_server
from Client import run_client


def _argparse():
    parser = argparse.ArgumentParser(description="Get IP address")
    parser.add_argument('--ip', dest='ip')
    args = parser.parse_args()
    ip_address = args.ip.split(',')
    return ip_address


def run():
    run_server()


ip = _argparse()
ip_b = ip[0]
ip_c = ip[1]


if __name__ == "__main__":
    thread = threading.Thread(target=run)
    thread.start()
    run_client(ip_b, ip_c)

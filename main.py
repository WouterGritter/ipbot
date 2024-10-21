import os
import re
import sys
import time
from typing import Optional

import requests
from discord_webhook import DiscordWebhook


def fetch_public_ip(ip_service) -> Optional[str]:
    try:
        response = requests.get(ip_service)
    except:
        return None

    if response.status_code != 200:
        return None

    ip = response.text
    if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
        return None

    return ip


def main():
    ip_service = os.getenv('IP_SERVICE', 'https://ifconfig.me/ip')
    check_interval = int(os.getenv('CHECK_INTERVAL', 15 * 60))
    discord_webhook_url = os.getenv('DISCORD_WEBHOOK_URL')

    print(f'ipbot version {os.getenv("IMAGE_VERSION")}')

    if discord_webhook_url is None or discord_webhook_url == '':
        print('Please provide a Discord webhook URL through the DISCORD_WEBHOOK_URL environment variable.')
        sys.exit(1)

    print(f'IP_SERVICE={ip_service}')
    print(f'CHECK_INTERVAL={check_interval}')
    print(f'DISCORD_WEBHOOK_URL={discord_webhook_url[:32]}...')

    ip_address = fetch_public_ip(ip_service)
    if ip_address is None:
        print('Couldn\'t fetch IP address at startup. Exiting.')
        sys.exit(1)

    print(f'First IP address fetch: {ip_address}')

    while True:
        time.sleep(check_interval)

        new_ip_address = fetch_public_ip(ip_service)
        if new_ip_address is None:
            print('Error fetching IP address!')
            continue

        if new_ip_address != ip_address:
            print(f'IP address changed from {ip_address} to {new_ip_address}')

            discord_message = f':repeat: Detected an IP address change! New IP address: `{new_ip_address}`'
            DiscordWebhook(url=discord_webhook_url, content=discord_message).execute()

            ip_address = new_ip_address


if __name__ == '__main__':
    main()

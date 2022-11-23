import datetime
import logging
import os

import azure.functions as func

from azlet.azertbot import AzertBot

def main(mytimer: func.TimerRequest) -> None:
    bot = AzertBot(keyvault_name=os.environ.get('keyVaultName'),
                   dns_subscription=os.environ.get("dnsSubscription"),
                   dns_rg=os.environ.get("dnsRg"),
                   zone=os.environ.get("dnsZoneName"))
    bot.rotate()

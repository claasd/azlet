import pem
import re
from typing import Optional
import logging

import OpenSSL
import sewer.client
from datetime import datetime, timezone

from azure.core.exceptions import ResourceNotFoundError
from azure.identity import DefaultAzureCredential
from azure.keyvault.certificates import CertificateClient, CertificatePolicy
from azure.keyvault.secrets import SecretClient
from sewer.crypto import AcmeKey, AcmeAccount

from azlet.dns_providers.azuredns import AzureDnsDns


def clean_name(domain: str) -> str:
    name = domain.lower()
    name = re.sub('[^0-9a-zA-Z]+', '-', name)
    if domain.startswith("*"):
        name = "star-" + name
    return name


class AzertBot:
    def __init__(self, keyvault_name: str, dns_subscription: str, dns_rg: str, zone: str, credential=None):
        if credential is None:
            credential = DefaultAzureCredential()
        self.certificate_client = CertificateClient(vault_url=f"https://{keyvault_name}.vault.azure.net/",
                                                    credential=credential, version="2016-10-01")
        self.secrets_client = SecretClient(vault_url=f"https://{keyvault_name}.vault.azure.net/",
                                           credential=credential)
        self.dns_class = AzureDnsDns(dns_subscription, dns_rg, zone, credential)
        self.acme_account = None

    def account(self) -> Optional[AcmeAccount]:
        if self.acme_account is None:
            try:
                secret = self.secrets_client.get_secret("acme-account-key2")
                self.acme_account = AcmeAccount.from_pem(secret.value.encode("UTF-8"))
            except ResourceNotFoundError as e:
                return None
        return self.acme_account

    def store_account(self, account: AcmeKey):
        self.secrets_client.set_secret("acme-account-key2", account.to_pem().decode('utf-8'))
        self.acme_account = account

    def store_pfx(self, domain: str, cert: str, key: AcmeKey, tags=None):
        name = clean_name(domain)
        all_certs = [OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem.as_bytes()) for pem in
                     pem.parse(cert.encode('utf-8'))]
        key_pem = OpenSSL.crypto.load_privatekey(OpenSSL.crypto.FILETYPE_PEM, key.to_pem())
        pkcs = OpenSSL.crypto.PKCS12()
        pkcs.set_privatekey(key_pem)
        pkcs.set_certificate(all_certs[0])
        pkcs.set_ca_certificates(all_certs[1:])
        pfx_cert = pkcs.export()
        if tags:
            self.certificate_client.import_certificate(name, pfx_cert, tags=tags)
        else:
            self.certificate_client.import_certificate(name, pfx_cert)

    def create_certificate(self, domain_name: str, tags=None):
        account = self.account()
        account_is_new = False
        if account is None:
            account = AcmeAccount.create("rsa3072")
            account_is_new = True
        client = sewer.client.Client(
            domain_name=domain_name,
            provider=self.dns_class,
            account=account,
            is_new_acct=account_is_new,
            cert_key=AcmeKey.create("rsa3072")
        )
        if account_is_new:
            client.acme_register()
            self.store_account(account)

        cert = client.get_certificate()
        key = client.cert_key

        self.store_pfx(domain_name, cert, key, tags)

    def check_exists(self, domain_name):
        name = clean_name(domain_name)
        try:
            cert = self.certificate_client.get_certificate(name)
            raise Warning(
                "Cannot create certificate: certificate for this name is already stored. Use 'rotate' to renew the certificate, or use --force-creation.")
        except ResourceNotFoundError:
            pass

    def create(self, prefix: str, force=False, tags=None):
        domain_name = prefix + "." + self.dns_class.zone
        if not force:
            self.check_exists(domain_name)
        self.create_certificate(domain_name, tags)
        

    def rotate(self, threshold: int = 14):
        for props in self.certificate_client.list_properties_of_certificates():
            if not props.enabled:
                continue
            logging.info(f"Checking {props.name}")
            diff = props.expires_on - datetime.now(timezone.utc)
            logging.info(f"Expires in {diff.days}d. (Threshold: {threshold}d)")
            if diff.days > threshold:
                continue
            cert = self.certificate_client.get_certificate(props.name)
            domain_name = cert.policy.subject.replace("CN=", "")
            logging.info(f'Checking subject: "{domain_name}" should end with "{self.dns_class.zone}"')
            if not str(domain_name).endswith(self.dns_class.zone):
                continue
            logging.info(f"Starting renewal ...")

            self.create_certificate(domain_name=domain_name, tags=props.tags)

    def rotate_domain(self, prefix: str):
        domain_name = prefix + '.' + self.dns_class.zone
        name = clean_name(domain_name)
        try:
            cert = self.certificate_client.get_certificate(name)
            # is None or dict of tags
            tags = cert.properties.tags
            self.create_certificate(domain_name=domain_name, tags=tags)
        except:
            logging.error("Cannot find certificate to renew.")

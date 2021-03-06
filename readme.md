# azlet : Azure lets encrypt library

[![PyPI - License](https://img.shields.io/pypi/l/azlet)](https://pypi.org/project/azlet/)
[![PyPI](https://img.shields.io/pypi/v/azlet)](https://pypi.org/project/azlet/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/azlet)



* azlet creates SSL certificates using letsencrypt and stores them in a key vault as certificate.
* The keyvault then can be used by azure APIM, Functions or Webservices to consume the certificates.
* You can create new certificates, or rotate existing certificates.
* to use azlet, you need an azure key vault an an azure DNS.
* azlet uses azure identity to access the key vault as well as the azure dns server. You can use your identity from azure cli, managed identity or enviromnent variables.
* azlet creates an account with letsencrypt, making sure all requests come from the same account. The account is stored in the key vault as secret.
* azlet uses the [sewer](https://github.com/komuw/sewer) library to create certificates.

## Usage

the identity that uses azlet must have secret get/set permissions as well as certificate get/list/update/create/import permissions on the key vault.

create a new certificate:
```bash
python -m azlet create --keyvault-name my-vault --dns-zone dns.zone.com --dns-subscription 11111111-1111-1111-1111-11111111111" --dns-resource-group dns --prefix test
```

create new certificates for all certificates that are valid less that 14 days:
```bash
python -m azlet rotate --keyvault-name my-vault --dns-zone dns.zone.com --dns-subscription 11111111-1111-1111-1111-11111111111" --dns-resource-group dns
```

see `python -m azlet -h` fro a full list of commands. 

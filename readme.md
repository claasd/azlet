# End of live notice
This system is no longer maintained. It is recomendet to swithc to https://github.com/shibayan/keyvault-acmebot



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

# Azure Function for auto-rotation

## infrastructure 
In `templates` there are bicep templates that create a python azure function.
Use `function.bicep` if you aready have a dns-zone and an key-vault. If you have nothing, you can use `all.bicep`. 
Example: 
```
az deployment group create -g rg-dns -f templates/deploy-function.bicep --parameters keyVaultName=kv-my-keyvault dnsZoneName=test.org functionName=func-my-cert-rotation
```
This will create the azure function with a managed identity, give the function identity access to the keyvault and add the function identity as zone contributor to the DNS zone.

## function
if `function` there is a python function that calls the rotate operation every night using a timer-trigger.
Deploy it to your function using the following command (inside the `function` folder):
```
func azure functionapp publish func-my-cert-rotation --python
```

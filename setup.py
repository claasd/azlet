from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='azlet',
    version='0.8.0',
    packages=['azlet', 'azlet.dns_providers'],
    url='https://github.com/claasd/azlet',
    license='MIT',
    author='Claas Diederichs',
    author_email='',
    description='Python package to create/renew certificates using azure DNS and azure KeyVault',
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        "pem",
        "sewer==0.8.4",
        "azure-keyvault-certificates~=4.2",
        "azure-keyvault-secrets~=4.2",
        "azure-identity~=1.5",
        "azure-mgmt-dns~=8.0",
        "pyopenssl~=20.0"
    ]
)

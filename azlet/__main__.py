import argparse

from azure.identity import DefaultAzureCredential

from azlet.azertbot import AzertBot


def execute():
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=["create", "rotate"])
    parser.add_argument("--keyvault-name", "-k", help="name of the keyvault")
    parser.add_argument("--dns-zone", "-d", help="name of the dns-zone")
    parser.add_argument("--dns-subscription", "-s", help="subscription of the dns zone")
    parser.add_argument("--dns-resource-group", "-g", help="resource-group of the dns zone")
    parser.add_argument("--prefix", "-p", help="name of the certificate prefix (only for create operation)",
                        required=False)
    parser.add_argument("--tags", "-t", nargs="*", action = keyvalue, help="tags of the certificate", default=False)
    parser.add_argument("--force-creation",
                        action='store_true',
                        help="Try to create a new certificate even if a certificate already exists in the key vault",
                        required=False)
    parser.add_argument("--rotation-threshold",
                        type=int,
                        default=30,
                        help="Number of days a rotation should be done before certificate expiration.")
    parser.add_argument("--exclude-cli-credential", type=bool, default=False,
                        help="Whether to exclude the Azure CLI from the credential.")
    parser.add_argument("--exclude-environment-credential", type=bool, default=False,
                        help="Whether to exclude a service principal configured by environment variables from the credential.")
    parser.add_argument("--exclude-managed-identity-credential", type=bool, default=False,
                        help="Whether to exclude managed identity from the credential.")
    parser.add_argument("--exclude-visual-studio-code-credential", type=bool, default=False,
                        help="Whether to exclude stored credential from VS Code.")
    parser.add_argument("--exclude-shared-token-cache-credential", type=bool, default=False,
                        help="Whether to exclude the shared token cache.")
    parser.add_argument("--exclude-interactive-browser-credential", type=bool, default=True,
                        help="Whether to exclude interactive browser authentication")
    args = parser.parse_args()

    credential = DefaultAzureCredential(
        exclude_cli_credential=args.exclude_cli_credential,
        exclude_environment_credential=args.exclude_environment_credential,
        exclude_managed_identity_credential=args.exclude_managed_identity_credential,
        exclude_visual_studio_code_credential=args.exclude_visual_studio_code_credential,
        exclude_shared_token_cache_credential=args.exclude_shared_token_cache_credential,
        exclude_interactive_browser_credential=args.exclude_interactive_browser_credential
    )
    bot = AzertBot(keyvault_name=args.keyvault_name, dns_subscription=args.dns_subscription,
                   dns_rg=args.dns_resource_group, zone=args.dns_zone, credential=credential)
    if args.operation == "rotate":
        bot.rotate(args.rotation_threshold)

    if args.operation == "create":
        if not args.prefix:
            parser.error("--prefix is required for command 'create'")
        if args.tags:
            bot.create(args.prefix, args.force_creation, args.tags)
        else:
            bot.create(args.prefix, args.force_creation)


class keyvalue(argparse.Action):
    def __call__( self , parser, namespace, values, option_string = None):
        setattr(namespace, self.dest, dict())
          
        for value in values:
            # split it into key and value
            key, value = value.split('=')
            # assign into dictionary
            getattr(namespace, self.dest)[key] = value


if __name__ == "__main__":
    execute()

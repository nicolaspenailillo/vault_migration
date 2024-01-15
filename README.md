# vault_migration
Util to copy secret enginefrom one Vault to another

# Usage
```console
python vaultMigration.py old_vault_url new_vault_url secret_engine_to_migrate [optional_new_path_prefix] [optional_new_engine_name]
```
old_vault_url: old vault url to migrate ex: https://oldvault.com
new_vault_url: new vault url to migrate ex: https://newvault.com
secret_engine_to_migrate: name of the secret engine to migrate
optional_new_path_prefix: add this in case of adding a prefix for all secrets path
optional_new_engine_name: add this in case of migrating the engine with a new name

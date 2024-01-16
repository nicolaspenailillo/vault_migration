# Hashicorp Vault Migration Util
Util to copy secret engine from one Vault to another with OIDC authentication

# Usage
```console
python vaultMigration.py old_vault_url new_vault_url secret_engine_to_migrate [optional_new_engine_name] [optional_new_path_prefix]
```

- old_vault_url: old vault url to migrate ex: https://oldvault.com
- new_vault_url: new vault url to migrate ex: https://newvault.com
- secret_engine_to_migrate: name of the secret engine to migrate ex: secrets
- optional_new_engine_name: add this in case of migrating the engine with a new name ex: secretsnew
- optional_new_path_prefix: add this in case of adding a prefix for all secrets path ex: cloud/

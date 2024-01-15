from vault_oidc_lib import VaultOIDCHandler, migrate_engine
import sys

if __name__ == "__main__":
    # Check if the correct number of arguments is provided
    if len(sys.argv) < 4 or len(sys.argv) > 6:
        print("Usage: python vaultMigration.py old_vault_url new_vault_url secret_engine_to_migrate [optional_new_path_prefix] [optional_new_engine_name]")
        sys.exit(1)
        
    # Get command line arguments
    old_vault_url = sys.argv[1]
    new_vault_url = sys.argv[2]
    secret_engine = sys.argv[3]

    optional_new_path_prefix = sys.argv[4] if len(sys.argv) > 4 else None
    optional_new_engine_name = sys.argv[5] if len(sys.argv) > 5 else None

    # Connect old vault
    vault_old = VaultOIDCHandler(old_vault_url, role='')
    vault_old.authenticate()
    if vault_old.token:
        # Do something
        pass

    # Connect new vault
    vault_new = VaultOIDCHandler(new_vault_url, role='')
    vault_new.authenticate()
    if vault_new.token:
        # Do something
        pass

    migrate_engine(vault_old.client, vault_new.client, secret_engine, optional_new_path_prefix, optional_new_engine_name)

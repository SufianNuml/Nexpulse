resource "azurerm_key_vault" "kv" {
  name                = "kv-nexpulse01"
  resource_group_name = azurerm_resource_group.nexpulse.name
  location            = azurerm_resource_group.nexpulse.location
  tenant_id           = data.azurerm_client_config.current.tenant_id

  sku_name = "standard"

  rbac_authorization_enabled = true
  soft_delete_retention_days = 7

  tags = {
    project     = "Nexpulse"
    environment = "dev"
    managed_by  = "terraform"
  }
}
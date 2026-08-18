resource "azurerm_databricks_access_connector" "nexpulse" {
  name                = "dbac-${var.project_name}"
  resource_group_name = azurerm_resource_group.nexpulse.name
  location            = azurerm_resource_group.nexpulse.location

  identity {
    type = "SystemAssigned"
  }

  tags = {
    project     = "Nexpulse"
    environment = "dev"
    managed_by  = "terraform"
  }
}

resource "azurerm_role_assignment" "dbac_storage" {
  scope                = azurerm_storage_account.adls.id
  role_definition_name = "Storage Blob Data Contributor"
  principal_id         = azurerm_databricks_access_connector.nexpulse.identity[0].principal_id
}
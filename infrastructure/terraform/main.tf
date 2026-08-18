resource "azurerm_resource_group" "nexpulse" {
  name     = "rg-${var.project_name}"
  location = var.location

  tags = {
    project     = "Nexpulse"
    environment = "dev"
    managed_by  = "terraform"
  }
}

resource "azurerm_storage_account" "adls" {
  name                = "adls${var.project_name}${var.storage_account_suffix}"
  resource_group_name = azurerm_resource_group.nexpulse.name
  location            = azurerm_resource_group.nexpulse.location

  account_tier             = "Standard"
  account_replication_type = "LRS"
  account_kind             = "StorageV2"

  is_hns_enabled = true

  tags = {
    project     = "Nexpulse"
    environment = "dev"
    managed_by  = "terraform"
  }
}

resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_id    = azurerm_storage_account.adls.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_id    = azurerm_storage_account.adls.id
  container_access_type = "private"
}

resource "azurerm_storage_container" "gold" {
  name                  = "gold"
  storage_account_id    = azurerm_storage_account.adls.id
  container_access_type = "private"
}
resource "azurerm_eventhub_namespace" "nexpulse" {
  name                = "evhns-nexpulse"
  location            = azurerm_resource_group.nexpulse.location
  resource_group_name = azurerm_resource_group.nexpulse.name

  sku      = "Standard"
  capacity = 1

  tags = {
    environment = "dev"
    project     = "Nexpulse"
    managed_by  = "terraform"
  }
}

resource "azurerm_eventhub" "orders" {
  name              = "orders"
  namespace_id      = azurerm_eventhub_namespace.nexpulse.id
  partition_count   = 3
  message_retention = 1
}

resource "azurerm_eventhub" "payments" {
  name              = "payments"
  namespace_id      = azurerm_eventhub_namespace.nexpulse.id
  partition_count   = 3
  message_retention = 1
}

resource "azurerm_eventhub" "inventory" {
  name              = "inventory"
  namespace_id      = azurerm_eventhub_namespace.nexpulse.id
  partition_count   = 3
  message_retention = 1
}

resource "azurerm_eventhub_namespace_authorization_rule" "kafka_client" {
  name                = "kafka-client-policy"
  namespace_name      = azurerm_eventhub_namespace.nexpulse.name
  resource_group_name = azurerm_resource_group.nexpulse.name

  listen = true
  send   = true
  manage = false
}
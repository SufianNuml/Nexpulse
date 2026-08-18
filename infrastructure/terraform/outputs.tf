output "storage_account_name" {
  value = azurerm_storage_account.adls.name
}

output "eventhub_namespace" {
  value = azurerm_eventhub_namespace.nexpulse.name
}

output "eventhub_kafka_connection_string" {
  value     = azurerm_eventhub_namespace_authorization_rule.kafka_client.primary_connection_string
  sensitive = true
}
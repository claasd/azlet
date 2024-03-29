param dnsZoneName string
param createKeyVault bool
param keyVaultName string = take('kv-azlet-${uniqueString(resourceGroup().id)}', 24)
param functionName string = 'func-azlet-${uniqueString(resourceGroup().id)}'
param storageName string = take('stazlet${uniqueString(resourceGroup().id)}', 24)
param location string = resourceGroup().location

resource keyVault 'Microsoft.KeyVault/vaults@2022-07-01' = if (createKeyVault) {
  name: keyVaultName
  location: location
  properties: {
    tenantId: subscription().tenantId
    accessPolicies: []
    sku: {
      name: 'standard'
      family: 'A'
    }
  }
}

resource dnsZone 'Microsoft.Network/dnsZones@2018-05-01' = {
  name: dnsZoneName
  location: 'global'
}

module deployFunction 'deploy-function.bicep' = {
  name: 'deploy-azlet-function'
  params: {
    dnsZoneName: dnsZone.name
    functionName: functionName
    keyVaultName: keyVault.name
    storageName: storageName
    location: location
  }
}

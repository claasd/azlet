param keyVaultName string
param dnsZoneName string
param storageName string = take('stazlet${uniqueString(resourceGroup().id)}',24)
param functionName string = 'func-azlet-${uniqueString(resourceGroup().id)}'
param keyVaultRg string = resourceGroup().name
param keyVaultSubscription string = subscription().subscriptionId
param dnsSubscription string = subscription().subscriptionId
param dnsRg string = resourceGroup().name



resource storageaccount 'Microsoft.Storage/storageAccounts@2021-02-01' = {
  name: storageName
  location: resourceGroup().location
  kind: 'StorageV2'
  sku: {
    name: 'Standard_LRS'
  }
}

resource appInsightsComponents 'Microsoft.Insights/components@2020-02-02-preview' = {
  name: 'appi-azlet'
  location: resourceGroup().location
  kind: 'web'
  properties: {
    Application_Type: 'web'
  }
}

resource azureFunction 'Microsoft.Web/sites@2020-12-01' = {
  name: functionName
  location: resourceGroup().location
  kind: 'functionapp,linux'
  identity: {
    type: 'SystemAssigned'
  }
  properties: {
    reserved: true
    httpsOnly: true
    siteConfig: {
      linuxFxVersion : 'python|3.8'
      pythonVersion: '3.8'
      appSettings: [
        {
          name: 'AzureWebJobsDashboard'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageaccount.name};AccountKey=${listKeys(storageaccount.name, '2019-06-01').keys[0].value}'
        }
        {
          name: 'AzureWebJobsStorage'
          value: 'DefaultEndpointsProtocol=https;AccountName=${storageaccount.name};AccountKey=${listKeys(storageaccount.name, '2019-06-01').keys[0].value}'
        }
        {
          name: 'FUNCTIONS_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'APPINSIGHTS_INSTRUMENTATIONKEY'
          value: appInsightsComponents.properties.InstrumentationKey
        }
        {
          name: 'FUNCTIONS_WORKER_RUNTIME'
          value: 'python'
        }
        {
          name: 'keyVaultName'
          value: keyVaultName
        }
        {
          name: 'dnsSubscription'
          value: dnsSubscription
        }
        {
          name: 'dnsRg'
          value: dnsRg
        }
        {
          name: 'dnsZoneName'
          value: dnsZoneName
        }
      ]
    }
  }
}



module dnsZoneRoleAssignment 'assign-role-to-zone.bicep' = {
  name: 'assignRoleToDnsZone'
  scope: resourceGroup(dnsSubscription, dnsRg)
  params: {
    dnsZoneName: dnsZoneName
    principalId: azureFunction.identity.principalId
  }
}

module keyVaultAccessAssignment 'assign-access-to-kv.bicep' = {
 name: 'keyVaultAccessAssignment'
 scope: resourceGroup(keyVaultSubscription, keyVaultRg)
 params: {
   keyVaultName: keyVaultName
   principalId: azureFunction.identity.principalId
 }
}

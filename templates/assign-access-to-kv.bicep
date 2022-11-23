param keyVaultName string
param principalId string

resource keyVaultAccess 'Microsoft.KeyVault/vaults/accessPolicies@2022-07-01' = {
  name: '${keyVaultName}/add'
  properties: {
    accessPolicies: [
      {
        tenantId: subscription().tenantId
        objectId: principalId
        permissions: {
          certificates: [
            'get'
            'list'
            'update'
            'create'
            'import'
          ]
        }
      }
    ]
  }
}

param dnsZoneName string
param principalId string
var dnsZoneContributorRole = subscriptionResourceId('Microsoft.Authorization/roleDefinitions','befefa01-2a29-4197-83a8-272ff33ce314')

resource dnsZone 'Microsoft.Network/dnsZones@2018-05-01' existing = {
  name: dnsZoneName
}


resource dnsZoneAssignment 'Microsoft.Authorization/roleAssignments@2020-04-01-preview' = {
  name: guid(dnsZone.id, principalId, dnsZoneContributorRole)
  scope: dnsZone
  properties: {
    roleDefinitionId: dnsZoneContributorRole
    principalId: principalId
    principalType: 'ServicePrincipal'
  }
}

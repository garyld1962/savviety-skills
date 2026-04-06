---
name: bicep
description: "Azure Bicep IaC patterns — module structure, naming, parameters, outputs, secure values, resource groups"
---

# Bicep Patterns

Opinionated patterns for Azure infrastructure as code with Bicep.

## File Structure

```
infra/
├── main.bicep              # Entry point — orchestrates modules
├── main.bicepparam         # Parameter values (per-environment)
├── modules/
│   ├── app-service.bicep   # One module per logical resource group
│   ├── database.bicep
│   ├── key-vault.bicep
│   ├── networking.bicep
│   └── monitoring.bicep
└── environments/
    ├── dev.bicepparam
    ├── staging.bicepparam
    └── prod.bicepparam
```

One module per logical concern. `main.bicep` composes them — it should contain no resources directly.

## Naming Convention

```bicep
// Parameters: camelCase
param appName string
param environment string
param location string = resourceGroup().location

// Variables: camelCase
var resourcePrefix = '${appName}-${environment}'
var tags = {
  application: appName
  environment: environment
  managedBy: 'bicep'
}

// Resources: camelCase, descriptive name
resource appServicePlan 'Microsoft.Web/serverfarms@2023-12-01' = {
  name: '${resourcePrefix}-plan'
  location: location
  tags: tags
  sku: { name: 'B1' }
}
```

## Parameters

- Use `@description()` on every parameter.
- Use `@allowed()` for constrained values.
- Use `@secure()` for secrets — NEVER default a secret.
- Provide defaults only when there's a sensible universal default.

```bicep
@description('Name of the application')
param appName string

@description('Deployment environment')
@allowed(['dev', 'staging', 'prod'])
param environment string

@description('SQL Server admin password')
@secure()
param sqlAdminPassword string   // NO default for secrets
```

## Modules

Modules should be self-contained — take parameters in, expose outputs.

```bicep
// main.bicep
module database 'modules/database.bicep' = {
  name: 'database-${uniqueString(resourceGroup().id)}'
  params: {
    serverName: '${resourcePrefix}-sql'
    adminPassword: sqlAdminPassword
    location: location
    tags: tags
  }
}

// Reference outputs from other modules
module appService 'modules/app-service.bicep' = {
  name: 'app-service-${uniqueString(resourceGroup().id)}'
  params: {
    connectionString: database.outputs.connectionString
  }
}
```

## Outputs

- Only output values that other modules or deployment scripts need.
- Mark connection strings and secrets as `@secure()` outputs or store in Key Vault.

```bicep
@description('FQDN of the database server')
output serverFqdn string = sqlServer.properties.fullyQualifiedDomainName

// WRONG — don't output secrets directly
// output connectionString string = 'Server=...'

// CORRECT — store secrets in Key Vault, output the reference
output connectionStringSecretUri string = keyVaultSecret.properties.secretUri
```

## Common Patterns

### Conditional resources
```bicep
param enableDiagnostics bool = true

resource diagnostics 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = if (enableDiagnostics) {
  name: 'diag-${appName}'
  // ...
}
```

### Loops
```bicep
param appSettings object = {}

resource settings 'Microsoft.Web/sites/config@2023-12-01' = {
  name: 'appsettings'
  parent: webApp
  properties: appSettings
}
```

### Existing resources
```bicep
resource existingVnet 'Microsoft.Network/virtualNetworks@2023-11-01' existing = {
  name: vnetName
  scope: resourceGroup(networkResourceGroup)
}
```

## Security Rules

- NEVER hardcode secrets, connection strings, or passwords in `.bicep` files.
- Use Key Vault references for all sensitive configuration.
- Use managed identities instead of connection strings where possible.
- Set `minTlsVersion: '1.2'` on all web resources.
- Enable HTTPS-only on app services.

# IBM Cloud Pak for Data zen watchdog monitor: Global Platform connections

## Monitor Summary

This monitor will generate the following observations:  
- Count available Cloud Pak for Data global connections  
- Perform a connection test for each connection

## Monitor Requirements
In order for Platform Global Connection to be available, CCS (Common Core Services) must be available on the Cloud Pak for Data instance. Catridges like Watson Studio and Watson Machine Learning automatically install CCS as part of their dependencies. If CCS is not available, no platform connections are available. 

## Administrative Credential Requirements

In order to retrieve the monitor data, the credential of admin user will be used. The default password of admin user is saved in the secret admin-user-details. You could use the below command to query the default password of the admin user..
```
oc extract secret/admin-user-details --keys=initial_admin_password --to=-
```
Once the password of the admin user is changed, please also change the password in the secret admin-user-details. 
```
oc set data secret/admin-user-details initial_admin_password=<new password>
```

## Deployment of the monitor

This monitor can be deployed using the IBM Cloud Pak Deployer or manually deployed using oc commands:
- [Cloud Pak Deployer](cp4d-platform-global-connections_cloud-pak-deployer.md) 
- [Manual Deployment using oc commands](cp4d-platform-global-connections_manual.md)

## Monitor Source

Source folder containing the script can be found  [here (cp4d-platform-global-connections).](/cp4d-platform-global-connections) 

## Generated observations
Once the monitor is deployed, the following observations are available in IBM Cloud Pak for Data Metrics:

### Using the IBM Cloud Pak for Data Platform Management Events: 
https://&lt;CP4D-BASE-URL&gt;/zen/#/platformManagement/events

On the Platform Management Events page the following entries are added:

| Event   | Event Type      | Possible values | Description |
|:----------|:-------------|:------|:----------|
| Cloud Pak for Data Global Connections Count |Number of CP4D Platform connections |info, warning | The Cloud Pak for Data Platform Connections are requested.<br> If this succeeds, an info metric is set.<br> If this request fails, a warning metric is set. |
| Global Connection - &lt;NAME OF CONNECTION&gt; |Test CP4D Platform connection   |info, warning | For each Global Platform connection a seperate entry is available.<br> If the connection test is successful, an info metric is set.<br> If the connection test fails, a warning metric is set. |

![Overview Events and Alerts](cp4d_events.png?raw=true "Overview Events and Alerts")

### Using the IBM Cloud Pak for Data Prometheus endpoint
https://&lt;CP4D-BASE-URL&gt;/zen/metrics

It will generate 2 types of metrics:
- Actual Result metrics  
  These metrics contain the observed values
- Zen Watchdog metrics  
  These metrics are used by the Cloud Pak for Data Zen Watchdog to monitor the state and trigger notifications

**Actual Result metrics:**
- global_connections_count<br>
  Provides the number of available connections
- global_connection_valid (for each connection)<br>
  For each connection, a test action is performed
    - 1 (Test Connection success)
    - 0 (Test connection failed)

```
# HELP global_connections_count 
# TYPE global_connections_count gauge
global_connections_count{event_type="global_connections_count",monitor_type="cp4d_platform_global_connections",reference="Cloud Pak for Data Global Connections Count"} 2

# HELP global_connection_valid 
# TYPE global_connection_valid gauge
global_connection_valid{event_type="global_connection_valid",monitor_type="cp4d_platform_global_connections",reference="Cognos MetaStore Connection"} 1
global_connection_valid{event_type="global_connection_valid",monitor_type="cp4d_platform_global_connections",reference="Cognos non-shared"} 0
```

**Zen Watchdog metrics** (used in platform management events)
- watchdog_cp4d_platform_global_connections_global_connections_count
- watchdog_cp4d_platform_global_connections_global_connection_valid (for each connection)
  
Zen Watchdog metrics can have the following values:
- 2 (info)
- 1 (warning)
- 0 (critical)

```
# HELP watchdog_cp4d_platform_global_connections_global_connection_valid 
# TYPE watchdog_cp4d_platform_global_connections_global_connection_valid gauge
watchdog_cp4d_platform_global_connections_global_connection_valid{event_type="global_connection_valid",monitor_type="cp4d_platform_global_connections",reference="Cognos MetaStore Connection"} 2
watchdog_cp4d_platform_global_connections_global_connection_valid{event_type="global_connection_valid",monitor_type="cp4d_platform_global_connections",reference="Cognos non-shared"} 1

# HELP watchdog_cp4d_platform_global_connections_global_connections_count 
# TYPE watchdog_cp4d_platform_global_connections_global_connections_count gauge
watchdog_cp4d_platform_global_connections_global_connections_count{event_type="global_connections_count",monitor_type="cp4d_platform_global_connections",reference="Cloud Pak for Data Global Connections Count"} 2
```


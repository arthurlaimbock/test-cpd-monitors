# Define Monitors in the Cloud Pak Deployer

The Cloud Pak Deployer, as part of its deployment process, can deploy monitors which can be used to monitor the health of the platform. 

Configuring monitors is to add a cp4d_monitors section to the configuration of the Cloud Pak Deployer.

The following example deploys a single monitor, which has 2 event types.
```
# List of cp4d_monitors
cp4d_monitors:
- name: cp4d-monitor-set-1
  cp4d_instance: <OC_PROJECT>
  openshift_cluster_name: <OC_CLUSTER_NAME>
  default_monitor_source_repo: https://github.ibm.com/CloudPakDeployer/cloud-pak-deployer-monitors
  default_monitor_source_token_secret: monitors_source_repo_secret
  default_monitor_target_cr: de.icr.io/monitorrepo  
  default_monitor_target_cr_user_secret: monitors_target_cr_username
  default_monitor_target_cr_password_secret: monitors_target_cr_password
  # List of monitors
  monitors:
  - name: cp4d-platform-global-connections
    #monitor_source_repo:             
    #monitor_source_token_secret:    
    #monitor_target_cr:              
    #monitor_target_cr_user_secret:  
    #monitor_target_cr_user_password:
    context: cp4d-platform-global-connections
    label: latest
    schedule: "*/15 * * * *"
    event_types:
    - name: "global_connections_count"
      simple_name: "Number of CP4D Platform connections"
      alert_type: "platform"
      short_description: "Number of CP4D Platform connections"
      long_description: "Number of CP4D Platform connections: <global_connections_count>"
      resolution: "none"
      reason_code_prefix: "80"
    - name: "global_connection_valid"
      simple_name: "Test CP4D Platform connection"
      alert_type: "platform"
      short_description: "Test CP4D Platform connection"
      long_description: "Test result CP4D Platform connection: <global_connection_valid>"
      resolution: "Validate the connection properties"
      reason_code_prefix: "80"
```

Each `cp4d_monitors` entry contains a set of default settings, which are applicable to the `monitors` list. These defaults can be overwritten per monitor if needed.

| Property | Description                                                          | Mandatory | Allowed values |
| -------- | -------------------------------------------------------------------- | --------- | -------------- |
| name  | The name of the monitor set    | Yes       |   |
| cp4d_instance | The OpenShift project (namespace) on which the Cloud Pak for Data instance resides  | Yes       |  |
| openshift_cluster_name | The Openshift cluster name | Yes |  |
| default_monitor_source_repo | The default repository location of all monitors located in the `monitors` section | No |  |
| default_monitor_source_token_secret | The default repo access token secret name, must be available in the vault | No |  |
| default_monitor_target_cr |   The default target container registry (cr) for the monitor image to be pushed. When omitted, the OpenShift internal registry is used | No |  |
| default_monitor_target_cr_user_secret | The default target container registry user name secret name used to push the monitor image. Must be available in the vault. Value is ignored if default_monitor_target_cr is not provided | No |  |
| default_monitor_target_cr_password_secret | The default target container registry password secret name used to push the monitor image. Must be available in the vault. Value is ignored if default_monitor_target_cr is not provided | No |  |
| monitors | List of monitors | Yes |  |

Per `monitors` entry, the following settings are specified:

| Property | Description                                                          | Mandatory | Allowed values |
| -------- | -------------------------------------------------------------------- | --------- | -------------- |
| name  | The name of the monitor entry     | Yes       | lowercase RFC 1123 subdomain (1)   |
| monitor_source_repo | Overrides default_monitor_source_repo for this single monitor | No | | 
| monitor_source_token_secret | Overrides default_monitor_source_token_secret for this single monitor | No | | 
| monitor_target_cr | Overrides default_monitor_target_cr for this single monitor | No | | 
| monitor_target_cr_user_secret | Overrides default_monitor_target_cr_user_secret for this single monitor | No | | 
| monitor_target_cr_user_password | Overrides default_monitor_target_cr_user_password for this single monitor | No | | 
| context | Sets the context of the monitor the the source repo (sub folder name) | Yes | | 
| label | Set the label of the pushed image, default to 'latest' | No | | 
| schedule | Sets the schedule of the generated Cloud Pak for Data monitor cronjob | No | | 
| event_types | List of monitor event types | Yes | | 

(1) Must consist of lower case alphanumeric characters, `-` or `.`, and must start and end with an alphanumeric character (e.g. `example.com`, regex used for validation is `[a-z0-9]([-a-z0-9]*[a-z0-9])?(\.[a-z0-9]([-a-z0-9]*[a-z0-9])?)*`)

Each monitors entry must have at least 1 event_types entry specified:

| Property | Description                                                          | Mandatory | Allowed values |
| -------- | -------------------------------------------------------------------- | --------- | -------------- |
| name  | The name of the event type entry     | Yes       | only use lowercase, numbers and "_" characters  |
| simple_name  | Simple name of the event type     | Yes |    |
| alert_type  | Alert type of the event type     | Yes | platform  |
| short_description  | Short description of the event type     | Yes |    |
| long_description  | Long description of the monitor. The `item` must be available in the metadata of the monitor response    | Yes |    |
| resolution  | Short description of proposed solution  | Yes       |    |
| reason_code_prefix  | Used for SNMP alerts, custom prefixes should be greater than 60  | Yes  |    |


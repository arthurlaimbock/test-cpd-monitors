# Deployment of monitor using the IBM Cloud Pak Deployer

## Configure authentication secrets in the vault used by the Cloud Pak Deployer

Before deploying the monitor, ensure the secrets used in the deployment are available in the vault used by the Cloud Pak Deployer.
- Source repository token (**Mandatory**)  
  Source token used to build and monitor image
- Target Container Registry username and password (**Optional**)  
  By default the image will be pushed to the internal image-registry of OpenShift, which do not require credentials. If the image is pushed to an external image registry, the required credentials must be available. 

Example to configure the secrets in the vaults used by the Cloud Pak Deployer

```
export STATUS_DIR=<Status directory of the Cloud Pak Deployer>
export CONFIG_DIR=<Configuration folder used by the Cloud Pak Deployer>

# Mandatory Source Repo secret
./cp-deploy.sh vault set --vault-secret monitors_source_repo_secret --vault-secret-value ThisIsMyGitAccessToken!
# Optional Target Image Registry Credentials
./cp-deploy.sh vault set --vault-secret default_monitor_target_cr_user_secret --vault-secret-value TargetCRUserName
./cp-deploy.sh vault set --vault-secret monitors_target_cr_password --vault-secret-value TargetCRPassword
```

Validate the created secrets are available:
```
export STATUS_DIR=<Status directory of the Cloud Pak Deployer>
export CONFIG_DIR=<Configuration folder used by the Cloud Pak Deployer>

# List all secrets
./cp-deploy.sh vault list

# Optionally retrieve the values to confirm the correct values are loaded
./cp-deploy.sh vault get --vault-secret monitors_source_repo_secret
```

## Add OpenShift Monitoring to the Cloud Pak Deployer configuration

Deploying monitors requires the OpenShift Monitoring to be enabled on the OpenShift cluster. If not already part of the Cloud Pak Deployer configuration, add the `openshift_monitoring` configuration. This can be added to an existing yaml configuration file, or a new yaml file can be added to the configuration.

```
openshift_monitoring:
- openshift_cluster_name: <OC_CLUSTER_NAME>
  user_workload: enabled
  # Optional properties to persist OpenShift Monitoring
  pvc_storage_class: ibmc-vpc-block-retain-general-purpose
  pvc_storage_size_gb: 100
  # Optional Remote Rewrite
  #remote_rewrite_url: http://remote_rewrite_url:<port>/write
  # Optional install local instance of Grafana on OpenShift
  grafana_operator: enabled
  grafana_project: grafana
```


| Property | Description                                                          | Mandatory | Allowed values |
| -------- | -------------------------------------------------------------------- | --------- | -------------- |
| openshift_cluster_name  | The name of the openshift cluster set    | Yes       |   |
| user_workload | Flag to enable or disable OpenShift User workload monitoring | Yes       | enabled, disabled  |
| pvc_storage_class | Storage class used to persist the OpenShift monitoring | No       |  |
| pvc_storage_size_gb | Size of the Persistent Volume Claim for storing OpenShift monitoring | No       |  |
| remote_rewrite_url | Push the Prometheus metrics to a remote system | No       |  |
| grafana_operator | Install the Red Hat Community Grafana Operator | No       | enabled, disabled  |
| grafana_project | Target OpenShift Project for the deployment of Grafana | No       |  |



## Add the monitor to the Cloud Pak Deployer configuration

Add the following section to the Cloud Pak Deployer configuration, or add the monitor to an existing `monitors` section. 

The `cp4d_monitors` can be added to an existing configuration yaml file in the `config` folder, or create a seperate yaml file:
- OC_PROJECT: The Project name in which Cloud Pak for Data is deployed where the monitors will be added
- OC_CUSTER_NAME: The name of the OpenShift Cluster

```
# List of cp4d_monitors
cp4d_monitors:
- name: cp4d-monitor-set-1
  cp4d_instance: <OC_PROJECT>
  openshift_cluster_name: <OC_CLUSTER_NAME>
  default_monitor_source_repo: https://github.ibm.com/CloudPakDeployer/cloud-pak-deployer-monitors
  default_monitor_source_token_secret: monitors_source_repo_secret
  #Optional target Container Registry
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

## Run the Cloud Pak Deployer

Run the Cloud Pak Deployer to implement the changes and deploy the monitors. 

```
export STATUS_DIR=<Status directory of the Cloud Pak Deployer>
export CONFIG_DIR=<Configuration folder used by the Cloud Pak Deployer>

./cp-deploy.sh env apply
```

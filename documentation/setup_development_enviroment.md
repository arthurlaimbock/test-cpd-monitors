# Setup Development Environment with Visual Studio Code (VSC)

### Purpose:

It is a step-by-step guide to setup Development Environment, which is able to run the monitoring scripts manually for developing, testing and debugging the monitoring scripts.


### Prerequisite:

1. Install the [Python 3.8.x](https://www.python.org/downloads/).

2. Install **requests** and **kubernetes** library in Python with pip.
```
pip install requests
pip install kubernetes
```

3. Install the latest [Visual Stuido Code](https://code.visualstudio.com/Download).

4. Set the following enviroments.
```
ENV=DEV
ICPD_CONTROLPLANE_NAMESPACE=<zen-dapper>
CP4D_HOST=<https://cpd-zen-dapper.dapper-demo-a939e0e6a37f1ce85dbfddbb7ab97418-0000.eu-de.containers.appdomain.cloud>
```

### Steps:


1. Go to the folder cloud-pak-deployer-monitors.

2. Run the command `code .` to run the VSC.

3. Login the Openshift cluster. The following shows an example for Openshift cluster login command:
```
oc login --token=sha256~C7TemiWvOm6gvqY6Gu6wmKIzKMTBv8rXdEtZ-f3sN0I --server=https://c115-e.eu-de.containers.cloud.ibm.com:32383
```

4. Run the specific Python script. 




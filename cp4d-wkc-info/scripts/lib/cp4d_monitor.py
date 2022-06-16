import datetime
import os
from pathlib import Path
import requests
import json
from lib import cpdctl
from lib import k8s
from requests.packages.urllib3.exceptions import InsecureRequestWarning

def create_and_validate_type(value):    
  #Replace all <SPACE> with _
  new_value = value.replace(" ", "_")
  #Replace all - with _
  new_value = new_value.replace("-","_")
  return new_value

def post_events (events):
    # configure post request and set secret headers
    url = 'https://zen-watchdog-svc:4444/zen-watchdog/v1/monitoring/events'
    with open('/var/run/sharedsecrets/token', 'r') as file:
        secret_header = file.read().replace('\n', '')
    headers = {'Content-type': 'application/json', 'secret': secret_header}

    #Prepare events for post
    json_string = json.dumps(events)

    print ("Sending events to zen-watchdog:")
    print (json_string)
    
    # post call to zen-watchdog to record events
    r = requests.post(url, headers=headers, data=json_string, verify=False)
    #print the results
    print("Response status_code: {}".format(r.status_code))
    print("Response content: {}".format(r.text))


def get_internal_service_token():
    service_broker_secret = get_secret_header_token()
    if service_broker_secret is None:
        print('could not find zen-service-broker-secret environment variable')
        return None
  
    url = 'https://zen-core-api-svc:4444/internal/v1/service_token'
    headers = {
        'secret': service_broker_secret
    }
    #include `verify=False` as the final argument to by-pass certificate verification
    r = requests.get(url, headers=headers, verify=False)
    if r.status_code != 200:
        print('Error requesting internal_service_token - status_code - ' + str(r.status_code))
        try:
            print(r.json())
        except Exception:
            print(r.text)
        return None
    else:
        print('Successfully requested internal_service_token - status_code - 200')
        try:
            resp = r.json()
            if resp['token']:
                bearer_token = 'Bearer ' + resp['token']
                return str(bearer_token)
            else:
                print('could not parse internal_service_token from the response')
                return None
        except Exception:
            print('could not parse internal_service_token from the response')
            return None

def get_secret_header_token ():
    secret_header = None
    with open('/var/run/sharedsecrets/token', 'r') as file:
        secret_header = file.read().replace('\n', '')
    return secret_header

def get_current_namespace():
     with open('/var/run/secrets/kubernetes.io/serviceaccount/namespace','r') as file:
        namespace_name = file.read().replace('\n','')
     return namespace_name
 
def get_current_timestamp():
    return datetime.datetime.now().timestamp()
 
def need_to_fetch(fetch_interval,fetch_timestamp):
   return get_current_timestamp()-(fetch_interval*60+fetch_timestamp)>0

configmap_name='cp4d-monitor-configuration'
project_last_refresh_key='cp4d-project-last-refresh'
project_refresh_interval_key='cp4d-project-refresh-interval-minutes'
jobs_last_refresh_key='cp4d-job-last-refresh'
jobs_last_refresh_interval_key='cp4d-job-refresh-interval-minutes'
wkc_last_refresh_key='cp4d-wkc-last-refresh'
wkc_last_refresh_interval_key='cp4d-wkc-refresh-interval-minutes'
cache_folder='/user-home/_global_/monitors'
Path(cache_folder).mkdir( parents=True, exist_ok=True )
projects_cache_file=cache_folder+'/projects.json'
jobs_cache_file=cache_folder+'/jobs.json'
wkc_cache_file=cache_folder+'/wkc.json'
namespace=os.environ.get('ICPD_CONTROLPLANE_NAMESPACE')
if namespace is None:
    print ("Unable to read from expected environment variable ICPD_CONTROLPLANE_NAMESPACE")
    exit(1)

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
admin_pass =k8s.get_admin_secret(namespace)
cp4d_host='https://ibm-nginx-svc'
k8s.check_ccs_svc(namespace)
cpdctl.cpdctl_init_config_context('admin', admin_pass,cp4d_host)

if not k8s.is_exist_config_map(namespace,configmap_name):  
    k8s.create_configmap_cp4d_monitor_configuration(namespace)

def get_project_list():
    projects=[]
    cacheconfig = k8s.get_config_map(namespace=namespace,name=configmap_name)
    project_fetch_interval = float(cacheconfig[project_refresh_interval_key])
    last_fetch_timestamp = float(cacheconfig[project_last_refresh_key])
    if need_to_fetch(project_fetch_interval,last_fetch_timestamp)==True or not os.path.exists(projects_cache_file):
        project_data = cpdctl.cpdctl_get_projects()
        if project_data['total_results'] > 0:
            projects=project_data['resources']

        with open(projects_cache_file, 'w') as f:
            f.write(json.dumps(projects))
        cacheconfig[project_last_refresh_key]=str(get_current_timestamp())
        k8s.set_config_map(namespace=namespace,name=configmap_name,data=cacheconfig)
        return projects
    
    with open(projects_cache_file, 'r') as f:
        projects = json.loads(f.read())
    return projects

def get_jobs_list(projects):
    jobs={}
    cacheconfig = k8s.get_config_map(namespace=namespace,name=configmap_name)
    job_fetch_interval = float(cacheconfig[jobs_last_refresh_interval_key])
    last_fetch_timestamp = float(cacheconfig[jobs_last_refresh_key])
    if need_to_fetch(job_fetch_interval,last_fetch_timestamp)==True or not os.path.exists(jobs_cache_file):
        for project in projects :
            project_id=project['metadata']['guid']
            jobs_data = cpdctl.cpdctl_get_jobs(project_id=project_id)
            if len(jobs_data)>0 and jobs_data['total_rows'] >0: 
                jobs[project_id]=cpdctl.cpdctl_get_jobs(project_id=project_id)
    
        with open(jobs_cache_file, 'w') as f:
            f.write(json.dumps(jobs))
        cacheconfig[jobs_last_refresh_key]=str(get_current_timestamp())
        k8s.set_config_map(namespace=namespace,name=configmap_name,data=cacheconfig)
        return jobs
    
    with open(jobs_cache_file, 'r') as f:
        jobs = json.loads(f.read())
    return jobs


def get_all_users():
    bearer_token = get_admin_token()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': str(bearer_token)}
    url = cp4d_host + '/usermgmt/v1/usermgmt/users'
    all_users_res = requests.get(url, headers=headers, verify=False)
    all_users = {}
    #print(all_users_response)
    if all_users_res.status_code != 200:
        print('Error requesting get all users - status_code - ' + str(all_users_res.status_code))
        try:
            print(all_users_res.json())
        except Exception:
            print(all_users_res.text)
        return None
         
    users = json.loads(all_users_res.text)
    for user in users:
        all_users[user['uid']] = user
    return all_users


def get_job_run_info(project_id, job_id):
    bearer_token = get_admin_token()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': str(bearer_token)}
    url = cp4d_host + f'/v2/jobs/{job_id}/runs?project_id={project_id}'
    job_run_info_res = requests.get(url, headers=headers, verify=False)
    if job_run_info_res.status_code != 200:
        print('Error requesting get all runs - status_code - ' + str(job_run_info_res.status_code))
        try:
            print(job_run_info_res.json())
        except Exception:
            print(job_run_info_res.text)
        return []
    
    runs = json.loads(job_run_info_res.text)
    return runs['results']   

def get_admin_token():
    headers= {'Content-Type': 'application/json', 'Accept': 'application/json'}
    data = {"username":"admin","password": admin_pass}
    auth_api = cp4d_host + "/icp4d-api/v1/authorize"    
    res = requests.post(auth_api,verify=False, headers=headers, json=data)
    if res.status_code!=200:
        print('Error requesting admin token - status_code - ' + str(res.status_code))
        try:
            print(res.json())
        except Exception:
            print(res.text)
        exit(1)
    admin_token = json.loads(res.text)['token']
    return str('Bearer '+admin_token)

def get_waston_knowledge_catalogs():
    bearer_token = get_admin_token()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': str(bearer_token)}
    url = cp4d_host + '/v2/catalogs'
    wkc_res = requests.get(url, headers=headers, verify=False)
    if wkc_res.status_code != 200:
        print('Error requesting get waston knowledge catalogs - status_code - ' + str(wkc_res.status_code))
        try:
            print(wkc_res.json())
        except Exception:
            print(wkc_res.text)
        return []
    return json.loads(wkc_res.text)['catalogs']

def get_waston_knowledge_catalogs_in_cache():
    wkc=[]
    cacheconfig=k8s.get_config_map(namespace=namespace,name=configmap_name)
    wkc_fetch_interval = float(cacheconfig[wkc_last_refresh_interval_key])
    last_fetch_timestamp = float(cacheconfig[wkc_last_refresh_key])
    if need_to_fetch(wkc_fetch_interval,last_fetch_timestamp)==True or not os.path.exists(wkc_cache_file):
        wkc = get_waston_knowledge_catalogs()
        with open(wkc_cache_file, 'w') as f:
            f.write(json.dumps(wkc))
        
        cacheconfig[wkc_last_refresh_key]=str(get_current_timestamp())
        k8s.set_config_map(namespace=namespace,name=configmap_name,data=cacheconfig)
        return wkc

    with open(wkc_cache_file, 'r') as f:
        wkc = json.loads(f.read())
    return wkc

def get_assets_by_catalog(catalog_id):
    bearer_token = get_admin_token()
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': str(bearer_token)}
    payload={"query":"*:*","limit":200}
    url = cp4d_host + f'/v2/asset_types/asset/search?catalog_id={catalog_id}'
    assets_res = requests.post(url, headers=headers, verify=False, json=payload)
    if assets_res.status_code != 200:
        print('Error requesting assets by catalog - status_code - ' + str(assets_res.status_code))
        try:
            print(assets_res.json())
        except Exception:
            print(assets_res.text)
        return []
    return json.loads(assets_res.text)

def get_CA_session(bearer_token):
    token = bearer_token[7:]
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': str(bearer_token), 'Cookie': f'ibm-private-cloud-session={token}'}
    url = cp4d_host + f'/cognosanalytics/api/v1/session'
    payload={}
    
    session_res = requests.put(url, headers=headers, verify=False, json=payload)
    return session_res

#List of roles in CA
def list_roles_in_CA():
    bearer_token = get_admin_token()
    cookies = get_CA_session(bearer_token).cookies
    CA_token = cookies.get_dict()['XSRF-TOKEN']
    headers = {'Content-Type': 'application/json',  'Accept': 'application/json', 'Authorization': str(bearer_token), 'X-XSRF-Token': CA_token}
    url = cp4d_host + '/cognosanalytics/api/v1/roles'   
    roles_res = requests.get(url, headers=headers, verify=False, cookies=cookies.get_dict())
    if roles_res.status_code != 200:
        print('Error requesting roles in CA - status_code - ' + str(roles_res.status_code))
        try:
            print(roles_res.json())
        except Exception:
            print(roles_res.text)
        return None
    return roles_res.text

def list_groups_in_CA():
    bearer_token = get_admin_token()
    cookies = get_CA_session(bearer_token).cookies
    CA_token = cookies.get_dict()['XSRF-TOKEN']
    headers = {'Content-Type': 'application/json',  'Accept': 'application/json', 'Authorization': str(bearer_token), 'X-XSRF-Token': CA_token}
    url = cp4d_host + '/cognosanalytics/api/v1/groups'   
    groups_res = requests.get(url, headers=headers, verify=False, cookies=cookies.get_dict())
    if groups_res.status_code != 200:
        print('Error requesting groups in CA - status_code - ' + str(groups_res.status_code))
        try:
            print(groups_res.json())
        except Exception:
            print(groups_res.text)
        return None
    return groups_res.text

def list_files_in_CA():
    bearer_token = get_admin_token()
    cookies = get_CA_session(bearer_token).cookies
    CA_token = cookies.get_dict()['XSRF-TOKEN']
    headers = {'Content-Type': 'application/json',  'Accept': 'application/json', 'Authorization': str(bearer_token), 'X-XSRF-Token': CA_token}
    url = cp4d_host + '/cognosanalytics/api/v1/content/iD09B05B01ECD40529491472D60140F4C/items'   
    files_res = requests.get(url, headers=headers, verify=False, cookies=cookies.get_dict())
    if files_res.status_code != 200:
        print('Error requesting groups in CA - status_code - ' + str(files_res.status_code))
        try:
            print(files_res.json())
        except Exception:
            print(files_res.text)
        return None
    print(files_res.text)
    return files_res.text

def main():
    list_files_in_CA()

if __name__ == '__main__':
    main()



    

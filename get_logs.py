import argparse
import subprocess
import os
import datetime


EXEC_PATH = os.getenv('EXEC_PATH')
BACKUP_PATH = os.getenv('BACKUP_PATH')

# OC
OC_PATH = os.getenv('OC_PATH')
OC_USERNAME = os.getenv('OC_USERNAME')
OC_PASSWORD = os.getenv('OC_PASSWORD')

ENVS = {
    'ta': 'bosa-dt-test-hcp-fedapi',
    'int': 'bosa-dt-acc-hcp-fedapi',
    'prod': 'bosa-dt-prod-hcp-fedapi'
}


def parse_arguments():
    """
    arguments can be:
        --env environment (ta, int, prod)
        --pod pod name (e.g., content-ds-service)
    :return:
    """
    parser = argparse.ArgumentParser(description='Retrieves logs from greenshift.')
    parser.add_argument('--env', dest='environment', help='Environment where to retrieve logs from.')
    parser.add_argument("--pod", dest='pod', help='Specific pod where to retrieve logs from.')
    parser.add_argument("--rsync", dest='rsync', help='Uses the rsync application to retrieve the complete logs if enabled, otherwise uses the oc logs command.')
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    environment = ENVS[arguments.environment]

    path = f"{EXEC_PATH}/{arguments.environment}/{datetime.datetime.now()}-{arguments.environment}"
    path = f'{path}-{arguments.pod}' if arguments.pod else path
    path = path.replace(':', '-').replace(' ', '_')

    if not os.path.exists(EXEC_PATH):
        os.mkdir(EXEC_PATH)

    if not os.path.exists(f"{EXEC_PATH}/{arguments.environment}"):
        os.mkdir(f"{EXEC_PATH}/{arguments.environment}")

    os.mkdir(path)

    # Login
    out = subprocess.Popen([OC_PATH, 'login', '-u', OC_USERNAME, '-p', OC_PASSWORD],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out.communicate()

    # project selection
    out = subprocess.Popen([OC_PATH, 'project', environment],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out.communicate()

    # retrieving pods list
    out = subprocess.Popen([OC_PATH, 'get', 'pod'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    pods = [s.split(b' ')[0] for s in stdout.split(b'\n')][1:-1]

    if arguments.pod:
        # If the pod is specified, only get logs from the filtered ones
        for pod in list(filter(lambda x: (arguments.pod in x.decode()), pods)):
            get_logs_for_pod(path=path, pod=pod, environment=arguments.environment, rsync=arguments.rsync)
    else:
        # else get logs of all the pods
        for pod in pods:
            get_logs_for_pod(path=path, pod=pod, environment=arguments.environment, rsync=arguments.rsync)

    # Copy of the logs to a backup path
    out = subprocess.Popen(["cp", "-R", f"{path}", f"{BACKUP_PATH}"])
    out.communicate()


def get_logs_for_pod(path: str, pod: str, environment: str, rsync: bool):
    print(f'Gettings logs for {pod}...')
    if rsync:
        pod_path = f'{path}/{pod.decode()}-{environment}'
        os.mkdir(pod_path)
        print(f'command={OC_PATH} rsync {pod.decode()}:/opt/bosa/ "{pod_path}"')
        out = subprocess.Popen([OC_PATH, 'rsync', f'{pod.decode()}:/opt/bosa/logs/', f'"{pod_path}"'],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        print(stderr)

    else:
        out = subprocess.Popen([OC_PATH, 'logs', pod],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        with open(f'{path}/{pod.decode()}-{environment}.log', 'w') as f:
            f.write(stdout.decode())
    print(f'Done.\n')


if __name__ == '__main__':
    main()

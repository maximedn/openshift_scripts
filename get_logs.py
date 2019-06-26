import argparse
import subprocess
import os
import datetime

BASE_PATH = './get_logs'

DRIVE_PATH = '/Users/maxime/bosa/onedrive/OneDrive - GCloud Belgium/logs'

USER_NAME = 'bosa-ext-maxd'

OC = '/Users/maxime/oc'

PROD_ENV = 'bosa-dt-prod-hcp-fedapi'
INT_ENV = 'bosa-dt-acc-hcp-fedapi'
TA_ENV = 'bosa-dt-test-hcp-fedapi'


def parse_arguments():
    parser = argparse.ArgumentParser(description='Retrieves logs from greenshift.')
    parser.add_argument('--env', dest='environment', help='Environment where to retrieve logs from.')
    parser.add_argument("--pod", dest='pod', help='Specific pod where to retrieve logs from.')
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    environment = INT_ENV if arguments.environment == 'int' else TA_ENV if arguments.environment == 'ta' else PROD_ENV

    path = f"{BASE_PATH}/{arguments.environment}/{datetime.datetime.now()}-{arguments.environment}"
    path = f'{path}-{arguments.pod}' if arguments.pod else path
    path = path.replace(':', '-').replace(' ', '_')

    if not os.path.exists(BASE_PATH):
        os.mkdir(BASE_PATH)

    if not os.path.exists(f"{BASE_PATH}/{arguments.environment}"):
        os.mkdir(f"{BASE_PATH}/{arguments.environment}")

    os.mkdir(path)

    out = subprocess.Popen([OC, 'login', '-u', USER_NAME, '-p', PASSWORD],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out.communicate()

    out = subprocess.Popen([OC, 'project', environment],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    out.communicate()

    out = subprocess.Popen([OC, 'get', 'pod'], stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = out.communicate()

    pods = [s.split(b' ')[0] for s in stdout.split(b'\n')][1:-1]

    if arguments.pod:
        pod = list(filter(lambda x: (arguments.pod in x.decode()), pods))[0]
        out = subprocess.Popen([OC, 'logs', pod],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        stdout, stderr = out.communicate()
        f = open(f'{path}/{pod.decode()}-{INT_ENV}.log', 'w')
        f.write(stdout.decode())
        f.close()
    else:
        for pod in pods:
            # pod_path = f'{path}/{pod.decode()}-{INT_ENV}'
            # os.mkdir(pod_path)
            # print(f'command={OC} rsync {pod.decode()}:/opt/bosa/logs/ "{pod_path}"')
            # out = subprocess.Popen([OC, 'rsync', f'{pod.decode()}:/opt/bosa/logs/', f'"{pod_path}"'],
            #                        stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            # stdout, stderr = out.communicate()
            # print(stderr)

            out = subprocess.Popen([OC, 'logs', pod],
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            stdout, stderr = out.communicate()
            f = open(f'{path}/{pod.decode()}-{INT_ENV}.log', 'w')
            f.write(stdout.decode())
            f.close()

    out = subprocess.Popen(["cp", "-R", f"{path}", f"{DRIVE_PATH}"])
    out.communicate()


if __name__ == '__main__':
    main()

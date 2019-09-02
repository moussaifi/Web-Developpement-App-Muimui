import paramiko
import time
from os.path import expanduser
from user_definition import *
from warnings import filterwarnings


filterwarnings('ignore')


def ssh_client():
    """Return ssh client object"""
    return paramiko.SSHClient()


def ssh_connection(ssh, ec2_address, user, key_file):
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(ec2_address, username=user,
                key_filename=expanduser("~") + key_file)
    return ssh


def create_or_update_environment(ssh):
    stdin, stdout, stderr = \
        ssh.exec_command("conda env create -f "
                         f"~/{git_repo_name}/environment.yml")
    if (b'already exists' in stderr.read()):
        stdin, stdout, stderr = \
            ssh.exec_command("conda env update -f "
                             f"~/{git_repo_name}/environment.yml")


def git_clone(ssh):

    stdin, stdout, stderr = ssh.exec_command("git --version")
    if(b"command not found" in stderr.read()):
        print("Installing Git.....")
        stdin, stdout, stderr = ssh.exec_command("sudo yum install -y git")

    cmd = "git config --global credential.helper store"
    stdin, stdout, stderr = ssh.exec_command(cmd)

    stdin, stdout, stderr = ssh.exec_command(f"cd {git_repo_name}")
    if (b"" is stderr.read()):
        print('found the repository, pulling the latest commits')
        cmd = f"cd {git_repo_name} && git pull"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)

    else:
        print("no folder in the root directory, cloning git repository")
        cmd = f"git clone https://{git_oauth_token}"
        cmd += f"@github.com/MSDS698/{git_repo_name}.git"
        stdin, stdout, stderr = ssh.exec_command(cmd)
        time.sleep(5)


cron_command = "echo '* * * * * /home/ec2-user/.conda/envs/muimui/bin/"
cron_command += "python3.7 /home/ec2-user/product-analytics-group-project"
cron_command += "-muimui/code/calculate_driving_time.py >/dev/null"
cron_command += " 2>&1' | crontab -"


def update_crontab(ssh):
    stdin, stdout, stderr = ssh.exec_command(cron_command)


def install_gcc(ssh):
    cmd = 'sudo yum install -y gcc72 gcc72-c++'
    stdin, stdout, stderr = ssh.exec_command(cmd)
    if not (b"" is stderr.read()):
        cmd = 'sudo apt install -y gcc'
        stdin, stdout, stderr = ssh.exec_command(cmd)


def run_webapp(ssh):
    cmd = f'cd ~/{git_repo_name}/code/src/webapp && '
    cmd += 'conda activate muimui && '
    cmd += 'gunicorn -D --threads 4 -b 0.0.0.0:8080 manage:app'
    stdin, stdout, stderr = ssh.exec_command(cmd)


def main():
    ssh = ssh_client()
    ssh_connection(ssh, ec2_address, user, key_file)
    git_clone(ssh)
    install_gcc(ssh)
    create_or_update_environment(ssh)
    run_webapp(ssh)
    ssh.close()


if __name__ == '__main__':

    main()

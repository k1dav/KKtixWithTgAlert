import argparse
import ipaddress
import json
import os
import pwd
import shlex
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_PATH = os.path.join(HERE, "config_templates")
PROJECT_NAME = "my-api"
parser = argparse.ArgumentParser()
parser.add_argument("container_type", choices=("local", "remote"))
args = parser.parse_args()


def main():
    ready_to_process_conf = True

    user_vars = {"username": 1000, "uid": os.getuid(), "gid": os.getgid()}
    if os.getuid() == 0:
        user_vars["uid"] = pwd.getpwnam(1000).pw_uid
        user_vars["gid"] = pwd.getpwnam(1000).pw_gid

    if args.container_type == "remote":
        ready_to_process_conf = False
        if remote_setup():
            ready_to_process_conf = True
        else:
            sys.exit("Something wrong in remote host.")

    if ready_to_process_conf:
        process_configs(args.container_type, user_vars)

        files_owned_by_users = [
            os.path.join(HERE, "devcontainer.json"),
            os.path.join(HERE, "docker-compose.yml"),
            os.path.join(HERE, f"images/{PROJECT_NAME}/Dockerfile"),
        ]
        # for f in files_owned_by_users:
        #     check_perms(f)

        print("Configuration files ready.")


def templates_to_config(input_path: str, user_vars):
    with open(input_path, "r") as f:
        data = [row.rstrip() for row in f]
    txt = "\n".join(data)
    constant_mappings = (
        ("HOME_PATH", os.environ["HOME"]),
        ("YOUR_USERNAME_HERE", user_vars["username"]),
        ("YOUR_UID_HERE", user_vars["uid"]),
        ("YOUR_GID_HERE", user_vars["gid"]),
    )
    for x, y in constant_mappings:
        txt = txt.replace(x, str(y))

    return "".join(txt)


def write_config(output_path: str, txt_conf: str, user_vars):
    with open(output_path, "w") as f:
        f.write(txt_conf)
    print(f"{output_path} saved.")


def process_configs(container_type: str, user_vars):
    file_list = ["docker-compose.yml", f"images/{PROJECT_NAME}/Dockerfile", f"images/{PROJECT_NAME}/requirements.txt"]
    if container_type == "local":
        file_list.append("devcontainer.json")
    else:
        write_remote_devcontainer_json()
        write_remote_docker_compose()

    write_vscode_settings(args.container_type)
    for f in file_list:
        src_fpath = os.path.join(TEMPLATES_PATH, f)
        dst_fpath = os.path.join(HERE, f)

        if not os.path.exists(os.path.dirname(dst_fpath)):
            os.makedirs(os.path.dirname(dst_fpath))

        conf = templates_to_config(src_fpath, user_vars)
        write_config(dst_fpath, conf, user_vars)


def create_dirs(path: str):
    if not os.path.exists(path):
        os.makedirs(path)


def check_perms(path: str, uid=1000, gid=1000):
    stat = os.stat(path)
    if (
        (isinstance(uid, int) or isinstance(gid, int))
        and (stat.st_uid != uid or stat.st_gid != gid)
    ) or (
        (isinstance(uid, str) or isinstance(gid, str))
        and (
            stat.st_uid != pwd.getpwnam(uid).pw_uid
            or stat.st_gid != pwd.getpwnam(gid).pw_uid
        )
    ):
        print(f"The uid and gid of {path} has to be {uid}.")
        print("Trying to modify the ownship...")
        chown_recursive(path, uid, gid)


def chown_recursive(path: str, uid=1000, gid=1000):
    command = f"chown {uid}:{gid} -R {path}"
    p = subprocess.run(shlex.split(command))
    if p.returncode != 0:
        sys.exit("Failed! please run this script as root again.")
    else:
        print(f"{path} ownership has been changed to {uid}:{gid}")
        return p


def conn_ready(ip_addr: str) -> bool:
    p = run(f"ping -c1 {ip_addr}")
    return p.returncode == 0


def remote_setup():
    remote_host_ip = input_ip_addr()
    if not conn_ready(remote_host_ip):
        sys.exit(f"Can't connect to host, check your connection to {remote_host_ip}")
    if not check_keys:
        run("ssh-keygen -t rsa -N '' -f ~/.ssh/id_rsa")

    remote_user = input_remote_user()
    run(f"ssh-copy-id {remote_user}@{remote_host_ip}")
    p = remote_run(remote_user, remote_host_ip, "ls")

    if PROJECT_NAME.encode("utf-8") not in p.stdout:
        print(f"{PROJECT_NAME} not exists on remote host, cloning...")
        run(
            remote_run(
                remote_user,
                remote_host_ip,
                f"'GIT_SSH_COMMAND=\"ssh -o StrictHostKeyChecking=no\" git clone git@hack.ap-mic.com:apmic/{PROJECT_NAME}.git'",
            )
        )
    else:
        print(f"{PROJECT_NAME} exists on remote host.")

    display_command = (
        f'\t{os.path.join(HERE, "setup-tunnel.sh")} {remote_user}@{remote_host_ip}\n'
    )
    print(
        (
            f"\n\n{'='*(len(display_command)+6)}\n"
            "Please open a SEPARATE terminal OUTSIDE vscode, "
            "and run\n"
            f"{display_command}"
            "before you run remote container!"
            f"\n{'='*(len(display_command)+6)}\n\n"
        )
    )
    return True


def check_keys():
    if os.path.exists("~/.ssh"):
        for k in os.listdir("~/.ssh"):
            if "id_rsa" in k:
                return True
    return False


def input_ip_addr():
    while True:
        ip_addr = input("Input your remote host ip / FQDN: ")
        try:
            ipaddress.ip_address(ip_addr)
            return ip_addr
        except ValueError:
            print("IP Address not valid, please try again. e.g. 192.168.0.1")


def input_remote_user() -> str:
    while True:
        txt = input(
            (
                "\nInput your username on remote host, "
                f"press Enter to use your current login name ({1000}): "
            )
        )
        if len(txt.strip()) > 0:
            return txt
        else:
            return 1000


def write_remote_devcontainer_json():
    src_file = os.path.join(HERE, "config_templates", "devcontainer.json")
    with open(src_file, "r") as f:
        config = json.load(f)

    config["dockerComposeFile"] = ["docker-compose.yml", "docker-compose.remote.yml"]

    with open(os.path.join(HERE, "devcontainer.json"), "w") as f:
        f.write(json.dumps(config, indent=4, sort_keys=True))


def write_remote_docker_compose():
    src_file = os.path.join(HERE, "config_templates", "docker-compose.remote.yml")

    with open(src_file, "r") as f:
        data = [row.rstrip() for row in f]
    txt = "\n".join(data)
    txt = txt.replace("HOME_PATH", os.environ["HOME"])

    target_file = os.path.join(HERE, "docker-compose.remote.yml")
    with open(target_file, "w") as f:
        f.write(txt)
    print(f"{target_file} saved.")


def write_vscode_settings(config_type):
    target_file = os.path.join(os.path.dirname(HERE), ".vscode/settings.json")

    if not os.path.exists(os.path.dirname(target_file)):
        os.makedirs(os.path.dirname(target_file))

    if config_type == "remote":
        if os.path.exists(target_file):
            with open(target_file, "r") as f:
                config = json.load(f)
            config["docker.host"] = "tcp://localhost:23750"
        else:
            config = {"docker.host": "tcp://localhost:23750"}
    else:
        if os.path.exists(target_file):
            with open(target_file, "r") as f:
                config = json.load(f)
            if "docker.host" in config:
                del config["docker.host"]

    with open(target_file, "w") as f:
        f.write(json.dumps(config, indent=4, sort_keys=True))
    print(f"{target_file} saved.")


def run(command: str):
    print(f"\n--> {command}")
    return subprocess.run(shlex.split(command), stdout=subprocess.PIPE)


def remote_run(user: str, host: str, command: str):
    return run(f"ssh -A {user}@{host} {command}")


if __name__ == "__main__":
    main()

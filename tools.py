import os
from subprocess import call


def is_executable(path):
    return os.path.isfile(path) and os.access(path, os.X_OK)


def get_all_paths(base_path, extension, exclude=()):
    matches = []
    for root, dirs, files in os.walk(base_path, topdown=True):
        dirs[:] = [d for d in dirs if d not in exclude]

        for filename in files:
            if filename.endswith(extension):
                matches.append(os.path.join(root, filename))

    return matches


def call_external(command, *args):
    if not is_executable(command):
        raise EnvironmentError

    cmd = list(args)
    cmd.insert(0, command)
    cmd_result_code = call(cmd, shell=True)

    return cmd_result_code == 0

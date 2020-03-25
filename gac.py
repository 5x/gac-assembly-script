import os
import sys

from tools import call_external, is_executable, get_all_paths
from register_helpers import get_reg_values_map, get_reg_keys

if sys.platform != 'win32':
    raise OSError('This script work only on OS Windows.')

DEFAULT_OUT_FOLDER_NAME = 'assemblies'
SDK_KEY_NAME = r'SOFTWARE\Microsoft\Microsoft SDKs\Windows'
NET_FRAMEWORK_KEY_PREFIX = r'SOFTWARE\Microsoft\NET Framework Setup\NDP'
DEFAULT_NET_FRAMEWORK_PATH = r'%SYSTEMROOT%\Microsoft.NET\Framework'
CS_COMPILER_NAME = 'csc.exe'
BUILD_DEBUG = False


def get_dot_net_versions():
    values = get_reg_keys(NET_FRAMEWORK_KEY_PREFIX)
    versions = [i[1:] for i in values if len(i) > 1 and i[1].isdigit()]
    versions.sort(key=lambda v: [int(part) for part in v.split('.')])

    return versions


def find_csc_path(version):
    version = 'v{0}'.format(version)
    reg_key = os.path.join(NET_FRAMEWORK_KEY_PREFIX, version)
    possible_paths = (
        get_reg_values_map('{0}\\Client'.format(reg_key)).get('InstallPath'),
        get_reg_values_map(reg_key).get('InstallPath'),
        os.path.join('{0}64'.format(DEFAULT_NET_FRAMEWORK_PATH), version),
        os.path.join(DEFAULT_NET_FRAMEWORK_PATH, version),
    )

    for path in possible_paths:
        if not path:
            continue

        tool_path = os.path.join(str(path), CS_COMPILER_NAME)
        if is_executable(tool_path):
            return tool_path


def get_csc_path(version_list):
    for version in version_list[::-1]:
        path = find_csc_path(version)
        if path:
            return path

    raise WindowsError('Can\'t find CSCompiler({}).'.format(CS_COMPILER_NAME))


def create_strong_name_key(output_path):
    """Creates a new, random key pair and stores.

    About another .net sn options see:
    https://msdn.microsoft.com/library/k5b5tt23(v=vs.71).aspx
    """
    return call_external(tools['sn'], '-q', '-k', output_path)


def compile_net_module(input_files, output_path):
    """Compile source code files into a single file .netmodule assembly.

    About used options see:
    https://msdn.microsoft.com/en-us/library/ms379563(v=vs.80).aspx
    """
    build_type = '/debug' if BUILD_DEBUG else '/optimize'
    return call_external(
        tools['csc'],
        build_type,
        '/target:module',
        '/out:{0}'.format(output_path),
        '/nologo',
        *input_files)


def link_assembly(assembly, key, out_filename):
    return call_external(
        tools['al'],
        '/out:{0}'.format(out_filename),
        '/keyfile:{0}'.format(key),
        '/nologo',
        assembly)


def install_gac(assembly_path):
    return call_external(tools['gacutil'], '/i', assembly_path, '/f',
                         '/nologo')


def get_gac_list(assembly_name):
    return call_external(tools['gacutil'], '/l', assembly_name, '/nologo')


def print_files(paths, prefix=''):
    prefix_count = len(prefix)

    for path in paths:
        print(path[prefix_count:])


def check_writable_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

    return os.path.isdir(directory) and os.access(directory, os.W_OK)


def prompt(message, default):
    default = str(default)
    user_input = input('[USER] {0}(default {1}): '.format(message, default))

    return user_input if user_input else default


def prompt_path(message):
    path = ''

    while not os.path.isdir(path):
        path = input('[USER] {0}'.format(message))

    return path


def confirm(message):
    input_confirm = input('[USER] {0}[Y, n]: '.format(message))

    return input_confirm in ('Y', 'y', '1')


def step(status, msg, required=True):
    status_symbol = 'DONE' if status else 'FAIL' if required else 'SKIP'
    msg = '[{0}] {1}'.format(status_symbol, msg)

    print(msg)

    if not status and required:
        input('Press any key to continue.')
        sys.exit()


if __name__ == '__main__':
    dot_net_versions = get_dot_net_versions()
    sdk_folder = get_reg_values_map(SDK_KEY_NAME).get('CurrentInstallFolder')

    tools = {
        'sn': os.path.join(sdk_folder, 'Bin', 'sn.exe'),
        'al': os.path.join(sdk_folder, 'Bin', 'al.exe'),
        'gacutil': os.path.join(sdk_folder, 'Bin', 'gacutil.exe'),
        'csc': get_csc_path(dot_net_versions)
    }

    print('[INFO] Available .Net versions: {0}'.format(dot_net_versions))
    print('[INFO] DonNET SDK folder: {0}'.format(sdk_folder))
    print('[INFO] DonNET Framework Compiler path: {0}'.format(tools['csc']))

    output_dir = os.path.join(os.getcwd(), DEFAULT_OUT_FOLDER_NAME)

    source_path = prompt_path('Source files path \n> ')
    source_files = get_all_paths(source_path, '.cs', ('obj', 'bin', 'temp'))

    print('[INFO] Source files:')
    print_files(source_files, source_path)

    default_build_name = os.path.basename(source_path)
    if not default_build_name:
        default_build_name = 'component'

    component_name = prompt('Enter component name', default_build_name)

    key_filename = '{0}.snk'.format(component_name)
    key_path = os.path.join(output_dir, key_filename)
    net_module_filename = '{0}.netmodule'.format(component_name)
    net_module_path = os.path.join(output_dir, net_module_filename)
    dll_filename = '{0}.dll'.format(component_name)
    dll_path = os.path.join(output_dir, dll_filename)

    step(check_writable_dir(output_dir),
         'Check output directory: {0}'.format(output_dir))

    step(create_strong_name_key(key_path),
         'Strong key pair created: {0}'.format(key_filename))

    step(compile_net_module(source_files, net_module_path),
         'DotNET module compiled: {0}'.format(net_module_filename))

    step(link_assembly(net_module_path, key_path, dll_path),
         'Assembly successful linked: {0}'.format(dll_filename))

    user_answer = confirm('Install to GAC(Default no)')
    next_step_check = install_gac(dll_path) if user_answer else False
    step(next_step_check, 'Install assembly to GAC.', required=user_answer)

    if next_step_check:
        get_gac_list(component_name)

    input('Success. \n\nPress ENTER to exit.\n')

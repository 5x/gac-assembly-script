from winreg import OpenKey, CloseKey, EnumValue, EnumKey, HKEY_LOCAL_MACHINE


def _register_walk(handle, storage, reg_key_path, prefix):
    try:
        reg_handle = OpenKey(prefix, reg_key_path)
    except OSError:
        return storage

    index = 0
    while True:
        try:
            handle(storage, reg_handle, index)
            index += 1
        except OSError:
            break

    CloseKey(reg_handle)

    return storage


def get_reg_values_map(reg_key_path, prefix=HKEY_LOCAL_MACHINE):
    def handle(storage, reg_handle, index):
        key, value, _ = EnumValue(reg_handle, index)
        storage[key] = value

    return _register_walk(handle, {}, reg_key_path, prefix)


def get_reg_keys(reg_key_path, prefix=HKEY_LOCAL_MACHINE):
    def handle(storage, reg_handle, index):
        key = EnumKey(reg_handle, index)
        storage.append(key)

    return _register_walk(handle, [], reg_key_path, prefix)

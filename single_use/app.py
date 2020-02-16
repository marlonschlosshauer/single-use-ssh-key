from hashlib import sha256
import argparse
import yaml
import os.path
import sys
import base64


def set_sshd_config(config):
    '''
    Set LogLevel in config to Verbose
    '''
    if not os.path.isfile(config):
        exit(1)
    else:
        # Translaten ~ to /home/user
        config = os.path.expanduser(config)

    with open(config, 'r+') as cfg:
        content = cfg.read()

        if content.rfind('LogLevel Verbose') == -1:
            start = content.rfind('LogLevel')

            # From 'LogLevel' to end of line
            end = start + 9 + content[start + 9:].find('\n')

            first_half = content[:start + 9]
            second_half = content[end:]

            cfg.seek(0)
            cfg.truncate()
            cfg.write(first_half + 'Verbose' + '\n' + second_half)


def append_rc(config, call):
    '''
    Append this script to .sshrc
    '''

    # Translaten ~ to /home/user
    config = os.path.expanduser(config)

    if not os.path.isfile(config):
        # Create file
        with open(config, 'w'):
            pass

    with open(config, 'a+') as cfg:
        cfg.seek(0)
        content = cfg.read()

        if content.rfind(call) == -1:
            cfg.seek(0, os.SEEK_END)
            cfg.write('\n' + call)


def get_path_to_config():
    path_to_config = os.path.abspath(os.path.dirname(sys.argv[0]))
    path_to_config = path_to_config[:path_to_config.rfind('/')]
    path_to_config = path_to_config + '/config.yml'

    # Translaten ~ to /home/user
    path_to_config = os.path.expanduser(path_to_config)
    return path_to_config


def install(path_to_config=None):
    if path_to_config is None:
        path_to_config = get_path_to_config()
    with open(path_to_config) as settings:
        config = yaml.safe_load(settings)

        sshd = os.path.expanduser(config['sshd_config'])
        call = os.path.expanduser(config['call'])

        set_sshd_config(sshd)
        append_rc(sshd, call)


def uninstall():
    '''
    Removes the appended script in .sshrc
    '''
    path_to_config = get_path_to_config()

    with open(path_to_config) as settings:
        config = yaml.safe_load(settings)

        # Translaten ~ to /home/user
        ssh_config = os.path.expanduser(config['ssh_config'])
        call = os.path.expanduser(config['call'])

        with open(ssh_config, 'a+') as cfg:
            cfg.seek(0)
            content = cfg.read().replace(call, '')
            cfg.seek(0)
            cfg.truncate()
            cfg.write(content)


def get_used_key(path):
    '''
    Get key that was last used to login, from logs
    :param path: location of sshd log
    :return: str of last used public key in an encoded format
    '''

    # Translaten ~ to /home/user
    path = os.path.expanduser(path)

    with open(path) as rsa:
        key = rsa.read()
        # Look for key that last entered
        start = key.rfind('Accepted publickey ')
        start = 11 + start + key[start:].find('RSA SHA256:')
        end = key[start:].find('\n')
        return key[start:start + end]


def encode_key(key):
    '''
    sshd saves public keys encoded like this.
    :param key: string of public key thats to be encoded
    :return: str of encoded public key
    '''
    # Remove non-key arguments
    key = key[8:key.rfind(' ')]
    # Decode to base64
    key = base64.standard_b64decode(key)
    # Encode SHA256
    key = sha256(key).digest()
    # Encode to base64
    key = base64.standard_b64encode(key)
    return key


def NoCommentProvided(Exception):
    pass


def delete_from_authorizes_keys(used_key, comment, authorized_keys):
    '''
    Find used_key in authorized_keys and remove it
    :param used_key: public key thats to be removed
    :param comment: public key with this comment
    :param authorized_keys: path to authorized keys
    '''
    # Error Handling : Should not delete every last used key, TODO: maybe option in future
    if comment is None:
        raise NoCommentProvided(
            'No comment to search for was provided. This is not allowed (right now) because every key would be deleted after single use, even ones used for administration duty.'
        )

    with open(authorized_keys, 'r+') as keys:
        raw_keys = keys.read().split('\n')

        # Remove end-of-file backslash
        # raw_keys.pop(-1)

        counter = -1
        for key in raw_keys:
            counter = counter + 1
            # If comment is specified, only look at key with comment

            if key.find(comment) == -1:
                continue

            # Remove trailing padding (=)
            decoded_key = (encode_key(key)[:-1]).decode('utf8')
            if decoded_key == used_key:
                print('Found key {} at position {}.'.format(used_key, counter))
                # Remove key from keys
                raw_keys.pop(counter)
                keys.seek(0)
                keys.truncate()
                keys.write('\n'.join(raw_keys))
                print('Removed key.')
                return


def delete(comment=None, path_to_config=None):
    if path_to_config is None:
        path_to_config = get_path_to_config()
    else:
        # Make sure ~ is translated to /home/user/
        path_to_config = os.path.expanduser(path_to_config)

    with open(path_to_config) as settings:
        config = yaml.safe_load(settings)

        if comment is None:
            comment = config['comment']

        authorized_keys = os.path.expanduser(config['authorized_keys'])
        key = get_used_key(os.path.expanduser(config['sshd_log']))

        delete_from_authorizes_keys(key, comment, authorized_keys)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-i', '--install', action='store_true')
    parser.add_argument('-u', '--uninstall', action='store_true')
    args = parser.parse_args()

    if args.install:
        install()
        exit(0)

    if args.delete:
        delete()
        exit(0)

    if args.uninstall:
        uninstall()
        exit(0)


if __name__ == '__main__':
    main()

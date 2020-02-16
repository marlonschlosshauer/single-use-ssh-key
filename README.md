## single-use-ssh-key
Treat specific ssh-keys as single use, removing them after logging in.

*Note :* __This is a proof-of-concept__. SSH usually writes logins to `/var/log/auth.log`, which requires sudo privilegs to read. This project needs to read that file on every login.

### Requirements
- Python (tested on Python 3.5.3)
- ssh (tested on OpenSSH 7.4)


### Quick Start
Run `single-use-ssh-key --install` on your remote maschine, generate a key with the comment `single-use-ssh-key`.
Add the public key to the remote maschine.
Login.
Done, the key logged in with was already removed.


### Install
Clone repo, change into the folder and run `pip3 install -e .`

Verify that the links in `config.yml` point to the correct files

Defaults where tested on Raspbian-10+deb9u7.

* Important are :
  * `sshd_config`: /etc/ssh/sshd_config
  * `sshd_log`: /var/log/auth.log
  * `ssh_config`: \~/.ssh/rc
  * `authorized_keys`: \~/.ssh/authorized_keys

Run the script with the `--install` option

`single-use-ssh-key --install`


Generate a key with the comment that you specified in config.yml

`ssh-keygen -C "single-use-key"`


Place the public key on your remote maschine

`ssh-copy-id -i . user@host`


### Usage
This script checks which key was last used to login (default looks in `/var/log/auth.log`), then tries to remove the key (default from `~/.ssh/authorized_keys`) if that key has the wanted comment (default `single-use-ssh-key`).

After installing, login using the key that uses the comment.

`ssh -i <private key filename> user@host`

Done.


### Uninstalling
`single-use-ssh-key --uninstall` removes this script from the `sshrc` file specified in `config.yml`.


*Note :* The LogLevel set by the install script will not be reverted from `Verbose`.



# wazo-auth-keys [![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-auth-keys)](https://jenkins.wazo.community/job/wazo-auth-keys)

A small tool to automatically provision/configure service keys in Wazo.

## Pre-requisite

Configuration to connect to the wazo-auth daemon are fetched from the `wazo-auth-cli`
configuration. It is possible to specify the wazo-auth-cli configuration directory with the
`--wazo-auth-cli-config` option or with the environment variable `WAZO_AUTH_CLI_CONFIG`. See the
[wazo-auth-cli documentation](https://github.com/wazo-platform/wazo-auth-cli) for more informations.


## Configuration

Configuration file is at the following location:

```
/etc/wazo-auth-keys/config.yml
```

The `/etc/wazo-auth-keys/config.yml` is the default configuration file shipped with the debian
package. This file should not be modified but can be used as a reference.

```sh
wazo-auth-keys --config ~/.config/wazo-auth-keys/config.yml
```


## Commands

### Completion

```sh
wazo-auth-keys complete > /etc/bash_completion.d/wazo-auth-keys
```

### Services

Updating services

```sh
wazo-auth-keys service update
```

Cleaning service

```sh
wazo-auth-keys service clean
```

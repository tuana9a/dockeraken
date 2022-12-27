# dockeraken

Simple Docker Agent run jobs

## how to setup (**python >= 3.8**)

```bash
mkdir /opt/dockeraken
```

```bash
python3 -m venv .venv
```

```bash
source .venv/bin/activate
```

```bash
pip install git+https://github.com/tuana9a/dockeraken
```

create service file `/etc/systemd/system/dockerakend.service`

```ini
[Unit]
Description=Dockeraken Daemon

[Service]
ExecStart=/opt/dockeraken/.venv/bin/dockerakend --config /your/path/to/dockeraken.ini

[Install]
WantedBy=default.target
```

config example see `dockeraken.ini.example`

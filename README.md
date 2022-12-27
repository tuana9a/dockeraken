# dockeraken

Simple Docker Agent run jobs

## package

```bash
python setup.py sdist
```

## systemd-service

`/etc/systemd/system/dockerakend.service`

```conf
[Service]
Environment="PYTHONUNBUFFERED=1"
ExecStart=/opt/dockerakend/.venv/bin/dockerakend

[Install]
WantedBy=default.target
```

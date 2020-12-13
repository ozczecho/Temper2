# TEMPer2 Mqtt wrapper

A wrapper for TEMPer2 USB device giving temperature readouts. It sends the current temperature to Home Assistant via MQTT. The code also includes system internal temperature readout via a shell script.

## hid_query Dependency

This project has a dependency on `https://github.com/edorfaus/TEMPered/blob/master/utils/hid-query.c`.


## Python Setup

Easiest way to get started is to create a virtual environment:

```sh
virtualenv venv --python=python3
```

The above will create a virtual environment in the current directory called `venv`. Activate the virtual environment so you can install the project dependencies:

```sh
source venv/bin/activate
pip install -r requirements.txt
```

You should be able to run the project interactively
```
python3 temper2.py
```
If you add more dependencies, remember to run `pip install -r requirements.txt` to keep the `requirements.txt` file current.
 
## Systemd Service Setup

I have included a simple unit file so that the wrapper can be setup to run as a systemd service. Edit the files as required.

* `sudo cp temper2.service /etc/systemd/system/`
* Edit the `service` file to suit your requirements
* `sudo systemctl daemon-reload`
* `sudo systemctl start temper2`
* `sudo systemctl status temper2`
* `sudo systemctl enable temper2` so the service auto starts.

### Config file

The wrapper relies on a config file to be present in the same directory. The config file has to be called `config.json`. A sample is included below:

```json
{
    "logLevel": "INFO",
    "mqtt":{
        "host": "host",
        "port": 2299,
        "user": "user",
        "password": "pwd",
        "client": "TEMPer2"
    },
    "publishServerRackTemperatureTopic": "home/server_room/temperature",
    "hidQueryPath": "/usr/local/bin/hid-query",
    "systemTemperatureScript": "./cubi_temp.sh",
    "publishSystemTemperatureTopic": "home/cubi/temperature",
    "scanInterval": 60
}
``` 


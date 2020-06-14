

## Hardware requirements

- Raspberry Pi
- [BME680 sensor](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors-bme680/) properly installed on the Raspberry Pi.

This project has been tested only on Raspberry Pi 4B and with the [Pimoroni BME680 sensor](https://shop.pimoroni.com/products/bme680-breakout).

## Setup

- Install Python3 if needed.
- Install Docker.
- Enable i2c via Raspberry Pi configuration, typing ``sudo raspi-config``.
 

## Build and run the image

1. Create a configuration file (e.g. ``default_config.yml``) and place it in a directory (e.g. ``/home/pi/dev/sensorics/bme680-data-recorder/mydata``).
2. Build image: ``docker build  -t bme680 .`` 
3. Run the container: `` docker run -ti --name mybme680 --device /dev/i2c-1 -v /home/pi/dev/sensorics/bme680-data-recorder/mydata/:/data:rw --env BME680_CONFIG_FILE=/data/default_config.yml bme680``.

## Configuration

The configuration file sets the following arguments:

- ``humidity_oversample``: Oversampling factor for temperature. The higher the value, the grater the reduction in noise and loss in accuracy. Possible values: ``OS_NONE``, ``OS_1X``, ``OS_2X``, ``OS_4X``, ``OS_8X``, ``OS_16X``. Recommended setting: ``OS_2X``
- ``temperature_oversample``: "OS_8X"
- ``pressure_oversample``: "OS_4X"
- ``filter_size``: "FILTER_SIZE_3"
- ``enable_gas_meas``: "yes"
- ``temp_offset``: 0
- ``gas_heater_temperature``: 320
- ``gas_heater_duration``: 150
- ``gas_heater_profile``: 0
- ``burn_in_time``: 10
- ``sampling_time``: 3
- ``humidity_baseline``: 40.0
- ``humidity_weight``: 0.25
- ``top_gas_reading_file``: "/data/top_gas_readings.txt"
- ``top_gas_reading_size``: 50
- ``log_level``: "INFO"
- ``log_telegraf``: "yes"

See ``data/default_config.yml`` for an example 

## Formula for computing air quality


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

The configuration file sets the following arguments.

See ``data/default_config.yml`` for example default config. 

### Pimoroni library configuration

The following argument set the arguments for the [Pimorini BME680 library](https://github.com/pimoroni/bme680-python/tree/master/library). Please refer to the library and the [Pimoroni tutorial](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout) for more details on these arguments.

- ``humidity_oversample``: Oversampling factor for humidity. The higher the value, the grater the reduction in noise and loss in accuracy. Possible values: ``OS_NONE``, ``OS_1X``, ``OS_2X``, ``OS_4X``, ``OS_8X``, ``OS_16X``. Recommended setting: ``OS_2X``
- ``temperature_oversample``: Oversampling factor for temperature. The higher the value, the grater the reduction in noise and loss in accuracy. Possible values: ``OS_NONE``, ``OS_1X``, ``OS_2X``, ``OS_4X``, ``OS_8X``, ``OS_16X``. Recommended setting: ``OS_8X``
- ``pressure_oversample``: Oversampling factor for pressure. The higher the value, the grater the reduction in noise and loss in accuracy. Possible values: ``OS_NONE``, ``OS_1X``, ``OS_2X``, ``OS_4X``, ``OS_8X``, ``OS_16X``. Recommended setting: ``OS_4X``
- ``filter_size``: Filters out transient spiky values due to environment anomalies. Possible values: ``FILTER_SIZE_[0|1|3|7|15|31|63|127]``. Recommended setting: ``FILTER_SIZE_3``. 
- ``enable_gas_meas``: Enables or disables gas measurements. Possible values: ``yes``, ``no``. Recommended setting: ``yes``.
- ``temp_offset``: Temperature offset. Recommended setting: ``0``. 
- ``gas_heater_temperature``: Gas sensor heater temperature. Recommended setting: ``320``.
- ``gas_heater_duration``: Heating duration in ms, must be between ``1`` and ``4032``. Recommended value: ``150``.
- ``gas_heater_profile``: Gas heater profile, must be between ``0`` and ``9``. Recommended value: `` 0``.

### Air quality index configuration

- ``burn_in_time``: Seconds of burn-in for calibrating the gas sensor before actual air quality values are computed. Recommended value: ``300``.
- ``sampling_time``: Seconds between each sensor measurement. Sampling at more than 3 seconds may provide inaccurate gas measurements. Recommended value: ``3``.
- ``humidity_baseline``: Humidity baseline for air quality formula. Recommended value: ``40.0``
- ``humidity_weight``: Humidity weight for air quality formula. Recommended value: ``0.25``
- ``top_gas_reading_file``: Output file in the Docker container file system where top gas reading will be stored. Defaults: ``/data/top_gas_readings.txt``.
- ``top_gas_reading_size``: Length of list of top gas readings. Recommended value: ``50``.

### Other configurations

- ``log_level``: Log level. Recommended value: ``INFO``.
- ``log_telegraf``: Enable logging for [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/). Telegraf logs will be in [InfluxDB protocol format](https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_reference/) as follows: ``weather temperature=<value>,pressure=<value>,humidity=<value>,gas=<value>,air_quality=<value>,aiq=<text value>``. Possible values: ``yes``, ``no``.


## Formula for computing air quality

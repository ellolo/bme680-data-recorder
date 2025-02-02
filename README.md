# BME680 Indoor Air Quality Data Recorder
A Docker image that reads the BME680 sensor data using the [Pimoroni BME680 library](https://github.com/pimoroni/bme680-python/), and outputs the following weather readings as logs in stderr:
temperature, pressure, humidity, gas resistance, Indoor Air Quality index. Example of logs from a running container:

```
20-06-14 09:55:29 - INFO - burn in 1561772.05 (0.11 / 10)
20-06-14 09:55:30 - INFO - burn in 332806.27 (1.19 / 10)
20-06-14 09:55:32 - INFO - burn in 375707.31 (2.21 / 10)
20-06-14 09:55:33 - INFO - burn in 390736.44 (3.21 / 10)
20-06-14 09:55:34 - INFO - burn in 393492.95 (4.22 / 10)
20-06-14 09:55:35 - INFO - burn in 420434.33 (5.23 / 10)
20-06-14 09:55:36 - INFO - burn in 434630.80 (6.24 / 10)
20-06-14 09:55:37 - INFO - burn in 432384.65 (7.25 / 10)
20-06-14 09:55:38 - INFO - burn in 451640.63 (8.26 / 10)
20-06-14 09:55:39 - INFO - burn in 458446.16 (9.26 / 10)
20-06-14 09:55:40 - INFO - Top gas reading file does not exist. Initializing it.
20-06-14 09:55:40 - INFO - 21.15 C, 954.96 %RH , 55.63 hPa, 458132.37 Ohms, air quality: 32.56(Good)
20-06-14 09:55:43 - INFO - 21.18 C, 954.96 %RH , 55.56 hPa, 476731.74 Ohms, air quality: 32.42(Good)
20-06-14 09:55:46 - INFO - 21.14 C, 954.97 %RH , 55.51 hPa, 465136.47 Ohms, air quality: 33.54(Good)
```
Optionally, the container can output logs in stdout in InfluxDB protocol (see section "Configuration"). These logs can be ingested by [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/) and further stored in InfluxDB.

## Hardware requirements

- Raspberry Pi
- [BME680 sensor](https://www.bosch-sensortec.com/products/environmental-sensors/gas-sensors-bme680/) properly installed on the Raspberry Pi.

This project has been tested only on Raspberry Pi 4B and with the [Pimoroni BME680 sensor](https://shop.pimoroni.com/products/bme680-breakout).

## Setup

- Install Python3 if needed.
- Install Docker.
- Enable i2c via Raspberry Pi configuration, typing ``sudo raspi-config``.
 

## Usage

1. Create a configuration file (e.g. ``default_config.yml``) and place it in a directory (e.g. ``/home/pi/dev/sensorics/bme680-data-recorder/mydata``).
2. Build image: ``docker build  -t bme680 .`` . 
3. Run the container: `` docker run -ti --name mybme680 --device /dev/i2c-1 -v /home/pi/dev/sensorics/bme680-data-recorder/mydata/:/data:rw --env BME680_CONFIG_FILE=/data/default_config.yml bme680``.
4. Run ``docker logs mybme680`` to get the logs of the container.

## Configuration

The configuration file sets the following arguments.

See ``data/default_config.yml`` for example default config. 

### Pimoroni library configuration

The following sets the arguments for the [Pimorini BME680 library](https://github.com/pimoroni/bme680-python/tree/master/library). Please refer to the library and the [Pimoroni tutorial](https://learn.pimoroni.com/tutorial/sandyj/getting-started-with-bme680-breakout) for more details on these arguments.

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
- ``humidity_weight``: Humidity weight for air quality formula, between ``0`` and ``1``. Recommended value: ``0.25``
- ``top_gas_reading_file``: Output file in the Docker container file system where top gas reading will be stored. Defaults: ``/data/top_gas_readings.txt``.
- ``top_gas_reading_size``: Length of list of top gas readings. Recommended value: ``50``.

### Other configurations

- ``log_level``: Log level. Recommended value: ``INFO``.
- ``log_telegraf``: Enable logging for [Telegraf](https://www.influxdata.com/time-series-platform/telegraf/). Telegraf logs will be in [InfluxDB protocol format](https://docs.influxdata.com/influxdb/v1.8/write_protocols/line_protocol_reference/) as follows: ``weather temperature=<value>,pressure=<value>,humidity=<value>,gas=<value>,air_quality=<value>,aiq=<text value>``. Possible values: ``yes``, ``no``.


## Computation of Indoor Air Quality (IAQ)

The AIQ is computed using the formula proposed by David Bird at Adafruit, whose idea and concept is Copyright (c) of David Bird 2018:

`` aiq_score = 100 * (gas_score + hum_score )``

where: 


- ``gas_score = ( 1 - hum_weight ) *  min (1, ( gas / gas_perfect_air ) )``

- ``hum_score = hum_weight *  hum / hum_perfect_air `` if ``hum > hum_perfect_air``

- ``hum_score = hum_weight * ( 100 - hum)  / ( 100 - hum_perfect_air )`` if ``hum <= hum_perfect_air``

Parameters in the above formula are set as follows:

- ``hum_weight``: importance of humidity in the formula. When 0.50 gas and humidity have equal importance.
- ``hum_perfect_air``: value of humidity in perfect environment, typically 40%.
- ``gas_perfect_air``: value of gas resistance in Ohms in perfect environment condition. Higher value corresponds to better air quality. This value is set automatically in the code by computing the average of the top 50 gas reading since the start of recording.


The resulting ``aiq_score`` is classified as follows:

| gas-score | air quality                    |
|-----------|--------------------------------|
| 0-50      | Good                           |
| 51-150    | Moderate                       |
| 151-175   | Unhealthy for sensitive people |
| 176-200   | Unhealthy                      |
| 201-300   | Very unhealthy                 |
| >300      | Hazardous                      |

 

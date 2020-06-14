import os
import sys
import argparse
import logging
import time
import heapq
from statistics import mean
import confuse
import bme680

logger = logging.getLogger(__name__)
logger_telegraf = logging.getLogger(f"{__name__}-telegraf")
config = confuse.Configuration("Bme680", read=False)


def get_constant(param_name, typ):
    constant = config[param_name].get(typ)
    try:
        return getattr(bme680.constants, constant)
    except AttributeError:
        logger.exception(f"Configuration value '{constant}' is not valid for parameter: '{param_name}'")
        raise


def write_top_gas(top_readings, file_path):
    logger.info("Writing top gas reading file.")
    with open(file_path, "w") as of:
        for reading in top_readings:
            of.write(f"{reading}\n")


def read_top_gas(file_path):
    try:
        with open(file_path, "r") as f:
            return [int(line) for line in f.readlines()]
    except IOError:
        logger.info("Top gas reading file does not exist. Initializing it.")
        return []
    except ValueError:
        logger.info("Top gas reading file corrupted. Re-initializing it.")
        return []


def burn_in(sensor):
    burn_in_time = config['burn_in_time'].get(int)
    start_time = time.time()
    curr_time = start_time
    while curr_time - start_time < burn_in_time:
        if sensor.get_sensor_data():# and sensor.data.heat_stable:
            gas = sensor.data.gas_resistance
            logger.info(f"burn in {gas:.2f} ({curr_time-start_time:.2f} / {burn_in_time})")
            time.sleep(1)
        curr_time = time.time()


def compute_air_quality(gas, hum, hum_perfect_air, hum_weight, gas_perfect_air):

    if gas > gas_perfect_air:
        gas_score = 1 - hum_weight
    else:
        gas_score = (1 - hum_weight) * (gas / gas_perfect_air)

    hum_offset = hum - hum_perfect_air

    if abs(hum_offset) < 3:
        hum_score = hum_weight
    else:
        if hum_offset > 0:
            hum_score = hum_weight * (100 - hum) / (100 - hum_perfect_air)
        else:
            hum_score = hum_weight * hum / hum_perfect_air

    percent_score = 100*(hum_score + gas_score)
    iaq_score = (100 - percent_score) * 5

    if iaq_score >= 301.:
        grade = "Hazardous"
    elif 201. <= iaq_score <= 300.:
        grade = "Very Unhealthy"
    elif 176. <= iaq_score <= 200.:
        grade = "Unhealthy"
    elif 151. <= iaq_score <= 175.:
        grade = "Unhealthy for Sensitive Groups"
    elif 51. <= iaq_score <= 150.:
        grade = "Moderate"
    elif 0. <= iaq_score <= 50.:
        grade = "Good"
    else:
        grade = "Error"
    return iaq_score, grade


def record_data(sensor):

    sampling_time = config['sampling_time'].get(int)
    humidity_baseline = config['humidity_baseline'].get(float)
    humidity_weight = config['humidity_weight'].get(float)
    top_gas_path = config["top_gas_reading_file"].as_filename()
    top_gas_reading_size = config["top_gas_reading_size"].get(int)
    log_telegraf = config["log_telegraf"].get() == "yes"

    top_gas_readings = read_top_gas(top_gas_path)
    heapq.heapify(top_gas_readings)
    min_top_gas = min(top_gas_readings) if len(top_gas_readings) > 0 else 0.
    mean_top_gas = mean(top_gas_readings) if len(top_gas_readings) > 0 else 0.

    while True:
        # read data
        if sensor.get_sensor_data():# and sensor.data.heat_stable:
            temp = sensor.data.temperature
            pres = sensor.data.pressure
            hum = sensor.data.humidity
            gas = sensor.data.gas_resistance
            if len(top_gas_readings) < top_gas_reading_size:
                heapq.heappush(top_gas_readings, gas)
                min_top_gas = min(top_gas_readings)
                mean_top_gas = mean(top_gas_readings)
            elif gas > min_top_gas:
                heapq.heappush(top_gas_readings, gas)
                heapq.heappop(top_gas_readings)
                min_top_gas = min(top_gas_readings)
                mean_top_gas = mean(top_gas_readings)
                write_top_gas(top_gas_readings, top_gas_path)

            # compute air quality
            logger.debug(f"top gas readings: {top_gas_readings}")
            logger.debug(f"mean top gas readings: {mean_top_gas}")
            air_quality, aiq = compute_air_quality(gas, hum, humidity_baseline, humidity_weight, mean_top_gas)
            logger.info(f"{temp:.2f} C, {pres:.2f} %RH , {hum:.2f} hPa, {gas:.2f} Ohms, air quality: {air_quality:.2f}"
                        f"({aiq})")
            if log_telegraf:
                logger_telegraf.info(f"weather temperature={temp:.4f},pressure={pres:.4f},humidity={hum:.4f},"
                                     f"gas={gas:.4f},air_quality={air_quality:.4f},aiq=\"{aiq}\"")
        time.sleep(sampling_time)


def parse_arguments():

    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', help='path to yaml configuration file', default=os.environ.get("BME680_CONFIG_FILE"))
    parser.add_argument('--humidity_oversample')
    parser.add_argument('--temperature_oversample')
    parser.add_argument('--pressure_oversample')
    parser.add_argument('--filter_oversample')
    parser.add_argument('--enable_gas_meas', type=str)
    parser.add_argument('--temp_offset', type=int)
    parser.add_argument('--gas_heater_temperature', type=int)
    parser.add_argument('--gas_heater_duration', type=int)
    parser.add_argument('--gas_heater_profile', type=int)
    parser.add_argument('--burn_in_time', type=int)
    parser.add_argument('--sampling_time', type=int)
    parser.add_argument('--humidity_baseline', type=float)
    parser.add_argument('--humidity_weight', type=float)
    parser.add_argument('--top_gas_reading_file')
    parser.add_argument('--top_gas_reading_size', type=int)
    parser.add_argument('--log_level')
    parser.add_argument('--log_telegraf', type=str, help='creates telegraf logs in stdout')
    args = parser.parse_args()
    if not args.config_file: 
      print("config_file not specified.")
      exit(parser.print_usage())
    return args
   

def check_args():
    config['sampling_time'].get(int)
    config['humidity_baseline'].get(float)
    config['humidity_weight'].get(float)
    config["top_gas_reading_file"].as_filename()
    config["top_gas_reading_size"].get(int)
    config["log_telegraf"].as_choice(["yes", "no"])
    config['enable_gas_meas'].as_choice(["yes", "no"]) 



def initialize_bme680():

    humidity_os = get_constant('humidity_oversample', str)
    temperature_os = get_constant('temperature_oversample', str)
    pressure_os = get_constant('pressure_oversample', str)
    filter_size = get_constant('filter_size', str)
    enable_gas_meas = bme680.constants.ENABLE_GAS_MEAS if config['enable_gas_meas'].get() == "yes"\
        else bme680.constants.DISABLE_GAS_MEAS
    temp_offset = config['temp_offset'].get(int)
    gas_heater_temperature = config['gas_heater_temperature'].get(int)
    gas_heater_duration = config['gas_heater_duration'].get(int)
    gas_heater_profile = config['gas_heater_profile'].get(int)

    sensor = bme680.BME680(bme680.constants.I2C_ADDR_PRIMARY)
    sensor.set_humidity_oversample(humidity_os)
    sensor.set_temperature_oversample(temperature_os)
    sensor.set_pressure_oversample(pressure_os)
    sensor.set_filter(filter_size)
    sensor.set_gas_status(enable_gas_meas)
    sensor.set_temp_offset(temp_offset)
    sensor.set_gas_heater_temperature(gas_heater_temperature)
    sensor.set_gas_heater_duration(gas_heater_duration)
    sensor.select_gas_heater_profile(gas_heater_profile)

    return sensor


def setup_loggers():
    log_level = config["log_level"].as_choice(["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"])

    logger.setLevel(getattr(logging, log_level))
    handler = logging.StreamHandler(sys.stderr)
    handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s", datefmt='%y-%m-%d %H:%M:%S'))
    logger.addHandler(handler)

    logger_telegraf.setLevel("INFO")
    handler_telegraf = logging.StreamHandler(sys.stdout)
    handler_telegraf.setFormatter(logging.Formatter("%(message)s"))
    logger_telegraf.addHandler(handler_telegraf)


def main():
    args = parse_arguments()
    config.set_file(args.config_file)
    config.set_args(args)
    check_args()
    setup_loggers()

    sensor = initialize_bme680()
    burn_in(sensor)
    record_data(sensor)


if __name__ == "__main__":
    # execute only if run as a script
    main()

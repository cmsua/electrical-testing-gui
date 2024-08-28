import time
import pyvisa

# Try and connect to the supply every X s.
def wait_for_power_supply(address: str, delay: int, data: object):
    rm = pyvisa.ResourceManager()
    while True:
        try:
            # Connect
            ps = rm.open_resource(address)
            ps.write_termination = "\n"
            ps.read_termination = "\n"

            # Turn Off            
            ps.write("OUTPut:TRACK 0")
            ps.write("OUTPut CH1,OFF")
            ps.write("OUTPut CH2,OFF")
            ps.write("OUTPut CH3,OFF")

            # Set Initial Values
            ps.write("CH1:VOLTage 1.5")
            ps.write("CH2:VOLTage 1.5")
            ps.write("CH1:CURRent 3.23")
            ps.write("CH2:CURRent 3.23")

            return ps
        except:
            pass

        time.sleep(delay)

def enable_power_supply(data):
    data["power_supply"].write("OUTPut CH1,ON")


def check_power(data):
    return {
        "lv_v": data["power_supply"].query("CH1:VOLTage?"),
        "lv_i": data["power_supply"].query("CH1:CURRent?")
    }

def disable_power_supply(data):
    data["power_supply"].write("OUTPut CH1,OFF")
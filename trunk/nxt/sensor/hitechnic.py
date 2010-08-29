# nxt.sensor.hitechnic module -- Classes to read HiTechnic sensors
# Copyright (C) 2006,2007  Douglas P Lau
# Copyright (C) 2009  Marcus Wanner, Paulo Vieira, rhn
# Copyright (C) 2010  rhn, Marcus Wanner, melducky, Samuel Leeman-Munk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

from .common import *
from .digital import BaseDigitalSensor
from .analog import BaseAnalogSensor

class CompassMode:
    MEASUREMENT = 0x00
    CALIBRATION = 0x43
    CALIBRATION_FAILED = 0x02


class Compass(BaseDigitalSensor):
    """Hitechnic compass sensor."""

    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'heading': (0x44, '<H'),
                        'mode': (0x41, 'B'),
    })

    def get_heading(self):
        """Returns heading from North in degrees."""
        return self.read_value('heading')[0]
    
    get_sample = get_heading

    def get_relative_heading(self,target=0):
        """This function is untested but should work.
        If it does work, please post a message to the mailing list
        or email marcusw@cox.net. If it doesn't work, please file
        an issue in the bug tracker.
        """
        rheading = self.get_sample()-target
        if rheading > 180:
            rheading -= 360
        elif rheading < -180:
            rheading += 360
        return rheading	
    
    #this deserves a little explanation:
    #if max > min, it's straightforward, but
    #if min > max, it switches the values of max and min
    #and returns true if heading is NOT between the new max and min
    def is_in_range(self,min,max):
        """This function is untested but should work.
        If it does work, please post a message to the mailing list
        or email marcusw@cox.net. If it doesn't work, please file
        an issue in the bug tracker.
        """
        reversed = False
        if min > max:
            (max,min) = (min,max)
            reversed = True
        heading = self.get_sample()
        in_range = (heading > min) and (heading < max)
        #an xor handles the reversal
        #a faster, more compact way of saying
        #if !reversed return in_range
        #if reversed return !in_range
        return bool(reversed) ^ bool(in_range) 

    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode):
         if mode != CompassMode.MEASUREMENT and \
                 mode != CompassMode.CALIBRATION:
             raise ValueError('Invalid mode specified: ' + str(mode))
         self.write_value('mode', (mode, ))
         
Compass.add_compatible_sensor(None, 'HiTechnc', 'Compass ') #Tested with version '\xfdV1.23  '
Compass.add_compatible_sensor(None, 'HITECHNC', 'Compass ') #Tested with version '\xfdV2.1   '


class Acceleration:
    def __init__(self, x, y, z):
        self.x, self.y, self.z =x, y, z

class Accelerometer(BaseDigitalSensor):
    'Object for Accelerometer sensors. Thanks to Paulo Vieira.'
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({'x_axis_high': (0x42, 'b'),
        'y_axis_high': (0x43, 'b'),
        'z_axis_high': (0x44, 'b'),
        'xyz_short': (0x42, '3b'),
        'all_data': (0x42, '3b3B')
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(Accelerometer, self).__init__(brick, port, check_compatible)

    def get_acceleration(self):
        """Returns the acceleration along x, y, z axes. Units are unknown to me.
        """
        xh, yh, zh, xl, yl, zl = self.read_value('all_data')
        x = xh << 2 + xl
        y = yh << 2 + yl
        z = zh << 2 + yl
        return Acceleration(x, y, z)
    
    get_sample = get_acceleration

Accelerometer.add_compatible_sensor(None, 'HiTechnc', 'Accel.  ')
Accelerometer.add_compatible_sensor(None, 'HITECHNC', 'Accel.  ') #Tested with version '\xfdV1.1   '


class IRReceiverSpeeds:
    def __init__(self, m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B):
        self.m1A, self.m1B, self.m2A, self.m2B, self.m3A, self.m3B, self.m4A, self.m4B = m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B
        self.channel_1 = (m1A, m1B)
        self.channel_2 = (m2A, m2B)
        self.channel_3 = (m3A, m3B)
        self.channel_4 = (m4A, m4B)

class IRReceiver(BaseDigitalSensor):
    """Object for HiTechnic IRReceiver sensors for use with LEGO Power Functions IR
Remotes. Coded to HiTechnic's specs for the sensor but not tested. Please report
whether this worked for you or not!
    """
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'm1A': (0x42, 'b'),
        'm1B': (0x43, 'b'),
        'm2A': (0x44, 'b'),
        'm2B': (0x45, 'b'),
        'm3A': (0x46, 'b'),
        'm3B': (0x47, 'b'),
        'm4A': (0x48, 'b'),
        'm4B': (0x49, 'b'),
        'all_data': (0x42, '8b')
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(IRReceiver, self).__init__(brick, port, check_compatible)

    def get_speeds(self):
        """Returns the motor speeds for motors A and B on channels 1-4.
Values are -128, -100, -86, -72, -58, -44, -30, -16, 0, 16, 30, 44, 58, 72, 86
and 100. -128 specifies motor brake mode. Note that no motors are actually
being controlled here!
        """
        m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B = self.read_value('all_data')
        return IRReceiverSpeeds(m1A, m1B, m2A, m2B, m3A, m3B, m4A, m4B)
    
    get_sample = get_speeds

IRReceiver.add_compatible_sensor(None, 'HiTechnc', 'IRRecv  ')
IRReceiver.add_compatible_sensor(None, 'HITECHNC', 'IRRecv  ')


class IRSeekerDSPMode:
    #Modes for modulated (AC) data.
    AC_DSP_1200Hz = 0x00
    AC_DSP_600Hz = 0x01

class IRSeekerDCData:
    def __init__(self, x, y, z):
        self.direction, self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4, self.sensor_5, self.sensor_mean = direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean

class IRSeekerACData:
    def __init__(self, x, y, z):
        self.direction, self.sensor_1, self.sensor_2, self.sensor_3, self.sensor_4, self.sensor_5 = direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5

class IRSeekerv2(BaseDigitalSensor):
    """Object for HiTechnic IRSeeker sensors. Coded to HiTechnic's specs for the sensor
but not tested. Please report whether this worked for you or not!
    """
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'mode': (0x41, 'b'),
        'DC_direction': (0x42, 'b'),
        'DC_sensor_1': (0x43, 'b'),
        'DC_sensor_2': (0x44, 'b'),
        'DC_sensor_3': (0x45, 'b'),
        'DC_sensor_4': (0x46, 'b'),
        'DC_sensor_5': (0x47, 'b'),
        'DC_sensor_mean': (0x48, 'b'),
        'all_DC': (0x42, '7b'),
        'AC_direction': (0x49, 'b'),
        'AC_sensor_1': (0x4A, 'b'),
        'AC_sensor_2': (0x4B, 'b'),
        'AC_sensor_3': (0x4C, 'b'),
        'AC_sensor_4': (0x4D, 'b'),
        'AC_sensor_5': (0x4E, 'b'),
        'all_AC': (0x49, '6b')
    })
    I2C_DEV = BaseDigitalSensor.I2C_DEV.copy()
    I2C_DEV = 0x10 #different from standard 0x02
    
    def __init__(self, brick, port, check_compatible=False):
        super(IRSeekerv2, self).__init__(brick, port, check_compatible)

    def get_dc_values(self):
        """Returns the unmodulated (DC) values.
        """
        direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean = self.read_value('all_DC')
        return IRSeekerDCData(direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5, sensor_mean)
    
    def get_ac_values(self):
        """Returns the modulated (AC) values. 600Hz and 1200Hz modes can be selected
between by using the set_dsp_mode() function.
        """
        direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5 = self.read_value('all_AC')
        return IRSeekerACData(direction, sensor_1, sensor_2, sensor_3, sensor_4, sensor_5)
    
    def get_dsp_mode(self):
        return self.read_value('mode')[0]
    
    def set_dsp_mode(self, mode):
        self.write_value('mode', (mode, ))
    
    get_sample = get_ac_values

IRSeekerv2.add_compatible_sensor(None, 'HiTechnc', 'NewIRDir')
IRSeekerv2.add_compatible_sensor(None, 'HITECHNC', 'NewIRDir')


class EOPD(BaseAnalogSensor):
    """Object for HiTechnic Electro-Optical Proximity Detection sensors. Coded to
HiTechnic's specs for the sensor but not tested. Please report whether this
worked for you or not!
    """
    def __init__(self, brick, port, illuminated=True):
        super(Light, self).__init__(brick, port)

    def set_range_long(self):
        self.set_input_mode(Type.LIGHT_ACTIVE, Mode.RAW)

    def set_range_short(self):
        self.set_input_mode(Type.LIGHT_INACTIVE, Mode.RAW)
    
    def get_raw_value(self):
        return 1023 - self.get_input_values().scaled_value
    
    def get_processed_value(self):
        return sqrt(self.get_raw_value() * 10)
    
    get_sample = get_processed_value


class ColorMode:
    ACTIVE = 0x00 #get measurements using get_active_color
    PASSIVE = 0x01 #get measurements using get_passive_color
    RAW = 0x03 #get measurements using get_passive_color
    BLACK_CALIBRATION = 0x42 #hold away from objects, results saved in EEPROM
    WHITE_CALIBRATION = 0x43 #hold in front of white surface, results saved in EEPROM
    LED_POWER_LOW = 0x4C #saved in EEPROM, must calibrate after using
    LED_POWER_HIGH = 0x48 #saved in EEPROM, must calibrate after using
    RANGE_NEAR = 0x4E #saved in EEPROM, only affects active mode
    RANGE_FAR = 0x46 #saved in EEPROM, only affects active mode, more susceptable to noise
    FREQ_50 = 0x35 #saved in EEPROM, use when local wall power is 50Hz
    FREQ_60 = 0x36 #saved in EEPROM, use when local wall power is 60Hz

class ActiveColor:
    def __init__(self, number, red, green, blue, white, index, normred, normgreen, normblue):
        self.number, self.red, self.green, self.blue, self.white, self.index, self.normred, self.normgreen, self.normblue = number, red, green, blue, white, index, normred, normgreen, normblue

class PassiveColor:
    #also holds raw mode data
    def __init__(self, red, green, blue, white):
        self.red, self.green, self.blue, self.white = red, green, blue, white

class Colorv2(BaseDigitalSensor):
    """Object for HiTechnic Color v2 Sensors. Coded to HiTechnic's specs for the sensor
but not tested. Please report whether this worked for you or not!"""
    I2C_ADDRESS = BaseDigitalSensor.I2C_ADDRESS.copy()
    I2C_ADDRESS.update({
        'mode': (0x41, 'B'),
        'number': (0x42, 'B'),
        'red': (0x43, 'B'),
        'green': (0x44, 'B'),
        'blue': (0x45, 'B'),
        'white': (0x46, 'B')
        'index': (0x47, 'B'),
        'normred': (0x48, 'B'),
        'normgreen': (0x49, 'B'),
        'normblue': (0x4A, 'B'),
        'all_data': (0x42, '9B'),
        'rawred': (0x42, '<H'),
        'rawgreen': (0x44, '<H'),
        'rawblue': (0x46, '<H'),
        'rawwhite': (0x48, '<H'),
        'all_raw_data': (0x42, '<4H')
    })
    
    def __init__(self, brick, port, check_compatible=False):
        super(Colorv2, self).__init__(brick, port, check_compatible)

    def get_active_color(self):
        """Returns color values when in active mode.
        """
        number, red, green, blue, white, index, normred, normgreen, normblue = self.read_value('all_data')
        return ActiveColor(number, red, green, blue, white, index, normred, normgreen, normblue)
    
    get_sample = get_active_color
    
    def get_passive_color(self):
        """Returns color values when in passive or raw mode.
        """
        red, green, blue, white = self.read_value('all_raw_data')
        return PassiveColor(red, green, blue, white)
    
    def get_mode(self):
        return self.read_value('mode')[0]
    
    def set_mode(self, mode)
        self.write_value('mode', (mode, ))

Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD')
Colorv2.add_compatible_sensor(None, 'HiTechnc', 'ColorPD ')
Colorv2.add_compatible_sensor(None, 'HITECHNC', 'ColorPD ')


class Gyro(BaseAnalogSensor):
    'Object for gyro sensors'
#This class is for the hitechnic gryo sensor. When the gryo is not
#moving there will be a constant offset that will change with 
#temperature and other ambient factors. The calibrate() function
#takes the currect value and uses it to offset subsequesnt ones.

    def __init__(self, brick, port):
        super(Gyro, self).__init__(brick, port)
        self.set_input_mode(Type.ANGLE, Mode.RAW)
        self.offset = 0
    
    def get_rotation_speed(self):
        return self.get_input_values().scaled_value - self.offset
    
    def set_zero(self, value):
        self.offset = value
    
    def calibrate(self):
        self.set_zero(self.get_rotation_speed())
    
    get_sample = get_rotation_speed
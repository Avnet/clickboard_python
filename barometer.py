#
# copyright (c) 2020, James Flynn
# SPDX-License-Identifier: MIT
#
# @file   barometer.py
# @brief  code for managing the ST LPS25HB sensor using python.  The LPS25HB sensor 
#         (https://www.st.com/resource/en/datasheet/lps25hb.pdf) provides both 
#         Barometer and Temperature readings.
#
# @author James Flynn
#
# @date   15-April-2020
#

import smbus
i2c = smbus.SMBus(1)  #using I2C devce 1

#Register addresses & constants used
device_address    = 0x5d
LPS25HB_WHO_AM_I  = 0xbd
ZERO_KELVIN       = -273.15


# --------------------------------------------------------------------------------
# write a byte to the specified register
#
def write_byte( address_reg , data ):
    global device_address
    i2c.write_byte_data(device_address, address_reg, data)

# --------------------------------------------------------------------------------
# read a byte of data from the specified register
#
def read_byte(address_reg):
    global device_address
    tmp = i2c.read_byte_data(device_address,address_reg)
    return tmp

# --------------------------------------------------------------------------------
# initialize the LPS25HB to active mode, operating at 12.5 Hz (both Pressure & Temperature)
#
def init():
    write_byte( 0x20, (read_byte(0x20)|0xb0))

# --------------------------------------------------------------------------------
# @brief    barometer_who_am_i returns the LPS25HB identification
#
# @returns  the SLPS25HB identification value
#
def who_am_i():
    return read_byte(0x0f)

# --------------------------------------------------------------------------------
# @brief    __temp is a function that is used internally when reading the 
#           temperature values.
#
# @returns  returns the temperature in Celsius. If an error occurs, a value representing
#           zero degrees kelvin (-273.15) is returned because it is impossible to achieve
#
def __temp():
    t = ZERO_KELVIN # degrees Celsius, physically impossible-to-reach temperature of zero kelvin

    if( (read_byte(0x27) & 0x01) != 0 ):
        l  = read_byte(0x2b) & 0xff
        h  = read_byte(0x2c) & 0xff
        t = ((h*255) + l) - (1<<16) 
        t = 42.5 + (t/480.0)
    return t

# --------------------------------------------------------------------------------
# @brief    barometer_get_tempC returns the LPS25HB temperature reading
#
def get_tempC():
    return __temp()

# --------------------------------------------------------------------------------
# @brief    barometer_get_tempF returns the LPS25HB temperature reading in fahrenheit
#
def get_tempF():
    return (__temp() * 1.8+32)

# --------------------------------------------------------------------------------
# @brief    barometer_get_pressure returns the LPS25HB atomspheric pressure reading
#
# @param    __pbar  a pointer to a BAROMETER struction
# @returns  float.
#
def get_pressure(): #in mbar
    press = -1
    if (read_byte(0x27) & 0x02) != 0:
        b1 = read_byte(0x28) & 0xff
        b2 = read_byte(0x29) & 0xff
        b3 = read_byte(0x2a) & 0xff
        press = ((b3*65535) + (b2*255) + b1) / 4096.0
    return press



# --------------------------------------------------------------------------------
# Compile without -O or -OO to run this test as a standalone routine to verify
# it is working correctly
#
if __debug__:
    init()
    print "WHO AM I = "+hex(who_am_i())
    t = ZERO_KELVIN
    while t == ZERO_KELVIN:
        t=get_tempC()
    print "Temp = %.2f C" % t
    
    t = ZERO_KELVIN*1.8+32
    while t == (ZERO_KELVIN * 1.8+32):
        t=get_tempF()
    print "Temp = %.2f F" % t
    
    print "Pressure = %.2f" % get_pressure()


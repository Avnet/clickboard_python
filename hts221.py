#
# copyright (c) 2018, James Flynn
# SPDX-License-Identifier: MIT
#
# @file   hts221.py
# @brief  code for managing an ST HTS221 sensor. 
#
# @author James Flynn
#
# @date   15-April-2020
#

import smbus
i2c = smbus.SMBus(1)  #using I2C devce 1

#Register addresses
CALIB_START       = 0x30
CALIB_END         = 0x3F

device_address    = 0x5f
who_am_i_reg      = 0x0f
I_AM_HTS221       = 0xbc  

CTRL_REG1         = 0x20
POWER_UP          = 0x80
BDU_SET           = 0x4
ODR0_SET          = 0x1   

CTRL_REG2         = 0x21
CTRL_REG3         = 0x22
REG_DEFAULT       = 0x00

STATUS_REG        = 0x27
TEMPERATURE_READY = 0x1
HUMIDITY_READY    = 0x2

HUMIDITY_L_REG    = 0x28
HUMIDITY_H_REG    = 0x29
TEMP_L_REG        = 0x2A
TEMP_H_REG        = 0x2B

# calibration data is saved in the following variables...
h0_rH             = 0
h1_rH             = 0
T0_degC           = 0
T1_degC           = 0
H0_T0             = 0
H1_T0             = 0
T0_OUT            = 0
T1_OUT            = 0

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
#    Initialize the hts221.
#
def init():
    id = read_byte(who_am_i_reg)

    if id != I_AM_HTS221:
        print "Error: unable to read ID register (" + id + ")"
    else:
        print "HTS221 initialized"

# --------------------------------------------------------------------------------
#    hts221_powerdown powers down the HTS221 
#
def powerdown():
    write_byte(CTRL_REG1, (read_byte(CTRL_REG1) & ~POWER_UP))

# --------------------------------------------------------------------------------
#    hts221_powerup the HTS221 
#
def activate():
    write_byte(CTRL_REG1, (read_byte(CTRL_REG1) | POWER_UP | ODR0_SET))
    calibrate()


# --------------------------------------------------------------------------------
#    calibrate  a function that performs the specified HTS221
#           calibration procedure to obtain accurate measurments. This function 
#           is only used internally.
#
def calibrate():
    global h0_rH, h1_rH, T0_degC, T1_degC
    global H0_T0, H1_T0, T0_OUT, T1_OUT

    h0_rH = read_byte(0x30)
    h1_rH = read_byte(0x31)
    T0_degC = read_byte(0x32)
    T1_degC = read_byte(0x33)

    data = read_byte(0x35)
    T0_degC = ((data&0x0003)<<8) | (T0_degC & 0x00ff)
    T1_degC = ((data&0x000C)<<6) | (T1_degC & 0x00ff)

    H0_T0 = (read_byte(0x36)&0xff) | (read_byte(0x37)<<8)
    H1_T0 = (read_byte(0x3a)&0xff) | (read_byte(0x3b)<<8)
    T0_OUT = (read_byte(0x3c)&0xff) | (read_byte(0x3d)<<8)
    T1_OUT = (read_byte(0x3e)&0xff) | (read_byte(0x3f)<<8)
        


# --------------------------------------------------------------------------------
#    hts221_bduActivate enabled Block Data Update. See 'H' file for description
#
def bduActivate():
    write_byte(CTRL_REG1, (read_byte(CTRL_REG1) | BDU_SET))

# --------------------------------------------------------------------------------
#    hts221_bduDeactivate disables Block Data Update. See 'H' file for description
#
def bduDeactivate():
    write_byte(CTRL_REG1, (read_byte(CTRL_REG1) & ~BDU_SET))

# --------------------------------------------------------------------------------
#    hts221_readHumidity returns the HTS221 humidity reading
#
def readHumidity():
    global h1_rH, h0_rH, H0_T0, H1_T0

    status = 0
    while (status & HUMIDITY_READY) == 0:
        status = read_byte(STATUS_REG)

    h_out = (read_byte(HUMIDITY_H_REG)<<8) | read_byte(HUMIDITY_L_REG)

    # Decode Humidity with x2 multiple removed
    h_tmp = (h1_rH - h0_rH)/2.0          

    # Calculate humidity in decimal of grade centigrades i.e. 15.0 = 150.
    humid  = ((h_out-H0_T0) * h_tmp) / (H1_T0 - H0_T0)
    h_tmp   = h0_rH / 2.0                         # remove x2 multiple
    humid += h_tmp                                # provide signed % measurement unit
    return humid

# --------------------------------------------------------------------------------
#    hts221_readTemperature returns the HTS221 temperature reading
#
def readTemperature():
    global T1_degC, T0_degC, T0_OUT, T1_OUT

    status = 0
    while (status & TEMPERATURE_READY) == 0:
        status = read_byte(STATUS_REG)

    t_out = (read_byte(TEMP_H_REG)<<8) | read_byte(TEMP_L_REG)

    # Decode Temperature with x8 multiplier removed
    deg    = (T1_degC - T0_degC)/8.0 

    # Calculate Temperature in decimal of grade centigrades i.e. 15.0 = 150.

    temp = ((t_out - T0_OUT) * deg) / (T1_OUT - T0_OUT)
    deg   = T0_degC / 8.0
    temp += deg  # signed celsius measurement unit

    return temp


# --------------------------------------------------------------------------------
# Compile with -O or -OO to run this test as a standalone routine to verify
# it is working correctly
#
if __debug__:
    init()
    activate()

    t = readTemperature()  #( *(9/5))+32
    h = readHumidity()
    print "Temp = %.1f C." %t
    print "Temp = %.1f F." %((t*1.8)+32)
    print "Humidity = %.1f%%" %h


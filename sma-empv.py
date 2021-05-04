#!/usr/bin/python3
"""
*
*  ----------------------------------------------------------------------------
*  Set of functions to decode the udp telegram messages sent out by the 
*  SMA Energy Meter on port 9522 of the multicast group 239.12.255.254
* 
*
*  Documentation of the protocol is unfortunately only available in German. It 
*  can be downloaded from:
*      https://github.com/ufankhau/sma-empv/documentation/SMA-EM_GE.pdf
*
*  The following code is inspired by the work of david-m-m and
*  datenschuft (https://github.com/datenschuft/SMA-EM)
*
*  2021-May-03
*
*  ----------------------------------------------------------------------------
*/
"""

#  load necessary libraries
import socket
import struct
import binascii
import sdnotify
from time import time, sleep, localtime, strftime

script_version = "0.2.1"
script_name = 'sma-empv.py'
script_info = '{} v{}'.format(script_name, script_version)
project_name = 'Energy Monitor for PV Installation with SMA Inverter and Energy Meter'
project_url = 'https://github.com/ufankhau/sma-empv'



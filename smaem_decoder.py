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
*  The core of the following code is taken from the work of david-m-m and
*  datenschuft (https://github.com/datenschuft/SMA-EM)
*
*  2021-May-02
*
*  ----------------------------------------------------------------------------
*/
"""

#  map of all SMA-EM measurement channels in the sma_index dictionary
#
#  <index>:(<smaem_name>,<unit_actual_value>,<unit_counter_value>)
sma_index = {
	# totals
	1:('P_CONS','W','kWh'),
	2:('P_SUP','W','kWh'),
	3:('S_CONS','VA','kVAh'),
	4:('S_SUP','VA','kVAh'),
	9:('Q_CONS','VAr','kVArh'),
	10:('Q_SUP','VAr','kVArh'),
	13:('COSPHI',''),
	14:('FREQ','Hz'),		# firmware 2.xxxx and higher 
	# phase 1
	21:('P1_CONS','W','kWh'),
	22:('P1_SUP','W','kWh'),
	23:('S1_CONS','VA','kVAh'),
	24:('S1_SUP','VA','kVAh'),
	29:('Q1_CONS','VAr','kVArh'),
	30:('Q1_SUP','VAr','kVArh'),
	31:('I1','A'),
	32:('U1','V'),
	33:('COSPHI1',''),
	# phase 2
	41:('P2_CONS','W','kWh'),
	42:('P2_SUP','W','kWh'),
	43:('S2_CONS','VA','kVAh'),
	44:('S2_SUP','VA','kVAh'),
	49:('Q2_CONS','VAr','kVArh'),
	50:('Q2_SUP','VAr','kVArh'),
	51:('I2','A'),
	52:('U2','V'),
	53:('COSPHI2',''),
	# phase 3
	61:('P3_CONS','W','kWh'),
	62:('P3_SUP','W','kWh'),
	63:('S3_CONS','VA','kVAh'),
	64:('S3_SUP','VA','kVAh'),
	69:('Q3_CONS','VAr','kVArh'),
	70:('Q3_SUP','VAr','kVArh'),
	71:('I3','A'),
	72:('U3','V'),
	73:('COSPHI3',''),
	# other
	0:('speedwire-version','')
}


"""
*  SMA sends their data ("value" or "counter") in the following units
*
*  power in			  0.1 W
*  energy in			1 Ws
*  current in			1 mA
*  voltage in			1 mV
*  frequency in		0.001 Hz
*  power factor in	0.001 of cos(phi)
*
*  This results in the following dictionary "sma_scale" to get to the units
*  specified in the "sma_index" dictionary
*/
"""
sma_scale = {
	'W':			10,
	'VA':			10,
	'VAR':			10,
	'kWh':	   3600000,
	'kVAh':	   3600000,
	'kVAhr':   3600000,
	'A':		  1000,
	'V':		  1000,
	'Hz':		  1000,
	'':			  1000
}


"""
*  Structure of the OBIS Identifier (4 Byte)
*
*  |----------|----------|----------|----------|
*  | BYTE 0   | BYTE 1   | BYTE 2   | BYTE 3   |
*  | Channel  | Index    | Type     | Tarif    |
*  |----------|----------|----------|----------|
*  
*  Channel: following standard, range 128 ... 199 reserved for supplier specific
*  			use, e.g. code 144 used by SMA for sending software version
*  Index:   according to above directory "sma_index"
*  Type:    type of measurement, 2 types are in use, "actual" value and "counter"
*  Tarif:   not used (always zero)
*/
"""
def decode_OBIS(obis):
	obis_channel = obis[0]
	obis_index = obis[1]
	obis_type = obis[2]
	if obis_type==4:
    	datatype='actual'
	elif obis_type==8:
		datatype='counter'
	elif raw_type==0 and obis_channel==144:
		datatype='version'
	else:
		datatype='unknown'
    	print_line('* OBIS: unknown datatype: obis_index: {} datatype: {} obis_type: {}'.format(obis_index,datatype,obis_type), debug=True)
  return (obis_index,datatype)


def decode_speedwire(datagram):
  emparts={}
  # process data only of SMA header is present
  if datagram[0:3]==b'SMA':
    # datagram length
    datalength=int.from_bytes(datagram[12:14],byteorder='big')+16
    #print('data lenght: {}'.format(datalength))
    # serial number
    emID=int.from_bytes(datagram[20:24],byteorder='big')
    #print('seral: {}'.format(emID))
    emparts['serial']=emID
    # timestamp
    timestamp=int.from_bytes(datagram[24:28],byteorder='big')
    #print('timestamp: {}'.format(timestamp))
    emparts['timestamp']=timestamp
    # decode OBIS data blocks
    # start with header
    position=28
    while position<datalength:
      # decode header
      #print('pos: {}'.format(position))
      (measurement,datatype)=decode_OBIS(datagram[position:position+4])
      #print('measurement {} datatype: {}'.format(measurement,datatype))
      # decode values
      # actual values
      if datatype=='actual':
        value=int.from_bytes( datagram[position+4:position+8], byteorder='big' )
        position+=8
        if measurement in sma_channels.keys():
          emparts[sma_channels[measurement][0]]=value/sma_units[sma_channels[measurement][1]]
          emparts[sma_channels[measurement][0]+'unit']=sma_channels[measurement][1]
      # counter values
      elif datatype=='counter':
        value=int.from_bytes( datagram[position+4:position+12], byteorder='big' )
        position+=12
        if measurement in sma_channels.keys():
          emparts[sma_channels[measurement][0]+'counter']=value/sma_units[sma_channels[measurement][2]]
          emparts[sma_channels[measurement][0]+'counterunit']=sma_channels[measurement][2]
      elif datatype=='version':
        value=datagram[position+4:position+8]
        if measurement in sma_channels.keys():
          bversion=(binascii.b2a_hex(value).decode("utf-8"))
          version=str(int(bversion[0:2],16))+"."+str(int(bversion[2:4],16))+"."+str(int(bversion[4:6],16))
          revision=str(chr(int(bversion[6:8])))
          #revision definitions
          if revision=="1":
              #S – Spezial Version
              version=version+".S"
          elif revision=="2":
              #A – Alpha (noch kein Feature Complete, Version für Verifizierung und Validierung)
              version=version+".A"
          elif revision=="3":
              #B – Beta (Feature Complete, Version für Verifizierung und Validierung)
              version=version+".B"
          elif revision=="4":
              #R – Release Candidate / Release (Version für Verifizierung, Validierung und Feldtest / öffentliche Version)
              version=version+".R"
          elif revision=="5":
              #E – Experimental Version (dient zur lokalen Verifizierung)
              version=version+".E"
          elif revision=="6":
              #N – Keine Revision
              version=version+".N"
          #adding versionnumber to compare versions
          version=version+"|"+str(bversion[0:2])+str(bversion[2:4])+str(bversion[4:6])
          emparts[sma_channels[measurement][0]]=version
        position+=8
      else:
        position+=8
  return emparts


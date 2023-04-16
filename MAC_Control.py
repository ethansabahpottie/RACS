#!/usr/bin/env python
#
# Very simple progrma to send/receive data from MAC5000/6000 Through Serial Port
#
#

import codecs
import os
import sys
import threading

import serial
from serial.tools.list_ports import comports

#pylint: disable=wrong-import-order,wrong-import-position
try:
    raw_input
except NameError:
    # pylint: disable=redefined-builtin,invalid-name
    raw_input = input   # in python3 it's "raw"
    unichr = chr
	
def ask_for_port():
	""" Show a list of ports and ask user to pick one """
	
	sys.stderr.write('\n--- Available ports:\n')
	ports = []
	for n, (port, desc, hwid) in enumerate(sorted(comports()),1):
		sys.stderr.write('--- {:2}: {:20} {!r}\n'.format(n, port, desc))
		ports.append(port)
	while True:
		port = raw_input('--- Enter port index or full name: ')
		try:
			index = int(port) - 1
			if not 0 <= index < len(ports):
				sys.stderr.write('---Invalid index!\n')
				continue
		except ValueError:
			pass
		else:
			port = ports[index]
		return port
	
class MacControl(object):
	""" Simple program to send/receive data from MAC5000/6000 Serial Port """
	
	def __init__(self, serial_instance, echo=False, eol='crlf', filters=()):
		self.serial = serial_instance
		self.echo = echo
		self.raw = False
		self.input_encoding = 'UTF-8'
		self.output_encoding = 'UTF-8'
		self.eol = eol
		self.filters = filters
		self.exit_character = unichr(0x1d)
		self.menu_character = unichr(0x14)
		self.alive = None
		self._reader_alive = None
		self.receiver_thread = None
		self.rx_decoder = None
		self.tx_decoder = None
		
	def close(self):
		self.serial.close()
		
	def sender(self,cmd):
		"""Send command to controller and get response"""
		try:
			rcd=''
			prev='0 1 0 1 0 1 0 1 1 1'
			out=''
			self.serial.write(cmd)
			#sys.stderr.write('---sender:tx   {}\n'.format(cmd))
			while True:
				data=self.serial.read(1)
				if data:
					out+='{:c}'.format(data[0])
					if prev == out:
						sys.stderr.write(out)
						return out
				else:
					#sys.stderr.write('---sender:rx   {}\n'.format(out))
					return out
				prev=out
			return out
		except serial.SerialException:
			self.alive = False
			self.console.cancel()
			raise
		
	def checkbusy(self):
		"""Check busy status of controller"""
		try:
			command='status\r'
			text=command.encode("utf-8")
			rcd=self.sender(text)
			#sys.stderr.write('---checkbusy:{}\n'.format(rcd))
			if rcd[0]=='N':
				#sys.stderr.write('        NOT BUSY\n')
				return False
			else:
				#sys.stderr.write('        BUSY\n')
				return True
		except serial.SerialException:
			self.alive = False	
			raise
			
	def getXposition(self):
		"""Check busy status of controller"""
		try:
			command='WHERE X\r'
			text=command.encode("utf-8")
			rcd=self.sender(text)
			#sys.stderr.write('---getXpos:{}\n'.format(rcd))
			if rcd:
				if rcd[3] != 'N':
					val=int(rcd[2:])
					#sys.stderr.write('---getXpos:{}\n'.format(val))
					return val
				else:
					val=-999999999999
					return val

		except serial.SerialException:
			self.alive = False	
			raise
			
	def getYposition(self):
		"""Check busy status of controller"""
		try:
			command='WHERE Y\r'
			text=command.encode("utf-8")
			rcd=self.sender(text)
			#sys.stderr.write('---getXpos:{}\n'.format(rcd))
			if rcd:
				if rcd[3] != 'N':
					val=int(rcd[2:])
					#sys.stderr.write('---getXpos:{}\n'.format(val))
					return val
				else:
					val=-999999999999
					return val

		except serial.SerialException:
			self.alive = False	
			raise

	def moveXtar(self,tar):
		"""Check busy status of controller"""
		try:
			command='MOVE X={}\r'.format(tar)
			text=command.encode("utf-8")
			rcd=self.sender(text)
			#sys.stderr.write('---getXpos:{}\n'.format(rcd))
			if rcd:
				if rcd[1] != 'N':
					return True
				else:
					return False

		except serial.SerialException:
			self.alive = False	
			raise

	def moveYtar(self,tar):
		"""Check busy status of controller"""
		try:
			command='MOVE Y={}\r'.format(tar)
			text=command.encode("utf-8")
			rcd=self.sender(text)
			#sys.stderr.write('---getYpos:{}\n'.format(rcd))
			if rcd:
				if rcd[1] != 'N':
					return True
				else:
					return False

		except serial.SerialException:
			self.alive = False	
			raise




	
def main(default_port=None, default_baudrate=9600, default_type=None, default_cmd=None, X_distance = 100000,Y_distance=100000):
	"""Command line tool, entry point"""
	import argparse

	
	parser = argparse.ArgumentParser(
		description='MacControl - A simple program to send commands to MAC5000/6000 and get return value')
		
	parser.add_argument('port',nargs='?',help='serial port name ("-" to show port list)',default=default_port)
	
	parser.add_argument(
		'baudrate',
		nargs='?',
		type=int,
		help='set baud rate, default:%(dfault)s',
		default=default_baudrate)
		
	parser.add_argument(
		'cmd',
		nargs='?',
		help='command to send to mac',
		default='VER')
		
	args = parser.parse_args()
	sys.stderr.write('---Hello')
	while True:
		# no port given on command line -> ask user now
		if args.port is None or args.port =='-':
			try:
				args.port = ask_for_port()
			except KeyboardInterrupt:
				sys.stderr.write('\n')
				parser.error('user aborted and port is not given')
			else:
				if not args.port:
					parser.error('port is not given')
		
		try:
			serial_instance = serial.serial_for_url(
				args.port,
				args.baudrate,
				parity='N',
				rtscts=0,
				xonxoff=0,
				timeout=.25,
				do_not_open=True)
				
			if not hasattr(serial_instance, 'cancel_read'):
				#enable timeout for alive flag polling
				serial_instance.timeout = .25
				
			serial_instance.open()
			
			
			
		except serial.SerialException as e:
			sys.stderr.write('could not open port {!r}: {}\n'.format(args.port,e))
			sys.exit(1)
		else:
			break
	X_distance = X_distance
	Y_distance = Y_distance
	maccontrol = MacControl(serial_instance)
	sys.stderr.write('--- MacControl on {p.name} {p.baudrate},{p.bytesize},{p.parity},{p.stopbits} ---\n'.format(p=maccontrol.serial))
	
	sys.stderr.write('Busy Status:{}\n'.format(maccontrol.checkbusy()))
	

	sys.stderr.write('X Position :{}\n'.format(maccontrol.getXposition()))
	sys.stderr.write('Y Position :{}\n'.format(maccontrol.getYposition()))
	sys.stderr.write('Move X=100000:{}\n'.format(maccontrol.moveXtar(X_distance)))
	while maccontrol.checkbusy():
		sys.stderr.write('X Position :{}\n'.format(maccontrol.getXposition()))
	'''
	sys.stderr.write('Move X=0:{}\n'.format(maccontrol.moveXtar(0)))
	while maccontrol.checkbusy():
		sys.stderr.write('X Position :{}\n'.format(maccontrol.getXposition()))
	'''
	sys.stderr.write('Move Y=100000:{}\n'.format(maccontrol.moveYtar(Y_distance)))

	while maccontrol.checkbusy():
		sys.stderr.write('Y Position :{}\n'.format(maccontrol.getYposition()))
	'''
	sys.stderr.write('Move Y=0:{}\n'.format(maccontrol.moveYtar(0)))
	while maccontrol.checkbusy():
		sys.stderr.write('Y Position :{}\n'.format(maccontrol.getYposition()))
	'''	
			
	
	maccontrol.close()


	
			
# - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
if __name__ == '__main__':
    main()
			
		
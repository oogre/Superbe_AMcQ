#!/usr/bin/python

import time, subprocess, getopt, sys

def remapValue( value, in_min, in_max, out_min, out_max ):
	return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

def fade(t, alpha_origin, alpha_dest):
	t0 = int(round(time.time() * 1000));
	tMax = t0 + t;
	while int(round(time.time() * 1000)) < tMax :
		deltaT = int(round(time.time() * 1000)) - t0;
		alpha = remapValue( deltaT, 0, t, alpha_origin, alpha_dest);
		subprocess.call(["./dbuscontrol.sh", "setalpha", str(alpha)]);
		subprocess.call(["./dbuscontrol.sh", "volume", str(alpha / 255.0)]);
		#time.sleep (10.0 / 1000.0);
	subprocess.call(["./dbuscontrol.sh", "setalpha", str(alpha_dest)]);
	subprocess.call(["./dbuscontrol.sh", "volume", str(max(0, 00.1, alpha_dest / 255.0))]);

def main(argv):
	print argv
	try:
		opts, args = getopt.getopt(argv,"hi:o:",["fadeIn=","fadeOut="])
	except getopt.GetoptError:
		print 'omxcontroller.py -i <fadeIn> -o <fadeOut>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'test.py -i <fadeIn> -o <fadeOut>'
			sys.exit()
		elif opt in ("-i", "--fadeIn"):
			fade(int(arg), 0, 255);
		elif opt in ("-o", "--fadeOut"):
			fade(int(arg), 255, 0);

main(sys.argv[1:])
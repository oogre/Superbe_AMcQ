#!/usr/bin/python
import ConfigParser,subprocess, getopt, sys, fadecontroler, time, os, RPi.GPIO as GPIO;

config = ConfigParser.ConfigParser()
config.readfp(open('./configuration.cfg'))

# path configuration
ROOT = config.get("GENERAL", "rootDir");
DEBUG = config.get("GENERAL", "debug") == "True";
SCRIPTS = str(ROOT + "scripts/")
DBUSCONTROL = str(SCRIPTS + "dbuscontrol.sh");
# GPIO configuration
PIN_A = config.get("GPIO", "PIN_A")
PIN_B = config.get("GPIO", "PIN_B")
# video configuration
videoFileStandBy = config.get("VIDEO", "standby");
videoFileactive = config.get("VIDEO", "active");
fadeIn = int(config.get("VIDEO", "fadeIn"));
fadeOut = int(config.get("VIDEO", "fadeOut"));
soundMin = config.get("VIDEO", "soundMin");
soundMax = config.get("VIDEO", "soundMax");
frameInterval = 1000.0 / int(config.get("VIDEO", "frameRate"));
# END configuration 

# REFERENCE TO VIDEO
curVideo = False
standbyVideo = False
activeVideo = False

# VIDEO CLASS DEFINITION
class Video:
	
	def __init__(self, type, path):
		if os.path.isfile(path) is False : 
			raise ValueError("Video file doesn't exist", path, type)
		self.path = path
		explode = self.path.split("/")
		self.name = explode[len(explode)-1]
		self.isPlaying = False
	def playAV(self):
		global curVideo;
		
		if DEBUG :
			curVideo = self.name
		else : 
			# omxplayer -b -o local movie.mov
			curVideo = subprocess.Popen(["omxplayer", "-b", "-o", "local", "--alpha", "0", "--vol", "0.01", "--loop", "--no-osd", "--no-keys", self.path ], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE);
		time.sleep(1);
		self.isPlaying = True
		fade(fadeIn, 0, 255);
	def killAV(self):
		global curVideo;
		fade(fadeOut, 255, 0);
		if DEBUG is False :
			#curVideo.stdin.write('q');
			subprocess.call([DBUSCONTROL, "stop"]);
			curVideo = False
		self.isPlaying = False

balance = True
balance_ticked = False
def checkGpio():
	global balance
	global balance_ticked
	# return 0 if GPIO PIN_A & PIN_B ARE OFF
	# return 1 if GPIO PIN_A | PIN_B is ON
	if True :
		if ((int(round(time.time())) % 10 == 0) & balance_ticked) :
			balance = not balance
			balance_ticked = False
			print "Tick"

		if ((int(round(time.time())) % 10 != 0) & (balance_ticked is False)) : 
			balance_ticked = True
		
		if balance : 
			return 0
		else : 
			return 1
	else :
		if GPIO.input(PIN_A) | GPIO.input(PIN_B) :
			return 1;
		else : 
			return 0;

def standBy():
	if activeVideo.isPlaying :
		activeVideo.killAV()		
	if standbyVideo.isPlaying is False :
		standbyVideo.playAV()
    
def active():
	if standbyVideo.isPlaying :
		standbyVideo.killAV()		
	if activeVideo.isPlaying is False :
		activeVideo.playAV()
    
mapGpioToVideo = {
	0 : standBy,
	1 : active
};

# map function copy from Arduino LIB
def remapValue( value, in_min, in_max, out_min, out_max ):
	return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

# currently played video : fadeIn + turn volume on AND fadeOut + turn volume off  
def fade(t, alpha_origin, alpha_dest):
	t0 = int(round(time.time() * 1000));
	tMax = t0 + t;
	
	while int(round(time.time() * 1000)) < tMax :
		frameTime = int(round(time.time() * 1000))
		deltaT = int(round(time.time() * 1000)) - t0;
		alpha = remapValue( deltaT, 0, t, alpha_origin, alpha_dest);
		if DEBUG is False:
			subprocess.call([DBUSCONTROL, "setalpha", str(alpha)]);
			subprocess.call([DBUSCONTROL, "volume", str(alpha / 255.0)]);

		frameTime = int(round(time.time() * 1000)) - frameTime
		if frameTime < frameInterval : 
			time.sleep((frameInterval - frameTime) / 1000.0)

	if DEBUG:
		print curVideo + " is faded from " + str(alpha_origin) + " to " + str(alpha_dest) + " in " + str(t) + " seconds" 
	else : 
		subprocess.call([DBUSCONTROL, "setalpha", str(alpha_dest)]);
		subprocess.call([DBUSCONTROL, "volume", str(max(0, 00.1, alpha_dest / 255.0))]);



def main(argv):	
	global standbyVideo
	global activeVideo
	'''
		try:
			opts, args = getopt.getopt(argv,"ha:b:c3:",["video0=","video1=","video2="])
		except getopt.GetoptError:
			print 'videocontroller.py -a <video0> -b <video1> -c <video2>'
			sys.exit(2)

		for opt, arg in opts:
			if opt == '-h':
				print 'videocontroller.py -a <video0> -b <video1> -c <video2>'
				sys.exit()
			elif opt in ("-a", "--video0"):
				videoFiles[0] = arg;
				print "v0 : " + arg;
			elif opt in ("-b", "--video1"):
				videoFiles[1] = arg;
			elif opt in ("-c", "--video2"):
				videoFiles[2] = arg;
	'''

	if DEBUG :
		print "YOU ARE DEBUGGING : "
		print "	GPIO is disabled"
		print "	Videos are disabled"
	else : 
		GPIO.setup(PIN_A, GPIO.IN);
		GPIO.setup(PIN_B, GPIO.IN);
		
	standbyVideo = Video("standby", videoFileStandBy);
	activeVideo = Video("active", videoFileactive);

	while 1:
		mapGpioToVideo[checkGpio()]()
		time.sleep(0.1)

main(sys.argv[1:])

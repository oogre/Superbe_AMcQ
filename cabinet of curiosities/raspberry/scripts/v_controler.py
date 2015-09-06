#!/usr/bin/python
import ConfigParser,subprocess, getopt, sys, time, os;

config 		= ConfigParser.ConfigParser();
config.readfp(open('./configuration.cfg'));

# path configuration
ROOT 		= os.path.dirname(os.path.abspath(__file__)) + "/";
DBUSCONTROL = str(ROOT + "dbuscontrol.sh");

# GPIO configuration
PIN_A 		= config.get("GPIO", "PIN_A");
PIN_B 		= config.get("GPIO", "PIN_B");

# video configuration
fadeIn 				= int(config.get("VIDEO", "fadeIn"));
fadeOut 			= int(config.get("VIDEO", "fadeOut"));
soundMin 			= config.get("VIDEO", "soundMin");
soundMax 			= config.get("VIDEO", "soundMax");
frameInterval 		= 1.0 / int(config.get("VIDEO", "frameRate"));
videoFileActive 	= ROOT + config.get("VIDEO", "active");
videoFileStandBy	= ROOT + config.get("VIDEO", "standby");

# END configuration 

# DEBUG VAR
DEBUG 			= config.get("GENERAL", "debug") == "True";
balance 		= True;
balance_ticked 	= False;
balance_time 	= int(config.get("GENERAL", "balance_time"));
GPIO_FLAG 		= config.get("GENERAL", "GPIO_FLAG") == "True";

if GPIO_FLAG :
	import RPi.GPIO as GPIO;


# ALGO VAR
fade_dir 	= "in"# "out" "none";
video 		= False;
alpha		= 0;
alpha_inc	= 255.0 / fadeIn
alpha_dec	= 255.0 / fadeOut


def playAV(videoPath):
	global video;
	# omxplayer -b -o local movie.mov
	if DEBUG is False :
		try:
			subprocess.Popen(["omxplayer", "-b", "-o", "local", "--alpha", "0", "--vol", "0.01", "--loop", "--no-osd", "--no-keys", videoPath ], stdin=subprocess.PIPE, stdout=subprocess.PIPE);
		except Exception, e:
			print "omx ERROR";
		
	video = videoPath;
	time.sleep(1);

def killAV():
	global video
	if DEBUG is False :
		try:
			#subprocess.Popen([DBUSCONTROL, "stop"]);
			subprocess.call([DBUSCONTROL, "stop"]);
		except Exception, e:
			print "DBUSCONTROL STOP ERROR";
	video = False;

def checkGpio():
	global balance
	global balance_ticked
	# return 0 if GPIO PIN_A & PIN_B ARE OFF
	# return 1 if GPIO PIN_A | PIN_B is ON
	if GPIO_FLAG is False :
		if ((int(round(time.time())) % balance_time == 0) & balance_ticked) :
			balance = not balance
			balance_ticked = False
			#print "Tick"

		if ((int(round(time.time())) % balance_time != 0) & (balance_ticked is False)) : 
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

# map function copy from Arduino LIB
def remapValue( value, in_min, in_max, out_min, out_max ):
	return (value - in_min) * (out_max - out_min) / (in_max - in_min) + out_min;

def checkAVFile(path):
	if os.path.isfile(path) is False : 
		raise ValueError("Video file doesn't exist", path, type);
	return path;


def fade(alpha):
	alpha = min(max(alpha, 0), 255);
	if DEBUG is False:
		try:
			#subprocess.Popen([DBUSCONTROL, "setalpha", str(alpha)]);
			#subprocess.Popen([DBUSCONTROL, "volume", str(max(0.01, alpha / 255.0))]);
			subprocess.call([DBUSCONTROL, "setalpha", str(alpha)]);
			subprocess.call([DBUSCONTROL, "volume", str(max(0.01, alpha / 255.0))]);
		except Exception, e:
			playAV(video);
			print "DBUSCONTROL ALPHA ERROR";
		
	return alpha

def fader():
	global alpha;
	if (fade_dir == "out") & (alpha > 0):
		alpha -= alpha_dec;
		alpha = fade(alpha);
	elif (fade_dir == "in") & (alpha < 255):
		alpha += alpha_inc;
		alpha = fade(alpha);

def standBy():
	global fade_dir;
	global video;
	
	if False : 
		print " "
		print "video "+ str(video)
		print "videoFileStandBy "+ str(videoFileStandBy)
		print "alpha "+ str(alpha)
		print fade_dir


	if video == videoFileStandBy : 
		if alpha >= 255 : 	# STABLE STATE - PERFUME ARE IN/AWAY FROM PLACE SINCE A WHILE
			fade_dir = "none"
		elif alpha > 0 : 	# GO BACK TO STABLE STATE - RESET THE PERFUME AT ITS PLACE BEFORE VIDEO HAD CHANGE
			fade_dir = "in"
	else :
		if alpha <= 0 :		# PERFUME HAVE TAKEN AWAY FROM IT S PLACE - VIDEO IS FADED TO 0 SO CHANGE THE VIDEO
			killAV();
			playAV(videoFileStandBy);
			fade_dir = "in"
		else : 				# PERFUME HAVE TAKEN AWAY FROM IT S PLACE - VIDEO IS FADING TO 0
			fade_dir = "out"

	if fade_dir != "none":
		fader();

def active():
	global video;
	global fade_dir;

	if False : 
		print " "
		print "video "+ str(video)
		print "videoFileActive "+ str(videoFileActive)
		print "alpha "+ str(alpha)
		print fade_dir

	if video == videoFileActive : 
		if alpha >= 255 : 	# STABLE STATE - PERFUME ARE IN/AWAY FROM PLACE SINCE A WHILE
			fade_dir = "none"
		elif alpha > 0 : 	# GO BACK TO STABLE STATE - RESET THE PERFUME AT ITS PLACE BEFORE VIDEO HAD CHANGE
			fade_dir = "in"
	else :
		if alpha <= 0 :		# PERFUME HAVE TAKEN AWAY FROM IT S PLACE - VIDEO IS FADED TO 0 SO CHANGE THE VIDEO
			killAV();
			playAV(videoFileActive);
			fade_dir = "in"
		else : 				# PERFUME HAVE TAKEN AWAY FROM IT S PLACE - VIDEO IS FADING TO 0
			fade_dir = "out"

	if fade_dir != "none":
		fader();

mapGpioToVideo = {
	0 : standBy,
	1 : active
};

def main():	
	global standbyVideo
	global activeVideo

	if GPIO_FLAG is False :
		print "YOU ARE DEBUGGING : "
		print "	GPIO is disabled"
		print "	Videos are disabled"
	else : 
		GPIO.setup(PIN_A, GPIO.IN);
		GPIO.setup(PIN_B, GPIO.IN);
		
	checkAVFile(videoFileActive);
	checkAVFile(videoFileStandBy);

	while 1:
		mapGpioToVideo[checkGpio()]()
		time.sleep(frameInterval)

main();
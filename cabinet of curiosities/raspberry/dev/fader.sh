#!/bin/bash



for (( c=255 ; c>0 ; c-- ))
do
   ./dbuscontrol.sh setalpha "$c";
   echo "$c";
done

# Written by Jacques Boucher
# 25 April 2024
# Quick and dirty script to calculate time zone offset in an exFat directory entry
#
# input: a one byte hexidecimal value found at 0x16, 0x17, and 0x18 in the file directory entry.

hexvalue = input("Enter hex value: ")
timeZoneOffset = (((int(hexvalue,16)+64)%128)-64)*15
timeZoneOffsetHours = timeZoneOffset/60
print(f'The time zone ofsfset is {timeZoneOffset} minutes ({timeZoneOffsetHours} hours)')
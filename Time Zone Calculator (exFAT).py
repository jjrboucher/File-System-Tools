# Written by Jacques Boucher
# 25 April 2024
# Quick and dirty script to calculate time zone offset in an exFat directory entry
#
# input: a one byte hexidecimal value found at 0x16, 0x17, and 0x18 in the file directory entry.

hexValue = input("Enter hex value: ")
decimalValue = int(hexValue, 16)
timeZoneOffset = (((decimalValue + 64) % 128) - 64) * 15
timeZoneOffsetHours = timeZoneOffset / 60

print(f'Calculation is done by converting the hex value 0x{hexValue} to decimal (0d{decimalValue}.')
print(f'You then add 0d64 to that value giving you', decimalValue + 64)
print(f'Next, you use the modulo function as follows: ', decimalValue + 64, '% 128, giving you',
      (decimalValue + 64) % 128)
print(f'Next, substract 64 from', (decimalValue + 64) % 128,'giving you', ((decimalValue + 64) % 128)-64)
print(f'Finally, multiply that by 15 giving you you {timeZoneOffset}')
print(f'Divide {timeZoneOffset} minutes by 60 to get {timeZoneOffsetHours} hours.')
"""
Written by Jacques Boucher
23 April 2024
Script to parse NTFS data runs.

Must enter hex values with spaces.
E.g., 21 03 DA 0D 21 01 4A F2 31 05 65 F3 03
"""

red = f'\033[91m'
white = f'\033[00m'
green = f'\033[92m'


def nibbles(hex_value):
    return (hex_value >> 4) & 0xF, (hex_value & 0xF)


def parse_run_list(run_list, run, cluster):
    leftNibble, rightNibble = nibbles(int(run_list[0], 16))
    clusterElements = run_list[rightNibble:0:-1]
    startingExtentElements = run_list[leftNibble + rightNibble:rightNibble:-1]
    clusters = int(''.join(str(nc) for nc in clusterElements), 16)

    startingExtentString = ''.join(str(se) for se in startingExtentElements)
    startingExtent = int(startingExtentString, 16)

    if startingExtent & (1 << (len(startingExtentString) * 4 - 1)):
        startingExtent -= 1 << (len(startingExtentString) * 4)
    clusterNumber = cluster + startingExtent

    print(f'{red}Run List # {run} {white}(0x{run_list[0]})')
    print(f'cluster elements (0x{leftNibble}{green}{rightNibble}{white}): {green}{clusterElements}{white} = '
          f'{red}{clusters}{white} clusters')
    print(f'extent elements (0x{green}{leftNibble}{white}{rightNibble}): {green}{startingExtentElements}{white} '
          f'= starting extent {red}{startingExtent}{white}')
    print(f'Go to cluster number: {cluster} + {startingExtent} = {red}{clusterNumber}{white}')
    print(f'')
    nextDataRun = run_list[leftNibble + rightNibble + 1:]

    if len(nextDataRun) > 0 and nextDataRun[0] != '00':
        parse_run_list(nextDataRun, run + 1, clusterNumber)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    runList = input("Enter run list: ").split(" ")

    parse_run_list(runList, 1, 0)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

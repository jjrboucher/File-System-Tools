# Author: Jacques Boucher
# Email:  jjrboucher@gmail.com
# Date:  May 15, 2016
# Platform:  Python 2.7

import struct
import binascii

### Reference notes ###
# example of byte masking to get only certain bits:
# ref: http://stackoverflow.com/questions/9945720/python-extracting-bits-from-a-byte
# You can strip off the leading bit using a mask ANDed with a byte from file.
# That will leave you with the value of the remaining bits:
#mask =  0b01111111
#byte_from_file = 0b10101010
#value = mask & byte_from_file
#print bin(value)
#>> 0b101010
#print value
#>> 42

# example of bit shifting to combine part bits from two bytes:
# ref: http://stackoverflow.com/questions/19705638/how-to-concatenate-bits-in-python
# By shifting the first byte by 4 bits to the left (first<<4) you'll add 4 trailing zero bits. 
# Second part (second>>4) will shift out to the right 4 LSB bits of your second byte to discard 
# them, so only the 4 MSB bits will remain, then you can just bitwise OR both partial results 
# (| in python) to combine them.
#first = 0b01010101
#second = 0b11110000
#res = (first<<4) | (second>>4)
#print bin(res)

class fat12_16_boot_sector(object):
    '''
    Decode FAT 12/16 boot sector
    Parameter: First 48 bytes of FAT partition
    Return: where applicable, returns a two element tuple with raw hex and decoded decimal value
    '''
    # Decode FAT 12 and 16
    # offset (hex) | length (bytes) |  Description
    # 0x00              3             Address for boot-strapping code - little-endien
    # 0x03              8             OEM Name (mkdosfs) - big-endien
    # 0x0B              2             The number of bytes in each sector - little endien
    # 0x0D              1             The nunmber of sectors in each cluster
    # 0x0E              2             The number of reserved sectors - little endien
    # 0x10              1             The number of FATs
    # 0x11              2             The max number of files in Root Directory
    #                                     Each entry is 32 bytes in size
    #                                     Hence mutiply # by 32 for total bytes in Root Directory
    # 0x13              2             Total number of sectors (if two bytes not large enough, these
    #                                     bytes are zeroed and four bytes at 0x20 - 0x23 are used)
    # 0x15              1             No longer required.
    # 0x16              2             The number of sectors in each FAT  

    def __init__(self, data):
        self.data = data

    def boot_strapping_address(self):
        # bytes 0-2, little-endien
        return (binascii.hexlify(self.data[:3]), struct.unpack("<I", self.data[:3]+b'\x00')[0])  # only 3 bytes, so adding \x00 at the end to make it 4 bytes.  When flipped (LE), \x00 has no impact.

    def oem_name(self):
        # bytes 3-10 - big-endien
        return (binascii.hexlify(self.data[3:11]), self.data[3:11])  # oem name

    def bytes_per_sector(self):
        # bytes 11 & 12 - little-endien
        return (binascii.hexlify(self.data[11:13]), struct.unpack("<H", self.data[11:13])[0])  # number of bytes per sector

    def sectors_per_cluster(self):
        # byte 13
        return (binascii.hexlify(self.data[13]), struct.unpack("<B", self.data[13])[0])  # number of sectors per cluster

    def reserved_sectors(self):
        # bytes 14 & 15 - little-endien
        return (binascii.hexlify(self.data[14:16]), struct.unpack("<H", self.data[14:16])[0])  # number of reserved sectors

    def max_files_in_root_dir(self):
        return (binascii.hexlify(self.data[11:13]), struct.unpack("<H", self.data[11:13])[0])  # max files in root director

    def sectors_in_root_directory(self):
        return self.max_files_in_root_dir()[1]*32/512

    def total_number_sectors(self):
        tns = (binascii.hexlify(self.data[19:21]), struct.unpack("<H", self.data[19:21])[0])  # 2 byte value (will be 0 if not large enough and 4 bytes are needed)
        if tns[1] > 0:  # if not 0, correct value
            return tns
        else:  # if 0, means it needed 4 bytes to represent value
            return (binascii.hexlify(self.data[32:36]), struct.unpack("<L", self.data[32:36])[0])

    def sectors_per_fat(self):
        return (binascii.hexlify(self.data[22:24]), struct.unpack("<H", self.data[22:24])[0])

    def FAT1_start_sector(self):
        return self.reserved_sectors()[1]

    def FAT2_start_sector(self):
        return self.FAT1_start_sector() + self.sectors_per_fat()[1]

    def root_dir_start_sector(self):
        return self.FAT2_start_sector() + self.sectors_per_fat()[1]

    def data_start_sector(self):
        return self.root_dir_start_sector() + self.sectors_in_root_directory()

    def __str__(self):
        return  "\n| Boot Sector | Reserved Area | FAT 1 | FAT 2 | Root Directory | Data Area ->\n\n" + \
            "Boot Strapping Address: 0x" + self.boot_strapping_address()[0] + " LE = " + str(self.boot_strapping_address()[1]) + " decimal" + \
            "\nOEM name: 0x" + self.oem_name()[0] + " BE = " + self.oem_name()[1] + \
            "\nBytes per sector: 0x" + self.bytes_per_sector()[0] + " LE = " + str(self.bytes_per_sector()[1]) + " decimal" + \
            "\nSectors per cluster: 0x" + self.sectors_per_cluster()[0] + " LE = " + str(self.sectors_per_cluster()[1]) + " decimal" + \
            "\nReserved sectors: 0x" + self.reserved_sectors()[0] + " LE = " + str(self.reserved_sectors()[1]) + " decimal" + \
            "\nMaximum files in Root Directory: 0x" + self.max_files_in_root_dir()[0] + " LE = " + str(self.max_files_in_root_dir()[1]) + " decimal" + \
            "\nSectors in Root Director: " + str(self.sectors_in_root_directory()) + \
            "\nTotal number of Sectors: 0x" + self.total_number_sectors()[0] + " LE = " + str(self.total_number_sectors()[1]) + " decimal" + \
            "\nSectors per FAT table: 0x" + self.sectors_per_fat()[0] + " LE = " + str(self.sectors_per_fat()[1]) + " decimal" + \
            "\nBoot Sector is at sector 0.\nFAT1 Start Sector: " + str(self.FAT1_start_sector()) + \
            "\nFAT2 Start Sector: " + str(self.FAT2_start_sector()) + \
            "\nRoot Directory Start Sector: " + str(self.root_dir_start_sector()) + \
            "\nData Start Sector: " + str(self.data_start_sector())


class root_directory(object):
    '''
    Input: root directory of a FAT 12/16 partition
    Output: Only 32 byte chunks with file data
            This reduces the volume of data processed
    '''
    def __init__(self, data):
        self.data = data

    def files(self):
        file_entries=[]  # list to contain list of files in the root directory
        for pointer in range(0, len(self.data), 32):  # loop through each 32 byte block of data
            if struct.unpack(">Q", self.data[pointer:pointer + 8])[0] != 0:  # if the first 8 bytes not equal to 0, it's a valid entry
                file_entries.append(self.data[pointer:pointer + 32])  # append the 32 byte block to the list.
            else:
                break
        return file_entries  # return the list
   
             
class directory_entry(object):
    '''
    Input: 32 byte FAT 12/16 directory entry
    Methods:
        short_file_name - returns the short file name
        is_deleted - returns True or False
        
    '''
    
    # pass start sector for directory entry - var.root_dir_start_sector
    # each entry is 32 bytes
    # LFN may exist.  If so, 32 bytes preceding the short file name 32 bytes.
    # LE format
    # 0x0B attribute:
    #     0b0000 0001 Read Only
    #     0b0000 0010 Hidden File
    #     0b0000 0100 System File
    #     0b0000 1000 Volume Label
    #     0b0000 1111 Long File Name
    #     0b0001 0000 Directory
    #     0b0010 0000 Archive
    
    def __init__(self, record):
        self.record = record
        
    def short_file_name(self):
        # bytes 0-7 - file name
        # bytes 8-10 - extension
        return self.record[:8].strip() + '.' + self.record[8:11]
        
    def is_deleted(self):
        # byte 0 has a value of 229 if deleted file - 0xE5
        return (True if struct.unpack("<B", self.record[0])[0] == 229 else False)
 
    def is_readonly(self):
        # byte 11, applying mask to isolate first bit only
        return (True if (0b00000001 & struct.unpack("<B", self.record[11])[0]) == 1 else False)
          
    def is_hidden(self):
        # byte 11, applying mask to isolate second bit only
        return (True if (0b00000010 & struct.unpack("<B", self.record[11])[0]) == 2 else False)
        
    def is_system(self):
        # byte 11, applying mask to isolate third bit only
        return (True if (0b00000100 & struct.unpack("<B", self.record[11])[0]) == 4 else False)
        
    def is_volume(self):
        # byte 11, applying mask to isolate fourth bit only
        return (True if (0b00001000 & struct.unpack("<B", self.record[11])[0]) == 8 else False)
                
    def is_directory(self):
        # byte 11, applying mask to isolate first four bits, then check if equal to 1
        return (True if (0b11110000 & struct.unpack("<B", self.record[11])[0]) >> 4 == 1 else False)

    def is_archived(self):
        # byte 11, applying mask to isolate first four bits, then check if equal to 2
        return (True if (0b11110000 & struct.unpack("<B", self.record[11])[0]) >> 4 == 2 else False)      
        
    def is_long_filename(self):
        # byte 11 has a value of 0x0f if a long filename entry
        return (True if ord(self.record[11]) == 15 else False)

    def _decode_date(self, date_value):
        year = ((0b11111110 & (struct.unpack("<H", date_value)[0]>>8)) >> 1) + 1980
        month = (0b0000000111100000 & struct.unpack("<H", date_value)[0])>>5
        day = (0b0000000000011111 & (struct.unpack("<H", date_value)[0]))   
        return '{:04d}'.format(year) + '-' + '{:02d}'.format(month) + '-' + '{0:2d}'.format(day)
        
    def created_date(self):
        # bytes 16 & 17 - little-endien
        return self._decode_date(self.record[16:18])
        
    def access_date(self):
        # bytes 18 & 19 - little-endien
        return self._decode_date(self.record[18:20])
        
    def modified_date(self):
        # bytes 24 & 25 - little-endien
        return self._decode_date(self.record[24:26])
        
    def _decode_time(self, time_value):
        hours = ((0b1111100000000000 & struct.unpack("<H", time_value)[0])>>11)  # applies a mask to get the first five bits only and then bit-wise shift of 11
        minutes = ((0b0000011111100000 & struct.unpack("<H", time_value)[0])>>5) # applies a mask to get the next 6 bits only, and then bit-wise shift of 5
        seconds = (0b0000000000011111 & struct.unpack("<H", time_value)[0]) * 2  # applies a mask to get the last 5 bits only.
        return '{:02d}'.format(hours) + ':' + '{:02d}'.format(minutes) + ' hrs and ' + str(seconds) + ' or ' + str(seconds+1) + ' seconds'
        
    def created_time(self):
        # bytes 14 & 15 - litte-endien
        return self._decode_time(self.record[14:16])

    def modified_time(self):
        # bytes 22 & 23 - little-endien
        return self._decode_time(self.record[22:24])
        
    def file_size(self):
        # bytes 28 to 32 (end of a directory entry) - little endien
        return struct.unpack("<L", self.record[28:])[0]
        
    def first_cluster(self):
        # high order bytes at 20 & 21 (little-endien), low order bytes at 26 & 27 (little-endien)
        return struct.unpack(">L", self.record[21] + self.record[20] + self.record[27] + self.record[26])[0]
        
class data_run(object):
    '''
    INPUT:
    FAT table
    starting cluster of directory entry
    '''
    
    def __init__(self, table, start):
        self.table = table
        self.start = start
        
    def list(self):
        cluster_run = []  # list to store cluster run
        cluster_run.append(self.start) # append first cluster passed to the class
        current_cluster=self.start  # assign it as the current cluster
        next_cluster=struct.unpack("<H", self.table[current_cluster*2:current_cluster*2+2])[0]  #  grab the value at that location - pointer to next cluster
        while next_cluster != 65535:  # while not 0x00ff, means it is pointing to next sector, keep grabbing the next one in the run
            cluster_run.append(next_cluster)  # append the next cluster
            current_cluster = next_cluster  # make the next cluster above now the current cluster
            next_cluster=struct.unpack("<H", self.table[current_cluster*2:current_cluster*2+2])[0]  # carve out the bytes at the next cluster
        return cluster_run  # return the list with the cluster run

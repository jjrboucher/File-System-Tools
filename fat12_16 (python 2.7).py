from fat_fs_parser import *
import sys

f = open(sys.argv[1], 'rb')  # open file and read it as binary data
d=f.read(48)
fat = fat12_16_boot_sector(d)  # read in 48 bytes and assigns to to the variable "fat" of class fat12_16_boot_sector
print fat
print '\n'

f.seek(fat.root_dir_start_sector()*fat.bytes_per_sector()[1])  # seek to start of root directory
root_dir_data = root_directory(f.read(fat.bytes_per_sector()[1] * fat.sectors_in_root_directory())) # read root directory and assigned it to the variable root_dir_data of class "root_directory"

f.seek(fat.FAT1_start_sector() * fat.bytes_per_sector()[1])
fat_table=f.read(fat.sectors_per_fat()[1] * fat.bytes_per_sector()[1])


for files in root_dir_data.files():
    entry=directory_entry(files)
    if  not entry.is_long_filename():
        clusters=data_run(fat_table, entry.first_cluster()) # declare variable "cluster" as class data_run
        print 'Name: ' + entry.short_file_name()
        print 'Created date: ' + entry.created_date()
        print 'Created time: ' + entry.created_time()
        print 'Access date: ' + entry.access_date()
        print 'Modified date: ' + entry.modified_date()
        print 'Modified time: ' + entry.modified_time()
        print 'Directory: ' + str(entry.is_directory())
        print 'Read only: ' + str(entry.is_readonly())
        print 'Hidden: ' + str(entry.is_hidden())
        print 'System: ' + str(entry.is_system())
        print 'Volume: ' + str(entry.is_volume())
        print 'Archived: ' + str(entry.is_archived())
        print 'Deleted: ' + str(entry.is_deleted())
        if not entry.is_directory(): # if not a directory
            print 'Logical File size: ' + str(entry.file_size()) # print logical file size
            if not entry.is_deleted() and entry.file_size() > 0: # if not a deleted file and file size > 0
                print 'Cluster run:', clusters.list(), '\n' # print list of clusters
            else: # 
                if entry.file_size() == 0: 
                    print 'Cluster run: n/a (zero byte file)\n'
                else:
                   print 'Cluster run:  ' + str(entry.first_cluster()) + '\n'
        else:
            print 'Cluster run: ' + str(entry.first_cluster()) + '\n'

f.close()  # close the file
import sys
import time
import array as ar
import os

import source.telink_driver as td
import argparse

__version__ = "0.2 dev"

print("")
print("BDT Software Tool " + __version__)

td.driver_init()

parser = argparse.ArgumentParser(description='Telink_Tools_BDT.py v%s - Telink BLE Device Burn' % __version__)

parser.add_argument("-a", "--activate", action="count", default=0)
parser.add_argument("-e", "--erase", action="count", default=0)

parser.add_argument("-f", "--flash", help='Download an image to Flash, ex: -f filename')
# parser.add_argument('filename', help='Firmware image')



args = parser.parse_args()
args.filename = args.flash

if args.activate:
    print("Activating: ")
    if(td.activate() == True):
        print('\033[32m', "Activate OK!", '\033[0m', sep='')

if args.erase:

    if td.erase_init():
        print("TC32 EVK : Swire OK")

    print("Erasing: ")

    firmware_size = 2048 #524288/16

    bar_len = 50

    for i in range(0,firmware_size,16):
        td.erase_adr(adr = i)
        hex_value = hex(i * 0x100)
        # print("Flash Sector (4K) Erase at address: " + str(hex_value))
        firmware_addr = i

        percent = (int)(firmware_addr *100 / (firmware_size - 16))
        sys.stdout.write("\r" + str(percent) + "% [\033[3;91m{0}\033[0m{1}]".format("#"*(int)(percent*bar_len/100),"="*(bar_len-(int)(percent*bar_len/100)))+"".join("0x%05x" % int(firmware_addr*256)))
        sys.stdout.flush()
    print("")

def burn(args):
    #  Try to change Baud to 921600 
    print("Burn Firmware :"  + args.filename)

    fo = open(args.filename, "rb")
    firmware_addr = 0
    firmware_size = os.path.getsize(args.filename)

    if firmware_size > 0x80000:
        print("\033[3;31mFirmware Too BIG!\033[0m")
        fo.close()

    bar_len = 50

    td.download_init()

    print("Flashing: ")

    while True:

        if(firmware_addr % 4096 == 0):
            # print("foi")
            td.download_block_init(int(firmware_addr/256))

        data = fo.read(256)
        if len(data) < 1: break

        td.donwload_adr(data, int(firmware_addr/256))

        firmware_addr += len(data)

        percent = (int)(firmware_addr *100 / firmware_size)
        sys.stdout.write("\r" + str(percent) + "% [\033[3;32m{0}\033[0m{1}]".format("#"*(int)(percent*bar_len/100),"="*(bar_len-(int)(percent*bar_len/100)))+"".join("0x%05x" % int(firmware_addr)))
        sys.stdout.flush()

    td.download_end()

    # telink_reboot(_port)
    print("")
    fo.close()
    # _port.close()

if args.filename:
    burn(args)
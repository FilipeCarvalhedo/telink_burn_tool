import sys
import time
import array as ar
import os

import source.telink_driver as td

td.driver_init()

# if(td.activate() == True):
#         print("Activate OK!")


# if __name__ == "__main__":
#     


import argparse
parser = argparse.ArgumentParser()
parser.add_argument("-f", "--filename", help="Flash a file")

parser.add_argument("-e", "--erase", action="count", default=0)

parser.add_argument("-a", "--activate", action="count", default=0)

args = parser.parse_args()

if args.activate:
    if(td.activate() == True):
        print("Activate OK!")

if args.erase:
    td.erase()

def burn(args):
    #  Try to change Baud to 921600 
    print("\033[3;32mOK!\033[0m\r\nBurn Firmware :"  + args.filename)

    fo = open(args.filename, "rb")
    firmware_addr = 0
    firmware_size = os.path.getsize(args.filename)

    if firmware_size > 0x80000:
        print("\033[3;31mFirmware Too BIG!\033[0m")
        fo.close()

    bar_len = 50

    td.download_init()

    while True:

        if(firmware_addr % 4096 == 0):
            # print("foi")
            td.download_block_init(int(firmware_addr/256))

        data = fo.read(256)
        if len(data) < 1: break

        # if not td.download(_port, firmware_addr, data):
        #     print("\033[3;31mBurn firmware Fail!\033[0m")
        #     break

        # print("".join("%02x" % i for i in data))
        # print("".join("%02x" % i for i in firmware_addr))
        # print("".join("%02x" % firmware_addr))
        print("".join("%02x" % int(firmware_addr/256)))
        td.donwload_adr(data, int(firmware_addr/256))

        firmware_addr += len(data)

        percent = (int)(firmware_addr *100 / firmware_size)
        # sys.stdout.write("\r" + str(percent) + "% [\033[3;32m{0}\033[0m{1}]".format(">"*(int)(percent*bar_len/100),"="*(bar_len-(int)(percent*bar_len/100))))
        # sys.stdout.flush()

    td.download_end()

    # telink_reboot(_port)
    print("")
    fo.close()
    # _port.close()

if args.filename:
    print("flash turned on")
    burn(args)

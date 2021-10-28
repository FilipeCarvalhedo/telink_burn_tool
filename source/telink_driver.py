import usb.core
import usb.util
import sys
import time
import array as ar


def driver_init():

    # find our device
    global dev
    dev = usb.core.find(idVendor=0x248a, idProduct=0x5320)
    # was it found?
    if dev is None:
        raise ValueError('Device not found')
    # get an endpoint instance
    cfg = dev[0]
    intf = cfg[(0,0)]

    try:
        dev.detach_kernel_driver(0)
    except:
        time.sleep(0.001)

    alt = usb.util.find_descriptor(cfg, find_all=True, bInterfaceNumber=1)

    # dev.set_configuration(cfg)

    cfg = usb.util.find_descriptor(dev, bConfigurationValue=1)
    dev.set_configuration(cfg)

    ep = usb.util.find_descriptor(
        intf,
        # match the first OUT endpoint
        custom_match = \
        lambda e: \
            usb.util.endpoint_direction(e.bEndpointAddress) == \
            usb.util.ENDPOINT_OUT)


    usb.control.get_descriptor(dev, 256, 1, 0)
    usb.control.get_descriptor(dev, 256, 2, 0)

    global last_message
    last_message=ar.array('B', [0])

def send(wValue = 0x7c, data_or_wLength = 12):
    dev.ctrl_transfer(bmRequestType = 0x41, bRequest = 0x02, wValue = wValue, wIndex = 0, data_or_wLength = data_or_wLength)
    # time.sleep(0.003)

def receive(wValue = 0x7c, data_or_wLength = 12, timeOut = 5, reset = False, test_index = None, test_data = None, test_last = None):
    timeout_start = time.time() + timeOut
    
    global last_message

    # if reset:
    #     last_message = dev.ctrl_transfer(bmRequestType = 0xC1, bRequest = 0x02, wValue = wValue, wIndex = 0, data_or_wLength = data_or_wLength)
	
    while(True):
        a = dev.ctrl_transfer(bmRequestType = 0xC1, bRequest = 0x02, wValue = wValue, wIndex = 0, data_or_wLength = data_or_wLength)
        # print("".join("%02x" % i for i in a))

        if(time.time() > timeout_start):
            break

        if test_last:
            if(a != last_message):
                break

        if(test_data != None and test_index != None):
            # print("aqui")
            if(a[test_index] == test_data):
                break

        # time.sleep(0.003)

    if time.time() >= timeout_start and timeOut != 0:
        print("Errror: ")
        print("".join("%02x" % i for i in a))
        raise ValueError('Timeout') 

    last_message = a

    time.sleep(0.003)

    return a

def activate():

    global last_message

    msg1 = bytearray.fromhex("02 9f ff 50 50 50 50 50 50")
    msg2 = bytearray.fromhex("02 9f ff 4d 4d 4d 4d 4d 4d")
    msg3 = bytearray.fromhex("02 9f f8 7f 7f 7f 7f 7f 7f 00 00 00 01 00 00 c1")

    send(wValue = 0x9fff, data_or_wLength = msg1)
    result = receive(wValue = 0x9ff4, data_or_wLength = 12, test_last = True)
    # print("".join("%02x" % i for i in (result)))

    send(wValue = 0x9fff, data_or_wLength = msg2)
    result = receive(wValue = 0x9ff4, data_or_wLength = 12, test_last = True)
    # print("".join("%02x" % i for i in (result)))

    send(wValue = 0x9fff, data_or_wLength = msg1)
    result = receive(wValue = 0x9ff4, data_or_wLength = 12, test_last = True)
    # print("".join("%02x" % i for i in (result)))

    send(wValue = 0x9fff, data_or_wLength = msg2)
    result = receive(wValue = 0x9ff4, data_or_wLength = 12, test_last = True)
    # print("".join("%02x" % i for i in (result)))

    send(wValue = 0x9ff8, data_or_wLength = msg3)
    time.sleep(0.003)

    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 5, reset = True, test_index = 0, test_data = 0x55)
    # print("".join("%02x" % i for i in ()))

    if(result[0] == 0):
        return False

    return True

def erase_init():

    time.sleep(0.010)

    msg1  = bytearray.fromhex("02 9f ff 50 50 50 50 50 50")
    msg2  = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 00 00 00 01 00 00 07")

    ################

    send(wValue = 0x9fff, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))


    ################

    msg1 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 00 00 00 01 00 00 07")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    #################

    msg1 = bytearray.fromhex("02 9f f8 b2 b2 b2 b2 b2 b2 00 00 00 01 00 00 81")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    #################

    msg1  = bytearray.fromhex("02 a0 00 ab ab ab ab ab ab")
    msg2  = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))


    ################


    msg1 = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 01 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 5, reset = True, test_index = 0, test_data = 0xab)

    # print("".join("%02x" % i for i in (result)))

    #################

    msg1  = bytearray.fromhex("02 a0 00 05 05 05 05 05 05")
    msg2  = bytearray.fromhex("02 9f f8 02 02 02 02 02 02 06 00 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    #################

    msg1 = bytearray.fromhex("02 9f f8 02 02 02 02 02 02 06 00 00 01 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 5, reset = True, test_index = 0, test_data = 0x05)

    # print("".join("%02x" % i for i in (result)))

    ####################

    msg1  = bytearray.fromhex("02 a0 00 00 00 00 00 00 00")
    msg2  = bytearray.fromhex("02 9f f8 22 22 22 22 22 22 06 00 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))


    ################

    msg1  = bytearray.fromhex("02 a0 00 00 00 00 00 00 00")
    msg2  = bytearray.fromhex("02 9f f8 43 43 43 43 43 43 06 00 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))


    ################

    # Gravacao Dut fica aqui, nao sei se eh necessaria


    msg1 = bytearray.fromhex("02 a0 00 28 28 28 28 28 28 80 05 00 00 00 00 00 4b 4e 4c 54 c1 01 88 00 a6 80 00 00 58 82 00 00 04 1c 00 00 00 00 00 00 0c 64 81 a2 0a 0b 1a 40 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 0c 6c 70 07 c0 46 c0 46 6f 00 80 00 26 08 c0 6b 27 08 85 06 25 08 c0 6b 26 08 85 06 00 a0 26 09 26 0a 91 02 02 ca 08 50 04 b1 fa 87 24 09 27 08 00 fa 08 40 48 40 2f 08 2f 09 01 50 09 fe 01 41 41 41 2f 08 00 a1 41 40 ab a1 01 40 00 a2 06 a3 01 b2 9a 02 fc cd 01 a1 41 40 24 08 24 09 02 ec 0a 40 40 a2 8a 40 8a 48 d2 f7 d2 ff 01 aa fa c0 4a 48 00 a0 82 02 09 c1 16 09 17 0a 17 0b 9a 02 04 ca 08 58 10 50 04 b1 04 b2 f8 87 14 09 15 0a 15 0b 9a 02 04 ca 08 58 10 50 04 b1 04 b2 f8 87 01 90 10 9c fe 87 c0 46 12 00 00 00 13 00 00 00 d0 21 84 00 00 fe 84 00 50 20 84 00 dd 28 84 00 0c 06 80 00 00 09 84 00 00 0a 84 00 00 f0 00 00 00 09 00 00 bc 1b 00 00 00 20 84 00 00 20 84 00 bc 1b 00 00 00 20 84 00 48 20 84 00 7e 00 00 00 b8 00 80 00 60 00 80 00 00 00 00 ff 00 00 80 00 0c 00 80 00 c4 00 00 00 ff ff ff ff 00 20 84 00 00 00 85 00 09 00 00 00 00 65 ff 64 d8 6b 41 06 4a 06 53 06 5c 06 65 06 3f 64 00 90 0d 98 3f 6c 88 06 91 06 9a 06 a3 06 ac 06 d0 6b ff 6c 00 69 c0 46 c0 46 c0 46 c0 46 70 07 c0 46 10 65 00 f6 00 fe 0a 0b 1c 48 00 a2 1a 40 09 0b 18 40 09 09 40 a3 0b 40 01 a2 0b 48 13 00 fc c1 06 0a 10 48 01 b2 13 40 01 0b 1c 40 10 6d c0 46 43 06 80 00 b8 00 80 00 ba 00 80 00 b9 00 80 00 10 65 00 f6 00 fe 09 f6 09 fe 0a 0b 1c 48 00 a2 1a 40 09 0b 18 40 01 b3 19 40 08 09 60 a3 0b 40 01 a2 0b 48 13 00 fc c1 04 0a 13 40 01 0b 1c 40 10 6d c0 46 43 06 80 00 b8 00 80 00 ba 00 80 00 03 0a 11 58 00 f1 13 58 5b ea 98 02 fb c2 70 07 40 07 80 00 00 65 c8 a0 80 a1 ff 97 d1 9f 30 a0 01 a1 07 a2 07 a3 01 90 ad 9b c7 a0 0e a1 ff 97 c7 9f c7 a0 0f a1 ff 97 c3 9f cf a0 ff 97 a0 9f 03 f6 fa c5 cb a0 ff 97 9b 9f 01 ec 33 a0 ff 97 b7 9f 30 a0 00 a1 07 a2 07 a3 01 90 93 9b c7 a0 0e a1 ff 97 ad 9f 00 6d 10 65 30 a0 60 a1 ff 97 a7 9f c6 a0 f6 a1 ff 97 a3 9f c6 a0 f7 a1 ff 97 9f 9f 40 a4 cf a0 ff 97 7b 9f 04 02 fa c0 c9 a0 ff 97 76 9f 01 ec 32 a0 ff 97 92 9f ca a0 ff 97 6f 9f 01 ec 31 a0 ff 97 8b 9f c6 a0 f6 a1 ff 97 87 9f 30 a0 20 a1 ff 97 83 9f 10 6d 00 65 2d a0 ff 97 5e 9f 7f a1 01 00 2d a0 ff 97 79 9f 09 0b 19 48 02 a2 0a 03 12 f6 12 fe 1a 40 06 0b 1a 48 02 a1 8a 03 1a 40 22 b3 1a 48 0c a1 8a 03 1a 40 00 6d c0 46 73 00 80 00 86 05 80 00 02 f2 12 fe 0c 0b 1a 40 0c 09 10 a2 0b 48 1a 02 fc c1 02 f4 12 fe 08 0b 1a 40 08 09 10 a2 0b 48 1a 02 fc c1 00 f6 00 fe 03 0b 18 40 03 09 10 a2 0b 48 1a 02 fc c1 70 07 0c 00 80 00 0d 00 80 00 30 65 05 ec 07 0c 01 a3 23 40 01 a0 ff 97 5a 9f 00 a3 23 40 04 0b 1d 40 10 a2 23 48 1a 02 fc c1 30 6d c0 46 0d 00 80 00 0c 00 80 00 70 65 64 a0 ff 97 48 9f 05 a0 ff 97 e3 9f 0a 08 0a 0c 00 a6 0a 09 10 a2 01 a5 26 40 0b 48 1a 02 fc c1 23 48 1d 02 02 c0 01 b8 00 a8 f5 c1 01 a2 03 0b 1a 40 70 6d c0 46 80 96 98 00 0c 00 80 00 0d 00 80 00 70 65 06 ec 09 0c 25 48 00 a3 23 40 06 a0 ff 97 bf 9f 20 a0 ff 97 bc 9f 30 ec ff 97 99 9f 01 a2 03 0b 1a 40 ff 97 ca 9f 25 40 70 6d 43 06 80 00 0d 00 80 00 f0 65 06 ec 0c ec 15 ec 11 0b 1f 48")
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 00 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    ###

    msg1 = bytearray.fromhex("02 a0 00 00 00 00 00 00 00 a2 1a 40 06 a0 ff 97 a3 9f 02 a0 ff 97 a0 9f 30 ec ff 97 7d 9f 00 ac 0b c0 00 a0 0a 0e 0b 09 10 a2 2b 1c 33 40 0b 48 1a 02 fc c1 01 b0 84 02 f7 c8 01 a2 05 0b 1a 40 ff 97 a0 9f 01 0b 1f 40 f0 6d c0 46 43 06 80 00 0c 00 80 00 0d 00 80 00 f0 65 47 06 80 64 07 ec 0c ec 15 ec 17 0b 1a 48 90 06 00 a6 1e 40 03 a0 ff 97 72 9f 38 ec ff 97 4f 9f 13 0b 1e 40 13 08 10 a1 12 0a 03 48 19 02 fb c1 0a a3 13 40 10 a1 13 48 19 02 fc c1 00 ac 0b c0 00 a0 0a 0e 0b 09 10 a2 33 48 2b 14 0b 48 1a 02 fc c1 01 b0 a0 02 f7 c1 01 a2 05 0b 1a 40 02 0b 42 06 1a 40 04 6c 90 06 f0 6d 43 06 80 00 0c 00 80 00 0d 00 80 00 30 65 0b 0b 1d 48 00 a4 1c 40 05 a0 ff 97 3c 9f 08 0b 1c 40 08 09 10 a2 0b 48 1a 02 fc c1 05 0b 18 48 01 a2 01 b3 1a 40 01 0b 1d 40 30 6d c0 46 43 06 80 00 0c 00 80 00 0d 00 80 00 70 65 04 f6 24 fe 15 0b 1e 48 00 a2 1a 40 06 a0 ff 97 1c 9f 01 a0 ff 97 19 9f 11 0b 1c 40 11 0a 10 a3 10 0c 15 48 1d 00 fb c1 01 a3 23 40 ff 97 23 9f 64 a0 ff 97 6c 9e 05 a0 ff 97 07 9f 08 0b 1d 40 10 a2 23 48 1a 02 fc c1 05 0b 18 48 01 a2 01 b3 1a 40 01 0b 1e 40 70 6d c0 46 43 06 80 00 0c 00 80 00 0d 00 80 00 70 65 06 ec 09 0c 25 48 00 a3 23 40 06 a0 ff 97 e9 9e 52 a0 ff 97 e6 9e 30 ec ff 97 c3 9e 01 a2 03 0b 1a 40 ff 97 f4 9e 25 40 70 6d 43 06 80 00 0d 00 80 00 70 65 06 ec 09 0c 25 48 00 a3 23 40 06 a0 ff 97 cf 9e d8 a0 ff 97 cc 9e 30 ec ff 97 a9 9e 01 a2 03 0b 1a 40 ff 97 da 9e 25 40 70 6d 43 06 80 00 0d 00 80 00 30 65 07 0c 25 48 00 a3 23 40 b9 a0 ff 97 b6 9e 01 a2 04 0b 1a 40 01 a0 ff 97 12 9e 25 40 30 6d 43 06 80 00 0d 00 80 00 f0 65 07 0c 27 48 00 a3 23 40 ab a0 ff 97 a2 9e 04 0d 01 a6 2e 40 ff 97 b3 9e 2e 40 27 40 f0 6d 43 06 80 00 0d 00 80 00 70 65 06 ec 09 0c 25 48 00 a3 23 40 06 a0 ff 97 8d 9e 81 a0 ff 97 8a 9e 30 ec ff 97 67 9e 01 a2 03 0b 1a 40 ff 97 98 9e 25 40 70 6d 43 06 80 00 0d 00 80 00 30 65 08 0c 25 48 00 a3 23 40 06 a0 ff 97 74 9e 60 a0 ff 97 71 9e 01 a2 03 0b 1a 40 ff 97 82 9e 25 40 30 6d 43 06 80 00 0d 00 80 00 70 65 04 ec 13 0b 1e 48 00 a5 1d 40 9f a0 ff 97 5d 9e 11 0b 1d 40 11 08 10 a1 10 0a 03 48 19 02 fb c1 0a a3 13 40 10 a1 13 48 19 02 fc c1 e5 ec 09 08 0a 09 10 a2 03 48 23 40 01 b4 0b 48 1a 02 fc c1 ac 02 f7 c1 01 a2 04 0b 1a 40 01 0b 1e 40 70 6d c0 46 43 06 80 00 0c 00 80 00 0d 00 80 00 f0 65 0c ec 00 f6 05 fe 21 0b 1f 48 00 a6 1e 40 28 ec ff 97 2b 9e 4b ad 23 c0 5a ad 2c c0 00 a2 1c 0b 1a 40 1c 08 10 a1 1b 0a 03 48 19 02 fb c1 0a a3 13 40 10 a1 13 48 19 02 fc c1 25 ec 10 b5 14 08 15 09 10 a2 03 48 23 40 01 b4 0b 48 1a 02 fc c1 ac 02 f7 c1 01 a2 0f 0b 1a 40 0c 0b 1f 40 f0 6d 00 a0 ff 97 e2 9d 0a 0b 1e 40 0a 09 10 a2 0b 48 1a 02 fc c1 d2 87 80 a0 ff 97 d7 9d 05 0b 1e 40 05 09 10 a2 0b 48 1a 02 fc c1 c7 87 c0 46 43 06 80 00 0c 00 80 00 0d 00 80 00 f0 65 47 06 80 64 81 60 34 a0 87 a1 ff 97 22 9d 00 a3 26 0a 13 40 b9 a1 01 ba 11 40 00 33 00 3b 01 ab 05 c8 00 3b 01 b3 00 33 00 3b 01 ab f9 c9 1e 0f 01 a3 3b 40 1e 0e 00 a4 34 40 0b a0 38 a1 ff 97 08 9d 82 a0 0c a1 ff 97 04 9d 19 0b 1d 48 2d f2 19 0b ed e8 2b 58 98 06 18 0b 2b 50 ff 97 1f 9c 43 06 2b 50 82 a0 64 a1 ff 97 f3 9c 0b a0 3b a1 ff 97 ef 9c 0f a3 33 40 3c 40 ab a2 10 0b") 
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 04 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    #####

    msg1 = bytearray.fromhex("02 a0 00 1a 1a 1a 1a 1a 1a 40 00 34 00 3b 01 ab 05 c8 00 3b 01 b3 00 33 00 3b 01 ab f9 c9 01 a2 04 0b 1a 40 34 a0 80 a1 ff 97 d8 9c 01 60 04 6c 90 06 f0 6d 0d 00 80 00 a1 05 80 00 0d 06 80 00 58 00 84 00 c0 06 c0 06 0c 00 80 00 f0 65 28 a2 15 0b 1a 40 00 a4 00 a5 14 0a 08 a1 08 a7 14 0e 17 40 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 c0 06 13 48 19 02 fc c1 30 58 00 ac 06 c0 43 eb 01 ab 07 c9 2b ec 43 00 01 ab 02 c0 01 b4 05 ec de 87 28 ec f0 6d c0 46 4c 07 80 00 4f 07 80 00 54 07 80 00 00 65 08 08 17 a1 01 90 31 98 fa a3 5b f1 06 0a 13 20 01 a2 05 0b 1a 40 00 a3 05 0a 13 40 01 b2 13 40 00 6d 60 1b 00 00 50 07 80 00 4f 07 80 00 20 0c 80 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 10 65 81 02 08 c2 00 aa 05 c0 00 a3 c4 1c cc 14 01 b3 93 02 fa c1 10 6d 00 aa fc c0 53 ee c0 e8 c9 e8 54 02 00 a3 c2 1c ca 14 01 bb a3 02 fa c1 f1 87 c0 46 00 aa 06 c0 09 f6 09 fe 00 a3 c1 14 01 b3 93 02 fb c1 70 07 10 65 04 ec 08 ec 21 ec ff 97 d6 9f 20 ec 10 6d 82 60 03 ec cb 00 01 33 20 a3 59 ea 88 00 00 30 01 3b 00 38 18 03 02 60 70 07 c0 46 f0 65 5f 06 56 06 4d 06 44 06 f0 64 b8 60 07 30 08 78 80 06 18 7a 02 32 03 ec 08 48 00 f6 4a 48 12 f4 82 e8 c8 48 12 e8 88 48 00 f2 12 e8 04 d3 04 b1 02 3c 9c 02 f0 c1 28 7d 00 35 30 7e 01 36 07 39 08 b1 30 ec 20 a2 ff 97 c4 9f 30 3d 99 08 82 06 00 a7 30 7c 02 80 01 b7 10 af 60 c0 e1 59 89 06 26 59 30 ec 06 a1 ff 97 bc 9f 04 30 30 ec 0b a1 ff 97 b7 9f 83 06 30 ec 19 a1 ff 97 b2 9f a2 59 94 06 53 06 04 b3 9a 06 04 bb 04 db 43 06 04 b3 98 06 04 bb 02 db 8a e8 4a 04 59 06 04 3b 59 00 48 00 10 e8 62 59 61 06 4a 00 16 00 63 06 73 00 c6 e8 28 ec 02 a1 ff 97 94 9f 83 06 28 ec 0d a1 ff 97 8f 9f 81 06 28 ec 16 a1 ff 97 8a 9f 63 58 1a ec 2a 03 a1 58 0a 00 2b 00 15 ec 1d 03 4b 06 5a 06 53 00 58 00 28 e8 e3 58 9b e9 e3 50 86 e9 e6 51 04 bc 21 ec 20 b1 25 5a 25 50 07 a3 3b 00 07 ab a8 c1 01 3b 00 3a 61 da 61 d3 61 da 61 d3 60 da 60 d3 25 5a 0c ec 01 b7 10 af 9e c1 64 08 81 06 40 a0 81 04 08 7e 0a 80 0f a3 3b 00 0f ab 00 c1 8f 80 01 b7 40 af 00 c1 97 80 25 58 04 3e b1 5b 88 06 08 ec 11 a1 ff 97 4b 9f 03 30 40 06 13 a1 ff 97 46 9f 05 30 72 5a 93 06 33 ed 04 33 70 58 82 06 07 a1 ff 97 3c 9f 06 30 50 06 12 a1 ff 97 37 9f 33 58 9b 04 05 3a 03 39 4a 00 43 06 99 fa 4a 00 13 ec 5b 04 06 39 48 00 51 06 ca f8 50 00 1b e8 9a 06 33 54 e2 59 03 32 26 59 30 ec 06 a1 ff 97 1e 9f 83 06 30 ec 0b a1 ff 97 19 9f 80 06 30 ec 19 a1 ff 97 14 9f a3 59 9c 06 49 06 04 b1 89 06 04 b9 04 d9 41 06 5b 06 59 00 48 00 03 39 40 e8 82 e8 61 59 63 06 59 00 0e 00 73 00 d6 e8 56 04 28 ec 02 a1 ff 97 fb 9e 82 06 28 ec 0d a1 ff 97 f6 9e 80 06 28 ec 16 a1 ff 97 f1 9e 63 58 1a ec 2a 03 a1 58 0a 00 2b 00 15 ec 1d 03 43 06 51 06 4b 00 58 00 28 e8 e3 58 9b e9 e3 50 86 e9 e6 51 04 bc 21 ec 20 b1 23 5a 23 50 07 a3 3b 00 07 ab 00 c0 78 87 01 3b 00 3a 70 da 70 d3 31 da 31 d3 41 da 41 d3 0c ec 0f a3 3b 00 0f ab 00 c0 6f 87 08 78 18 79 40 a2 ff 97 ba 9e 04 39 40 b9 04 31 01 b7 40 af 00 c0 67 87 28 7c 00 a1 07 3d 40 dc 88 ec 80 f0 47 1d 2b e8 5a 48 12 f2 3a 03 9f 48 3f f4 3a 03 df 48")    
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 08 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    #####

    msg1 = bytearray.fromhex("02 a0 00 3f 3f 3f 3f 3f 3f f6 3a 03 92 e9 2a 14 10 fa 58 40 10 fc 98 40 12 fe da 40 01 b1 08 a9 e6 c1 38 60 3c 6c 90 06 99 06 a2 06 ab 06 f0 6d 18 1a 00 00 00 65 00 a1 68 a2 ff 97 7f 9e 00 6d f0 65 47 06 80 64 05 ec 0c ec 16 ee 35 c0 02 48 43 48 1b f2 13 03 82 48 12 f4 13 03 c2 48 12 f6 13 03 3f a0 18 00 f3 e8 2b 40 1a fa 6a 40 1a fc aa 40 1b fe eb 40 33 e8 98 06 3f a3 98 05 20 c9 00 a8 10 c0 40 a7 3f ea 2e ec 28 b6 30 e8 3a ec ff 97 5e 9e 28 ec 31 ec ff 97 70 9e e4 e9 46 06 40 be 3f ae 07 c9 28 ec 21 ec ff 97 67 9e 40 b4 40 be 3f ae f7 c8 00 ae 02 c1 04 6c 90 06 f0 6d 00 a0 28 b5 28 e8 21 ec 32 ec ff 97 41 9e f4 87 f0 65 47 06 80 64 90 60 04 ec 88 06 03 48 47 48 3f f2 1f 03 83 48 1b f4 1f 03 c3 48 1b f6 1f 03 fe f0 6d 06 68 06 00 a1 40 a2 ff 97 1f 9e 80 a3 2b 40 3f a2 17 00 37 af 32 c8 38 a2 d2 eb 20 ec 69 06 ff 97 95 9f 00 a3 00 33 33 fe 2b 41 33 fc 6b 41 33 fa ab 41 ee 41 20 ec 69 06 08 a2 ff 97 87 9f 43 06 00 a1 88 f8 02 b0 80 f0 05 1d 20 e8 42 48 12 f2 2a 03 85 48 2d f4 2a 03 c0 48 00 f6 02 03 10 fe 18 40 10 fc 58 40 10 fa 98 40 da 40 04 b1 04 b3 20 a9 e6 c1 10 60 04 6c 90 06 f0 6d 78 a2 d2 eb cb 87 c0 46 f0 65 47 06 80 64 9a 60 06 ec 88 06 17 ec 68 06 ff 97 54 9f 00 a3 00 33 01 33 0a 0a 02 7b 23 da 23 d3 23 da 23 d3 03 da 03 d3 68 06 31 ec 42 06 ff 97 4a 9f 68 06 39 ec ff 97 8e 9f 1a 60 04 6c 90 06 f0 6d 18 1b 00 00 08 0b 1b f3 1b fb 08 0a 9b e8 08 0a 13 50 08 0a 12 58 19 f6 09 fe 11 40 1b f4 1b fe 53 40 01 a0 70 07 c0 46 d0 21 84 00 00 80 fc ff d4 28 84 00 44 20 84 00 70 65 1a 0e 33 58 1a 49 58 49 00 f2 10 03 9a 49 12 f4 10 03 da 49 12 f6 10 03 1a 4a 5c 4a 24 f2 99 4a db 4a 14 03 12 0d 21 ec 2a ec ff 97 1a 9b 00 ac 0d c0 0f 08 2a 48 03 48 9a 02 14 c1 00 a3 03 80 e9 1c c2 1c 91 02 08 c1 01 b3 9c 02 f8 c8 33 58 24 f6 24 fe 1c 40 01 a0 70 6d 1b f6 1b fe 32 58 53 40 00 a0 f8 87 00 a3 f9 87 44 20 84 00 d0 23 84 00 d0 21 84 00 f0 65 23 0b 1a 58 13 49 50 49 00 f2 18 03 93 49 1b f4 d1 49 18 03 1f 0b 18 50 13 49 53 49 93 49 d5 49 00 ad 2e c0 00 a3 1b 0c 16 4a 51 4a 09 f2 31 03 96 4a 36 f4 31 03 d6 4a 36 f6 31 03 de f0 f1 00 e1 14 01 b3 9d 02 ef c1 14 0e 29 ec 32 ec ff 97 cc 9a 12 09 6d e8 0b ec 00 a7 f2 e8 11 09 52 e8 11 48 19 40 e0 e8 0e 09 40 e8 11 48 02 48 91 02 00 c0 01 a7 01 b3 ab 02 ef c1 78 ee 47 ee b8 01 f0 6d 29 ec 05 0a ff 97 b0 9a 00 a7 f5 87 44 20 84 00 d0 28 84 00 d0 21 84 00 d0 23 84 00 08 00 04 01 f8 ff fb fe 70 65 18 0b 1b 58 1a 49 58 49 00 f2 10 03 9a 49 12 f4 d9 49 10 03 14 0a 10 50 1a 49 5a 49 9a 49 dd 49 12 0c 29 ec 22 ec ff 97 8c 9a 00 a6 00 ad 14 cd 0f 09 68 e8 0b ec 02 80 01 b3 83 02 0d c0 e2 e8 0c 09 52 e8 11 48 19 40 12 48 ff aa f4 c1 01 b6 36 f6 36 fe 01 b3 83 02 f1 c1 a8 eb 45 ee a8 01 70 6d 44 20 84 00 d0 28 84 00 d0 23 84 00 08 00 04 01 f8 ff fb fe 70 65 82 60 15 0b 1b 58 19 49 5a 49 12 f2 0a 03 99 49 09 f4 0a 03 d8 49 00 f6 01 ec 11 03 1a 4a 5c 4a 24 f2 98 4a db 4a 14 03 63 ee 00 a0 07 ab 10 c8 02 ac 10 c9 0a 0e 6d 06 08 ec 21 ec 6a 06 ff 97 44 9a 00 a3 9a e9 e9 1c 11 40 01 b3 a3 02 f9 c1 01 a0 02 60 70 6d 02 0e ed 87 44 20 84 00 08 00 04 01 04 00 04 01 f0 65 57 06 4e 06 45 06 e0 64 27 0b 1b 58 1a 49 58 49 00 f2")
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 0c 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    #####

    msg1 = bytearray.fromhex("02 a0 00 10 10 10 10 10 10 03 9a 49 12 f4 d9 49 10 03 23 0e 30 50 19 4a 5a 4a 12 f2 0a 03 99 4a 09 f4 0a 03 db 4a 1b f6 13 03 9b f8 1d 0f 3b 50 01 a2 00 ab 1b c0 00 a3 99 06 1b 0d 6c ec ff b4 80 a3 5b f1 98 06 ff 97 bf 99 00 a3 9a 06 30 58 50 04 80 a1 49 f0 2a ec ff 97 fe 99 2b ec 02 80 01 b3 a3 02 09 c0 1a 48 ff aa f9 c0 00 a2 10 ec 1c 6c 90 06 99 06 a2 06 f0 6d 80 a3 5b f0 9a 04 c2 05 e4 c1 30 58 80 a3 5b f1 c0 e8 30 50 01 a3 99 04 3b 58 4b 05 d6 c8 01 a2 e8 87 44 20 84 00 d0 28 84 00 d8 28 84 00 d0 23 84 00 f0 65 5f 06 56 06 4d 06 44 06 f0 64 98 60 9b 0e 33 58 19 49 5a 49 12 f2 0a 03 99 49 09 f4 0a 03 d9 49 09 f6 11 03 88 06 19 4a 5a 4a 12 f2 0a 03 99 4a 09 f4 0a 03 db 4a 1b f6 13 03 99 06 11 7d 8f 0b 2a ec 13 db 13 d2 1b 58 13 50 8d 0b 40 06 18 03 82 06 8c 0c 02 a1 22 ec ff 97 a7 99 23 48 66 ab 1b c0 63 48 66 ab 18 c0 17 78 ff 97 b8 9a 17 3b 1b f4 1b fc 17 33 84 08 1a e8 00 aa 36 c0 83 09 5a e8 00 aa 32 c0 82 0a 93 02 2f c0 82 0a 13 20 33 58 06 a2 1a 40 00 a0 21 80 40 06 08 a1 22 ec ff 97 83 99 7d 0b 00 a5 7d 08 02 80 01 b3 83 02 0d c0 e2 e8 7b 09 52 e8 11 48 19 40 12 48 ff aa f4 c1 01 b5 2d f6 2d fe 01 b3 83 02 f1 c1 08 ad 42 c0 33 58 99 a2 1a 40 88 a2 5a 40 01 a0 18 60 3c 6c 90 06 99 06 a2 06 ab 06 f0 6d 0d 7f 4b a0 39 ec ff 97 a4 9a 00 a3 00 a0 02 80 01 b3 10 ab 09 c0 f9 1c ea 1c 91 02 f8 c1 01 b0 00 f6 00 fe 01 b3 10 ab f5 c1 10 a8 21 c0 42 06 13 fb 1b f3 9b 06 18 ec ff 97 f9 98 80 a3 5b f1 18 ec 58 04 00 30 65 ec ff b5 58 06 80 a1 49 f0 22 ec ff 97 34 99 23 ec 02 80 01 b3 ab 02 25 c0 1a 48 ff aa f9 c0 33 58 03 a2 9d 87 33 58 01 a2 9a 87 40 06 08 a1 22 ec ff 97 21 99 4c 0b 00 a5 4c 08 02 80 01 b3 83 02 0b c0 e2 e8 4a 09 52 e8 11 48 19 40 12 48 ff aa f4 c1 01 b5 2d f6 2d fe f0 87 08 ad 53 c0 33 58 66 a2 9e 87 80 a1 49 f0 8b 04 00 3a 93 05 c8 c1 01 7d 38 ec 10 a1 2a ec 01 a3 ff 97 8c 9d 00 a0 09 7f 84 06 63 06 3b 14 03 ec 00 a2 e9 1c 4a 00 08 b3 1f ab fa c9 3a 14 01 b0 08 a8 f2 c1 3b 48 3f ab 02 c8 7a 48 8b aa 44 c0 48 06 02 f2 15 7d 2b 40 7b 48 6b 40 bb 48 ab 40 e8 40 13 fc 2b 41 12 fe 6a 41 fb 48 ab 41 3b 49 eb 41 40 06 08 a1 2a ec ff 97 a2 98 40 06 08 a1 22 ec ff 97 cb 98 00 a3 00 a0 20 09 5a e8 e1 1c 11 40 e9 1c e2 1c 91 02 00 c0 01 a0 01 b3 08 ab f3 c1 00 a8 05 c0 33 58 04 a2 2c 87 33 58 02 a2 29 87 66 a3 2b 40 50 06 01 a1 2a ec ff 97 80 98 50 06 01 a1 22 ec ff 97 a9 98 2a 48 23 48 9a 02 00 c1 3c 87 33 58 05 a2 15 87 ba 48 9e aa b7 c1 7b 49 ba 49 7a 40 fa 49 ba 40 b1 87 44 20 84 00 38 1b 00 00 fe 0f 00 00 d0 23 84 00 38 9f ff ff af bf ff ff 85 60 00 00 08 80 00 01 08 00 04 01 10 00 04 01 f8 ff fb fe f0 65 57 06 46 06 c0 64 25 0d 2b 58 7f a4 25 0e 00 a2 92 06 77 ec ff b7 b8 06 02 80 5a 48 01 aa 1f c0 da 48 22 00 49 aa 35 c1 1a 48 01 aa f5 c1 1a 49 58 49 00 f2 10 03 9a 49 12 f4 10 03 da 49 12 f6 10 03 1a 4a 59 4a 09 f2 9f 4a db 4a 11 03 32 ec ff 97 29 98 2b 58 52 06 1a 40 5a 48 01 aa df c1 1a 49 58 49 00 f2 10 03 9a 49 12 f4 10 03 da 49 12 f6 10 03 1a 4a 59 4a 09 f2 9f 4a db 4a 11 03 42 06 ff 97 10 98 2b 58 52 06 5a 40 da 48 22 00 49 aa c9 c0 01 a0 0c 6c 90 06 9a 06 f0 6d 44 20 84 00 d0 21 84 00 f0 65 47 06 80 64 22 0f 3b 58 19 49")
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 10 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    #####

    msg1 = bytearray.fromhex("02 a0 00 5a 5a 5a 5a 5a 5a 49 12 f2 0a 03 99 49 09 f4 0a 03 d9 49 09 f6 11 03 88 06 1a 4a 5c 4a 24 f2 99 4a db 4a 14 03 19 0e 40 06 21 ec 32 ec fe 97 e4 9f 17 0d 40 06 21 ec 2a ec ff 97 0c 98 00 ac 0c c0 2a 48 33 48 9a 02 1b c1 00 a3 03 80 e9 1c f2 1c 91 02 0c c1 01 b3 9c 02 f8 c8 3b 58 22 f6 12 fe 1a 40 24 fa 5c 40 01 a0 04 6c 90 06 f0 6d 19 f6 09 fe 1b f4 1b fe 3a 58 11 40 53 40 00 a0 f3 87 00 a3 00 a1 f7 87 c0 46 44 20 84 00 d0 21 84 00 d0 23 84 00 f0 65 28 0b 1a 58 13 49 50 49 00 f2 18 03 93 49 1b f4 d1 49 18 03 24 0e 30 50 13 49 53 49 93 49 d5 49 00 ad 33 c0 00 a3 20 0c 17 4a 51 4a 09 f2 39 03 97 4a 3f f4 39 03 d7 4a 3f f6 39 03 df f0 f9 00 e1 14 01 b3 9d 02 ef c1 29 ec 22 ec fe 97 89 9f 30 58 16 0e 29 ec 32 ec fe 97 b1 9f 15 09 6d e8 0b ec 00 a7 f2 e8 13 09 52 e8 11 48 19 40 e0 e8 11 09 40 e8 11 48 02 48 91 02 00 c0 01 a7 01 b3 ab 02 ef c1 78 ee 47 ee b8 01 f0 6d 29 ec 06 0a fe 97 67 9f 30 58 29 ec 05 0a fe 97 90 9f 00 a7 f0 87 44 20 84 00 d0 28 84 00 d0 21 84 00 d0 23 84 00 08 00 04 01 f8 ff fb fe f0 65 57 06 4e 06 45 06 e0 64 41 0f 3a 58 13 49 50 49 00 f2 18 03 93 49 1b f4 d1 49 18 03 3d 09 8a 06 08 50 13 49 53 49 93 49 d3 49 00 ab 98 06 5a c0 00 a3 38 0d 14 4a 51 4a 09 f2 21 03 94 4a 24 f4 21 03 d4 4a 24 f6 21 03 dc f0 e1 00 e9 14 01 b3 98 05 ef c1 31 0c 41 06 22 ec fe 97 52 9f 2f 0a 16 ec 46 04 13 ec 00 a1 89 06 99 a2 94 06 88 a0 e2 e8 2b 09 52 e8 11 48 19 40 12 48 ff aa 05 c0 3a 58 61 06 11 40 50 40 01 a2 91 06 01 b3 b3 02 ee c1 00 a0 01 a3 99 05 20 c0 51 06 08 58 41 06 2a ec fe 97 00 9f 52 06 10 58 41 06 22 ec fe 97 28 9f 1a 0b 00 a0 e2 e8 1a 09 52 e8 11 48 19 40 ef e8 17 09 7f e8 11 48 3a 48 91 02 00 c0 01 a0 01 b3 b3 02 ef c1 01 b8 43 ee 98 01 1c 6c 90 06 99 06 a2 06 f0 6d 0c 0c 41 06 22 ec fe 97 09 9f 52 06 10 58 41 06 07 0a fe 97 d5 9e 53 06 18 58 41 06 22 ec fe 97 fd 9e 00 a0 e4 87 c0 46 44 20 84 00 d0 28 84 00 d0 21 84 00 d0 23 84 00 08 00 04 01 f8 ff fb fe 30 65 0e 0d 2b 58 19 49 5a 49 12 f2 0a 03 99 49 09 f4 0a 03 db 49 1b f6 13 03 00 a4 01 ab 0a c0 20 ec fe 97 35 9f 2b 58 18 40 44 00 1f a0 20 00 44 02 60 01 30 6d 28 a4 f2 87 c0 46 44 20 84 00 f0 65 57 06 46 06 c0 64 90 06 00 a2 90 05 31 c0 1a 0d 2b 48 00 ab 1e c1 19 0b 9a 06 1a ec 00 a7 01 a5 18 0e 80 a3 5b f0 9c 06 3b ec 00 a4 04 80 5b f8 73 00 01 b4 08 ac 05 c0 1d 02 f8 c1 5b f8 01 b4 08 ac f9 c1 08 d2 01 b7 67 05 ed c1 01 a3 0a 0d 2b 40 01 80 0a 0a 92 06 00 a3 ff a4 ca 1c 42 00 22 00 92 f0 55 06 aa 18 00 fa 50 00 01 b3 98 05 f4 c8 0c 6c 90 06 9a 06 f0 6d dc 28 84 00 d0 24 84 00 20 83 b8 ed f0 65 5f 06 56 06 4d 06 44 06 f0 64 81 60 3e 08 82 06 03 58 19 49 5a 49 12 f2 0a 03 99 49 09 f4 0a 03 d9 49 09 f6 11 03 00 31 19 4a 5a 4a 12 f2 0a 03 99 4a 09 f4 0a 03 db 4a 1b f6 13 03 99 06 5b fa 98 06 49 06 cb f5 db fd 9b 06 00 a2 90 05 55 c0 00 3d 00 a4 01 a6 76 02 2c 0f 28 ec 80 a1 89 f0 3a ec fe 97 56 9e 30 ec 39 ec 80 a2 92 f0 ff 97 82 9f 06 ec 01 b4 80 a3 9b f0 ed e8 a0 05 ec c8 43 06 00 a0 83 05 0d c0 5b f2 00 39 58 e8 1e 0c 59 06 22 ec fe 97 3d 9e 30 ec 21 ec 5a 06 ff 97 6a 9f 06 ec f6 03 52 06 13 58 ff a2 11 ec 31 00 18 4a 19 42 31 fa 11 00 58 4a 59 42 31 fc 11 00 98 4a")
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 14 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    #####

    msg1 = bytearray.fromhex("02 a0 00 99 99 99 99 99 99 42 36 fe d9 4a de 42 49 06 11 00 18 49 19 41 48 06 01 fa 11 00 58 49 59 41 48 06 01 fc 0a 00 99 49 9a 41 02 fe d9 49 da 41 01 a0 01 60 3c 6c 90 06 99 06 a2 06 ab 06 f0 6d 00 a3 01 a6 76 02 be 87 c0 46 44 20 84 00 d0 21 84 00 00 65 ff 97 2d 98 02 a0 00 90 c0 98 04 a2 01 0b 1a 40 00 6d 61 00 80 00 f0 65 47 06 80 64 01 a0 40 02 23 09 01 a2 ff 97 1f 9f 22 0b 98 06 19 58 21 0d 7f a4 00 a6 cb 48 a3 03 fc c0 2a ec 00 a3 c8 48 40 f6 40 fe 17 48 bc 06 84 05 07 c0 01 b3 05 b2 0d ab f4 c1 cb 48 23 00 cb 40 eb 87 0e 40 4e 40 8e 40 9a f0 d3 e8 eb e8 59 48 9a 48 12 f2 0a 03 d9 48 09 f4 0a 03 1b 49 1b f6 13 03 00 90 1d 98 00 f6 00 fe 01 a8 0b c0 47 06 39 58 ca 48 52 f6 52 fe ff a3 53 00 8b 40 cb 48 23 00 cb 40 c9 87 43 06 19 58 cb 48 5b f6 5b fe 8b 40 f4 87 d0 21 84 00 44 20 84 00 00 20 84 00 18 07 c0 46 00 65 ff 97 9d 9f ff 97 a7 9f fe 87 f0 65 57 06 46 06 c0 64 0e ee 29 cd 04 ec 00 a5 40 a7 80 a2 13 f4 98 06 3f a2 92 06 07 80 08 aa 23 c0 07 aa 27 c0 01 b5 04 b4 ae 02 18 cd 23 48 61 48 09 f2 08 ec 18 03 a1 48 e3 48 1f 02 f2 c0 42 06 02 03 94 06 52 06 1a 00 03 aa e7 c1 80 a2 12 f4 13 ec 63 04 19 40 01 b5 04 b4 ae 02 e6 cc 30 ec 0c 6c 90 06 9a 06 f0 6d 63 06 18 f6 00 fe fe 97 24 9c d7 87 00 f2 40 e8 fe 97 3f 9c d2 87 f0 65 0f f6 3f fe 16 f6 36 fe 1c f6 24 fe 05 f6 2d fe 28 ec fe 97 f2 9b 01 b6 36 eb 01 a3 b3 00 1e ec 01 be 33 ec a3 00 01 ec 99 03 37 00 a7 00 39 03 09 f6 09 fe 28 ec fe 97 00 9c f0 6d c0 46 00 f6 00 fe 05 a8 08 c9 00 a2 0b 0b 1a 40 0a b3 1a 48 01 a1 8a 03 1a 40 70 07 80 f0 07 0b 1b 18 9f 06 20 a2 f1 87 44 a2 ef 87 43 a2 ed 87 42 a2 eb 87 60 a2 e9 87 c0 46 66 00 80 00 48 1b 00 00 98 2f 8a 42 91 44 37 71 cf fb c0 b5 a5 db b5 e9 5b c2 56 39 f1 11 f1 59 a4 82 3f 92 d5 5e 1c ab 98 aa 07 d8 01 5b 83 12 be 85 31 24 c3 7d 0c 55 74 5d be 72 fe b1 de 80 a7 06 dc 9b 74 f1 9b c1 c1 69 9b e4 86 47 be ef c6 9d c1 0f cc a1 0c 24 6f 2c e9 2d aa 84 74 4a dc a9 b0 5c da 88 f9 76 52 51 3e 98 6d c6 31 a8 c8 27 03 b0 c7 7f 59 bf f3 0b e0 c6 47 91 a7 d5 51 63 ca 06 67 29 29 14 85 0a b7 27 38 21 1b 2e fc 6d 2c 4d 13 0d 38 53 54 73 0a 65 bb 0a 6a 76 2e c9 c2 81 85 2c 72 92 a1 e8 bf a2 4b 66 1a a8 70 8b 4b c2 a3 51 6c c7 19 e8 92 d1 24 06 99 d6 85 35 0e f4 70 a0 6a 10 16 c1 a4 19 08 6c 37 1e 4c 77 48 27 b5 bc b0 34 b3 0c 1c 39 4a aa d8 4e 4f ca 9c 5b f3 6f 2e 68 ee 82 8f 74 6f 63 a5 78 14 78 c8 84 08 02 c7 8c fa ff be 90 eb 6c 50 a4 f7 a3 f9 be f2 78 71 c6 67 e6 09 6a 85 ae 67 bb 72 f3 6e 3c 3a f5 4f a5 7f 52 0e 51 8c 68 05 9b ab d9 83 1f 19 cd e0 5b 51 01 51 01 51 01 51 01 51 01 51 01 51 01 51 01 fe 19 00 00 02 1a 00 00 06 1a 00 00 0a 1a 00 00 fa 19 00 00 e0 19 00 00 60 00 00 c3 61 00 00 c3 62 00 00 c3 63 00 ff c3 64 00 ff c3 65 00 ff c3 82 00 64 c8 34 00 80 c8 0b 00 3b c8 8c 00 02 c8 27 00 00 c8 28 00 00 c8 29 00 00 c8 2a 00 00 c8 40 0c 04 c3 41 0c 04 c3 42 0c 04 c3 43 0c 04 c3 44 0c 04 c3 45 0c 04 c3 46 0c 04 c3 47 0c 04 c3 48 0c 04 c3 40 b9 0d 00 00 41 f5 13 00 00 42 ed 0d 00 00 43 91 14 00 00 44 65 0e 00 00 45 4d 15 00 00 46 0d 0f 00 00 4d ed 0f 00 00 4e 75 16 00 00 4f 85 0f 00 00 49 4d 13 00 00 50 3d 17 00 00 56 a5 10 00 00 00 00 00")
    msg2 = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 18 04 00 00 04 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    ################### Fim gravacao

    msg1  = bytearray.fromhex("02 a0 00 04 04 04 04 04 04 00 84 00")
    msg2  = bytearray.fromhex("02 9f f8 00 00 00 00 00 00 1c 04 00 04 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x04))
    # print("".join("%02x" % i for i in result))

    ############

    msg1  = bytearray.fromhex("02 a0 00 88 88 88 88 88 88")
    msg2  = bytearray.fromhex("02 9f f8 02 02 02 02 02 02 06 00 00 01 00 00 41")

    ################

    send(wValue = 0xa000, data_or_wLength = msg1)
    # time.sleep(0.030)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    # print("TC32 EVK : Swire OK")
    return True

import struct

def erase_adr(adr = 0):

    msg1 = bytearray.fromhex("02 a0 00 4d 4d 4d 4d 4d 4d 00 00 00 00 04 00 00 00")

    adr_bin = list((adr).to_bytes(2, byteorder="little"))

    msg1[10:12]=adr_bin

    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    time.sleep(0.003)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x09))
    # print("".join("%02x" % i for i in result))

    ######################

    msg1  = bytearray.fromhex("02 a0 00 cd cd cd cd cd cd")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    time.sleep(0.003)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    ######################

    msg1 = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1")

    timeout_start = time.time() + 5

    while(True):
        send(wValue = 0x9ff8, data_or_wLength = msg1)
        # time.sleep(0.003)
        result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
        # print("".join("%02x" % i for i in result))

        result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 0)
        # print("".join("%02x" % i for i in (result)))

        # print("".join("%02x" % result[0]))

        if(time.time() > timeout_start):
            break

        if(result[0] == 0x4d):
            # print("deu")
            break

    if time.time() >= timeout_start:
        raise ValueError('Timeout') 

    msg1 = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x0c))
    # print("".join("%02x" % i for i in result))

    result = (receive(wValue = 0xa000, data_or_wLength = 20, timeOut = 0))

    # print("".join("%02x" % i for i in (result)))

    
    # print("Flash Sector (4K) Erase at address: " + str(hex_value))

    return True


def erase():
    # if erase_init():
    #     print("TC32 EVK : Swire OK")

    # for i in range(0,2048,16):
    #     erase_adr(adr = i)
    #     hex_value = hex(i * 0x100)
    #     print("Flash Sector (4K) Erase at address: " + str(hex_value))

    return True


def download_init():

    erase_init()

    # "send"="02 a0 00 40 40 40 40 40 40 00 00 00 00 00 00 00 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41"
    # "recv"="09 00 00 00 c4 30 00 00 07 00 04 00 00 00 00 00"

    # "send"="02 a0 00 c0 c0 c0 c0 c0 c0"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41"
    # "recv"="01 00 00 00 7c 1a 00 00 07 00 04 00 00 00 00 00"

    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="40"

    # "send"="02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1"
    # "recv"="0c 00 00 00 fb 32 00 00 04 00 04 00 00 00 00 00"
    # "recv"="d0 a1 40 40 00 00 00 00 00 00 00 00"

    msg1  = bytearray.fromhex("02 a0 00 40 40 40 40 40 40 00 00 00 00 00 00 00 00")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x09))
    # print("".join("%02x" % i for i in result))

    ###############

    msg1  = bytearray.fromhex("02 a0 00 c0 c0 c0 c0 c0 c0")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    ###############

    msg1  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 5, reset = True, test_index = 0, test_data = 0x40))
    # print("".join("%02x" % i for i in result))

    ###############

    msg1  = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x0c))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0xa000, data_or_wLength = 20, timeOut = 0))
    # print("".join("%02x" % i for i in result))

    return True


def download_end():
    # "send"="02 a0 00 50 50 50 50 50 50 00 00 00 00 00 fc 03 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41"
    # "recv"="09 00 00 00 c4 30 00 00 07 00 04 00 00 00 00 00"
    # "send"="02 a0 00 d0 d0 d0 d0 d0 d0"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41"
    # "recv"="01 00 00 00 7c 1a 00 00 07 00 04 00 00 00 00 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 af 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="d0"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="50"
    # "send"="02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1"
    # "recv"="0c 00 00 00 fb 32 00 00 04 00 04 00 00 00 00 00"
    # "recv"="00 00 50 50 00 fc 03 00 3b 96 78 e1"


    msg1  = bytearray.fromhex("02 a0 00 50 50 50 50 50 50 00 00 00 00 00 fc 03 00")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x09))
    # print("".join("%02x" % i for i in result))

    ###############

    msg1  = bytearray.fromhex("02 a0 00 d0 d0 d0 d0 d0 d0")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    ###############

    msg1 = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1")

    timeout_start = time.time() + 5

    while(True):
        send(wValue = 0x9ff8, data_or_wLength = msg1)
        # time.sleep(0.003)
        result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
        # print("".join("%02x" % i for i in result))

        result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 0)
        # print("".join("%02x" % i for i in (result)))

        # print("".join("%02x" % result[0]))

        if(time.time() > timeout_start):
            break

        if(result[0] == 0x50):
            # print("deu")
            break

    if time.time() >= timeout_start:
        raise ValueError('Timeout') 

    ###############

    msg1  = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x0c))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0xa000, data_or_wLength = 20, timeOut = 0))
    # print("".join("%02x" % i for i in result))

    # print("Download Finish")
    return True

def donwload_adr(data, adr):

    # "send"="02 a0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00"
    # "send"="02 9f f8 d0 d0 d0 d0 d0 d0 21 04 00 00 01 00 41"
    # "recv"="00 00 00 00 fb 32 00 00 d0 21 04 00 00 00 00 00"
    # "recv"="00 01 00 00 ae e0 02 00 d0 21 04 00 00 00 00 00"
    # "send"="02 a0 00 41 41 41 41 41 41 00 f0 03 00 00 01 00 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41"
    # "recv"="09 00 00 00 c4 30 00 00 07 00 04 00 00 00 00 00"
    # "send"="02 a0 00 c1 c1 c1 c1 c1 c1"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41"
    # "recv"="01 00 00 00 7c 1a 00 00 07 00 04 00 00 00 00 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="41"
    # "send"="02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1"
    # "recv"="0c 00 00 00 cf 32 00 00 04 00 04 00 00 00 00 00"
    # "recv"="00 01 41 41 00 f0 03 00 00 01 00 00"

    msg1  = bytearray.fromhex("02 a0 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00")
    
    msg1[8:]=data

    msg1[3]=data[0]
    msg1[4]=data[0]
    msg1[5]=data[0]
    msg1[6]=data[0]
    msg1[7]=data[0]

    # print("".join("%02x" % i for i in msg1))

    msg2  = bytearray.fromhex("02 9f f8 d0 d0 d0 d0 d0 d0 21 04 00 00 01 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 8, test_data = 0xd0))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 1, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    ##############

    msg1  = bytearray.fromhex("02 a0 00 41 41 41 41 41 41 00 00 00 00 00 01 00 00")

    adr_bin = list((adr).to_bytes(2, byteorder="little"))
    msg1[10:12]=adr_bin

    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x09))
    # print("".join("%02x" % i for i in result))

    ##############

    msg1  = bytearray.fromhex("02 a0 00 c1 c1 c1 c1 c1 c1")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))


    #############

    msg1 = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1")

    timeout_start = time.time() + 5

    while(True):
        send(wValue = 0x9ff8, data_or_wLength = msg1)
        # time.sleep(0.003)
        result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
        # print("".join("%02x" % i for i in result))

        result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 0)
        # print("".join("%02x" % i for i in (result)))

        # print("".join("%02x" % result[0]))

        if(time.time() > timeout_start):
            break

        if(result[0] == 0x41):
            # print("deu")
            break

    if time.time() >= timeout_start:
        raise ValueError('Timeout') 

    ###########

    msg1 = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x0c))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0xa000, data_or_wLength = 20, timeOut = 0))
    # print("".join("%02x" % i for i in result))

    # print("".join("Flash Page Program at address %02x" % int(adr*256)))

    return True

def download_block_init(adr):
    
    # "send"="02 a0 00 4d 4d 4d 4d 4d 4d 00 10 00 00 04 00 00 00"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41"
    # "recv"="09 00 00 00 c4 30 00 00 07 00 04 00 00 00 00 00"

    # "send"="02 a0 00 cd cd cd cd cd cd"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41"
    # "recv"="01 00 00 00 7c 1a 00 00 07 00 04 00 00 00 00 00"

    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="cd"

    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 af 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="cd"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="cd"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="cd"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="cd"
    # "send"="02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1"
    # "recv"="01 00 00 00 c5 18 00 00 07 00 04 00 00 00 00 00"
    # "recv"="4d"
    # "send"="02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1"
    # "recv"="0c 00 00 00 fb 32 00 00 04 00 04 00 00 00 00 00"
    # "recv"="00 00 4d 4d 00 10 00 00 04 00 00 00"

    msg1  = bytearray.fromhex("02 a0 00 4d 4d 4d 4d 4d 4d 00 00 00 00 04 00 00 00")

    adr_bin = list((adr).to_bytes(2, byteorder="little"))
    msg1[10:12]=adr_bin

    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 09 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x09))
    # print("".join("%02x" % i for i in result))

    #################

    msg1  = bytearray.fromhex("02 a0 00 cd cd cd cd cd cd")
    msg2  = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 41")

    send(wValue = 0xa000, data_or_wLength = msg1)
    send(wValue = 0x9ff8, data_or_wLength = msg2)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
    # print("".join("%02x" % i for i in result))

    #################

    msg1 = bytearray.fromhex("02 9f f8 07 07 07 07 07 07 00 04 00 01 00 00 c1")

    timeout_start = time.time() + 5

    while(True):
        send(wValue = 0x9ff8, data_or_wLength = msg1)
        # time.sleep(0.003)
        result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x01))
        # print("".join("%02x" % i for i in result))

        result = receive(wValue = 0xa000, data_or_wLength = 9, timeOut = 0)
        # print("".join("%02x" % i for i in (result)))

        # print("".join("%02x" % result[0]))

        if(time.time() > timeout_start):
            break

        if(result[0] == 0x4d):
            # print("deu")
            break

    if time.time() >= timeout_start:
        raise ValueError('Timeout') 

    ################

    msg1 = bytearray.fromhex("02 9f f8 04 04 04 04 04 04 00 04 00 0c 00 00 c1")

    send(wValue = 0x9ff8, data_or_wLength = msg1)
    # time.sleep(0.003)
    result = (receive(wValue = 0x9ff0, data_or_wLength = 24, timeOut = 5, reset = True, test_index = 0, test_data = 0x0c))
    # print("".join("%02x" % i for i in result))
    result = (receive(wValue = 0xa000, data_or_wLength = 20, timeOut = 0))
    # print("".join("%02x" % i for i in result))

    # print("Erase: " + str(int(adr*16)))
    # print("".join("Flash Sector (4K) Erase at address %02x" % int(adr*256)))

    return True
    

####Main

# if(activate() == True):
#     print("Activate OK!")

# for i in range(10):
#     dev.ctrl_transfer(bmRequestType = 0xC1, bRequest = 0x02, wValue = 0x7c, wIndex = 0, data_or_wLength = 12)

# erase()

if __name__ == "__main__":
    driver_init()

    if(activate() == True):
        print("Activate OK!")

    for i in range(10):
        dev.ctrl_transfer(bmRequestType = 0xC1, bRequest = 0x02, wValue = 0x7c, wIndex = 0, data_or_wLength = 12)

    erase()

    download_init()

    data = bytearray.fromhex("01 02 03 04 05 06 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 05 04 03 02 01")

    download_block_init(5)
    donwload_adr(data, 5)



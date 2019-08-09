import struct
from bluepy.btle import Scanner, DefaultDelegate, UUID, Peripheral

TARGET_UUID = "BLE Keyboard"
#TARGET_UUID = "Galaxy S9+"
target_dev = None
UART_SERVICE_UUID = UUID("1b72634b-ab7b-4f99-8086-ba0124f4681f")
uart_service = None
UART_WRITE_UUID = UUID("13125d01-fd8b-41f2-b0fe-746fddc2feb0")
write_char = None
#UART_READ_UUID = UUID("326d606d-fe02-4f6d-bf6a-17395639c549")
UART_READ_UUID = UUID("0000fff4-0000-1000-8000-00805f9b34fb")
read_char = None
read_handle = None
write_char = None
write_handle = None
read_cccd = None

#############################################
# Define scan callback
#############################################
class ScanDelegate(DefaultDelegate):
        def __init__(self):
                    DefaultDelegate.__init__(self)                 

        def handleDiscovery(self, dev, isNewDev, isNewData):
            if isNewDev:
                print("Discovered device %s" % dev.addr)
            elif isNewData:
                print("Received new data from %s", dev.addr)

#############################################
# Define notification callback
#############################################
class NotifyDelegate(DefaultDelegate):
        #Constructor (run once on startup)  
        def __init__(self, params):
                    DefaultDelegate.__init__(self)

        #func is caled on notifications
        def handleNotification(self, cHandle, data):
            print("Noti function")
            #print("Notification : " + data.decode("utf-8"))
            print("notification : " + str(data))

#############################################
# Main starts here
#############################################
scanner = Scanner().withDelegate(ScanDelegate())
devices = scanner.scan(5.0)

for dev in devices:
    print("Device %s (%s), RSSI=%d dB" % (dev.addr, dev.addrType, dev.rssi))

    for (adtype, desc, value) in dev.getScanData():
# Check iBeacon UUID
# 255 is manufacturer data (1  is Flags, 9 is Name)        
        if adtype is 9 and TARGET_UUID in "BLE Keyboard" :
            target_dev = dev
            print("  +--- found target device!!")
        print("  (AD Type=%d) %s = %s" % (adtype, desc, value))
if target_dev is not None:
    #############################################
    # Connect
    #############################################
    print("Connecting...")
    print(" ")
    
    p = Peripheral(target_dev.addr, target_dev.addrType)
    #p = Peripheral("00:0B:57:25:B6:1F", "public")

    try:
        # Set notify callback
        p.setDelegate(NotifyDelegate(p))
        #############################################
        # For debug
        #############################################
        services=p.getServices()
        # displays all services
        for service in services:
            print(service)
            # displays characteristics in this service
            chList = service.getCharacteristics()
            print("-------------------------------------------------------")
            print("Handle   UUID                                Properties")
            print("-------------------------------------------------------")
            for ch in chList:
                print("  0x"+ format(ch.getHandle(),'02X')  +"   "+str(ch.uuid) +" " + ch.propertiesToString())
            print("-------------------------------------------------------")
            print(" ")

            #############################################
            # Set up characteristics
            #############################################
            uart_service = p.getServiceByUUID(UART_SERVICE_UUID)
            write_char = uart_service.getCharacteristics(UART_WRITE_UUID)[0]
            read_char = uart_service.getCharacteristics(UART_READ_UUID)[0]

#print("read char = ", read_char.handle)
#print("write char = ", write_char.handle)

#spp_service = p.getServiceByUUID(SPP_SERVICE_UUID)
#spp_send_data = spp_service.getCharacteristics(SPP_SEND_UUID)[0]

            read_handle = read_char.getHandle()
            write_handle = write_char.getHandle()

#spp_handle = spp_send_data.getHandle()

            print("read handle value : 0x" + format(read_handle, "02X"))
            print("write handle value : 0x" + format(write_handle, "02X"))

            #spp_send_data.write(str.encode("hi gyutae"))

            # Search and get the read-Characteristics "property" 
            # (UUID-0x2902 CCC-Client Characteristic Configuration))
            # which is located in a handle in the range defined by the boundries of the Service
            for descriptor in p.getDescriptors(read_handle, 0xFFFF):  # The handle range should be read from the services 
                if (descriptor.uuid == 0x2902):                   #      but is not done due to a Bluez/BluePy bug :(     
                        print("Client Characteristic Configuration found at handle 0x"+ format(descriptor.handle, "02X"))
                        read_cccd = descriptor.handle
                        #spp_cccd = descriptor.handle
                        p.writeCharacteristic(read_cccd, struct.pack('<bb', 0x01, 0x00))
                        #p.writeCharacteristic(spp_cccd, struct.pack('<bb', 0x01, 0x00))
                        #print("pack ", struct.pack('<bb', 0x01, 0x00))
            
            #############################################
            # BLE message loop
            #############################################
            while True:
                if p.waitForNotifications(5.0):
                    # handleNotification() was called
                    continue
                    #pass
                
                # p.writeCharacteristic(hButtonCCC, struct.pack('<bb', 0x01, 0x00))
                #print("waiting ... ")
                write_char.write(str.encode("Hello GTO \n"))
                #read_char.read()
#spp_send_data.write(str.encode("spp send data\n"))
#spp_send_data.read()
                print("OK ---> Send write data!")

    finally:
     p.disconnect()

else:
    print("No matching device found...")

print("Close app")

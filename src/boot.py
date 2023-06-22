import board
import digitalio
import storage, usb_hid, usb_midi
import os
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
led.value = True

topSwitch = digitalio.DigitalInOut(board.GP2)
topSwitch.direction = digitalio.Direction.INPUT
topSwitch.pull = digitalio.Pull.UP
storage.remount("/", readonly=False)

if (not topSwitch.value) or (os.getenv('OPEN_AI_KEY') == "Bearer xx-xxxxxxxxx..."): #hold top button for usb host write access, or allow usb host write access if keys are missing
	storage.remount("/", readonly=True)
	print('readonly false')



#print('boot!')
#import usb_cdc

#usb_cdc.disable()   # Disable both serial devices.

#usb_cdc.enable(console=True, data=False)   # Enable just console
                                           # (the default setting)
  
#usb_cdc.enable(console=True, data=True)    # Enable console and data

#usb_cdc.enable(console=False, data=False)  # Disable both
                                           # Same as usb_cdc.disable()
                                           
                                        


usb_hid.disable()       # Disable all HID devices.
usb_midi.disable()
#storage.disable_usb_drive()
#storage.remount("/", readonly=False)

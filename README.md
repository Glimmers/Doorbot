Doorbot -- Internet enabled doorbell discord bot
================================================

This project contains the files and schematics needed to build a raspberry-pi compatible doorbell
which will send a message to a Discord channel.

Dependencies
------------

* A Raspberry Pi running Raspbian
* The following packages

        python3
        python3-rpi.gpio
        python3-requests

* A Discord account
* A webhook set up for the discord channel you want your messages to go to. For instructions on
      setting up a webhook, visit
      https://support.discordapp.com/hc/en-us/articles/228383668-Intro-to-Webhooks

Software Installation instructions
----------------------------------

1. Download the package to your pi.

    * Via git: 

            git clone https://github.com/Glimmers/Doorbot.git doorbot

    * Via wget:

            wget https://github.com/Glimmers/Doorbot/archive/master.zip

2. Run the included install.sh shell script to add the requisite service user, install dependencies,
copy the files into the service user's directory, and install the systemd service.

3. Copy the example discord.ini file to the actual ini file, and fill out the fields inside. At a
minimum, you will need to replace all the values in the [Doorbot] section.

    a) If you're not using a camera, set UseCamera = no .

    b) If you are using a Camera, fill out the [Camera] section with the access type, hostname,
    username and password if needed, and path to get an image. For example, if the URL to get an image
    from the camera is: http://hostname/path/to/image.cgi , you'll want to set the config values as:

        [Camera]
        Protocol = http
        Host = hostname
        Path = /path/to/image.cgi

4. Enable the doorbot service
    
        sudo systemctl enable doorbot.service

5. Start the doorbot service

        sudo systemctl start doorbot.service
   

Hardware Installation Instructions
----------------------------------

In the Eagle Schematics directory, there are schematics in Eagle 7.x format for two variants of sense
boards. The first -- Doorbell.sch -- is a basic 1-transistor schematic. The second --
DoorbellBothRelayBJT.sch -- is the 3-transistor schematic which has better noise tolerance. For both of
these circuits, hooking up to the Pi side of the board is the same. Pin 1 goes to the +3.3 volt supply
pin of the Pi (pin 1 or pin 17). Pin 2 goes to one of the GPIO pins, typically pin 37. Pin 3 goes to
Ground (any one of pin 6, 9, 14, 20, 25, 30, 34, or 39).

*     For the 1 transistor schematic, pin 1 of the relay side goes to the Normally Open pin of the
      relay. Pin 3 of the relay goes to the common side. Pin 2 is for testing, and not used for normal
      operation.

*     For the 3-transistor schematic, pin one of the relay side goes to the Normally Open pin of the
      relay. Pin 2 goes to the Common pin of the relay. Pin 3 goes to the Normally Closed pin.

For hooking the relay up to the chime, typically you'll hook the coil leads so one is going to the
terminal labelled "Trans" and the other to the terminal labelled "Front". While hooking it up, you'll
want to either disconnect the doorbell transformer, or have someone watching the door to
avoid the risk of getting shocked while hooking it up.

For Testing/Development
-----------------------

The one-transistor board has a provision for testing, which is useful in developing the software for
the board. In testing, remove the board from the relay, and hook a 2N2222 or 2N3904 transistor to the
relay header, with pin 1 of the transistor corresponding to pin 1 of the socket, pin 2 of the
transistor going to pin 2 of the socket, and pin 3 going to pin 3. The test pin should go to one of the
GPIO leads of the PI, typically pin 35.

License
-------

This project is available under the 2-clause BSD license. For details of the license, see the LICENSE file.


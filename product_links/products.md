# Product Links

This document contains a list of the physical tools that are used throughout the lesson along with links to where the items can be purchased. 

I have selected these tools as the best balance of affordability and quality that I was able to find in an effort to keep this course as affordable as possible. I have tested all the tools linked and used them throughout the recording of this course. That being said, if you are interested in continuing with hardware hacking you may want to invest in more expensive tools, I'd encourage you to do so however I can only support and guarantee the lab activities will work with the tools in this list. 

**I've split the list into two sections:**

1. Required for Hands-On Participation: These items are required at a minimum if you'd like to participate in all of the hands-on labs and activities in the course. 
2. Optional: These are items that I use or demonstrate in the course but are not required to follow along with the hands-on portions however they make things easier. 

**Note that I've tried to add as much detail as possible about what each tool will be used for and if there are alternatives to purchasing.**

None of the links provided are affiliate links and I make no commission of of their sales. 

# Required:

## Practice Target: TP-Link WR841n Wireless Router

**Where is this used:** The router is used throughout almost the entire course as the practice target that we will be using for practicing taking measurements, sniffing communications and extracting firmware. 

**Alternative to purchasing:** If you are unable to or would prefer not to purchase this router then you won't be able to follow along with any of the hands-on measuring or testing, however, I'll make things like the analyzer captures available and you can download a copy of the firmware for analysis from the TP-Link website. With these files, you'll still be able to follow along with and complete all the portions of the course that rely on analyzing the captures and firmware. If you choose to not purchase the router then I'd suggest skipping the rest of the tools below as you'll need something to test or use the tools on. 

**Links to Purchase:**

Link 1: https://www.tp-link.com/us/where-to-buy/

Link 2: https://www.amazon.com/TP-Link-N300-Wireless-Wi-Fi-Router-TL-WR841N/dp/B001FWYGJS

## Number 1 Phillips Screw Driver

**Where is this used:** Used to open the two retaining screws on the router. 

**Alternative to purchasing:** You'll need this to open the router, pretty much any Number 1, 0 or 00 Phillips screwdriver will work for this. 

**Links to Purchase:**

Note - you don't need to purchase these specific ones - I'm only linking for convenience if you need to buy one. Use whatever ph1/ph0 screwdriver you prefer or have. 

Link to Jewellers Screw Driver Kit: https://www.amazon.com/Screwdriver-Eyeglass-Precision-Different-Screwdrivers/dp/B07YJG766F

Number 1 Phillips Screwdriver: https://www.amazon.com/Wera-05118020001-Screwdriver-Electronic-Applications/dp/B0001P18LO


## UART to USB Adapter: CP2102 TTL USB to UART Adapter

**Where this is used:** This tool is used to interface with the UART pins on the router and establish a serial shell connection. 

**Alternative to purchasing:** Unfortunately there is not a great alternative to purchasing this, if you'd prefer to skip this then you won't be able to follow along with any of the sessions where we use the serial shell to the router. 

**Links to Purchase:**

Note that you'll see these devices sold in many different form factors and branding, any of the CP2102 TTL to USB should be sufficient however I've linked the one I used in the course below from a few different vendors.

Link 1: https://www.amazon.com/IZOKEE-CP2102-Converter-Adapter-Downloader/dp/B07D6LLX19

Link 2: https://www.amazon.com/HiLetgo-CP2102-Converter-Adapter-Downloader/dp/B00LODGRV8

Link 3: https://www.amazon.com/CP2102-Serial-Adapter-Converter-Module/dp/B08ZS6H9VS

Link 4: https://www.aliexpress.com/item/1005003536455256.html

## Male through-hole header pins

**Where this is used:** These are used to enable a connection to the UART pins on the router. The router PCB has bare through-hole pads exposed for UART and in order to interface with them with the other tools we need to attach these header pins. A solderless option using these pins is demonstrated in the course. 

**Alternative to purchasing:** Unfortunately there is not a great alternative to purchasing this, luckily they are not expensive and are a great component to keep in your home lab. That being said, if you do purchase one of the ch341a programmers below many of them come with 4-pin headers for breakout additions and you could use one of those. 

**Links to Purchase:**

Note these are pretty standard and you can grab them from any electronics shop. I've linked a few below. 

Link 1: https://www.amazon.com/Proto-Advantage-HDR100IMP40M-G-V-TH-Vertical-Header-Through/dp/B098KLMT7T

Link 2: https://www.digikey.com/en/products/detail/w%C3%BCrth-elektronik/61300311121/4846825

Link 3: https://www.mouser.com/ProductDetail/Chip-Quik/HDR100IMP40M-G-V-TH?qs=Wj%2FVkw3K%252BMBASWNGaQOKpg%3D%3D

## Digital Multimeter: AstroAI AM33D Multimeter 2000 Counts Digital Multimeter

**Where this is used:** The multimeter is used throughout the course for testing and verification, in addition, most of section 2 of the course is dedicated to teaching how to use a multimeter and its various functions. 

**Alternative to purchasing:** If you don't purchase a multimeter then you won't be able to follow along with section 2 and a few of the additional verification steps in other lessons. While it's not advised, you could skip the verification steps using the multimeter and rely on the verification that I perform. I strongly discourage you from doing this though as the multimeter is your best tool in protecting your other equipment from being damaged by verifying voltage levels. It's also probably the most important tool in your hardware hacking toolkit moving forwards. If you would like to purchase another multimeter or already have one, any multimeter that can perform DC voltage reading and has a continuity tester setting will work. 

**Links to Purchase:**

Link 1: https://www.amazon.com/AstroAI-Digital-Multimeter-Voltage-Tester/dp/B01ISAMUA6

Link 2: https://www.astroai.com/digital-multimeter-2000-counts-am33d/ap/100071

## Logic Analyzer: Comidox USB Logic Analyzer

**Where this is used:** The logic analyzer is used to sniff and capture both UART and SPI communications taking place on the router PCB. 

**Alternative to purchasing:** If you don't purchase the logic analyzer you can still do the majority of the lessons involving it as I will post links to the captures that I take and you will be able to then analyze them the same as if you took them yourself. If you're trying to save some money on tools to buy then this is one I'd recommend skipping. 

**Links to purchase**: 

Note that you can get these logic analyzers from multiple different manufacturers and they all look very similar and usually function identically with the only difference being the sticker applied to the top. The exact one I've used in the course is linked first. 

Link 1: https://www.amazon.com/Comidox-Analyzer-Device-Channel-Arduino/dp/B07KW445DJ

Link 2: https://www.aliexpress.com/item/1005003375736481.html

Link 3: https://www.amazon.com/HiLetgo-Analyzer-Ferrite-Channel-Arduino/dp/B077LSG5P2

## Flash ROM Programmer: ch341a USB Programmer

**Where this is used:** The flash ROM programmer is used to extract the firmware from the device. 

**Alternative to purchasing:** If you don't purchase the flash programmer then you can use the firmware that is downloadable from the TP-Link support website for the router and use that instead to perform the firmware analysis. 

**Links to purchase**: 

Note that you can get these flash programmers from multiple different manufacturers and they all look very similar and usually function identically make sure you get one that uses the ch341a chip. I've linked below to the one that I used in the course. 

Link 1: https://www.amazon.com/KeeYees-SOIC8-EEPROM-CH341A-Programmer/dp/B07SHSL9X9

Link 2: https://www.amazon.com/Geekstory-CH341A-EEPROM-Programmer-Module/dp/B098DYJ3LQ

Link 3: https://www.aliexpress.com/item/32793476447.html

# Optional:

## Spudger Set

Link: https://www.amazon.com/STREBITO-Spudger-Ultimate-Computer-Electronics/dp/B0BHPC2WB5

## Soldering Station: Weller WLC100

Link: https://www.amazon.com/Weller-Digital-Soldering-Station-WLC100/dp/B000AS28UC

## ESD Mat

Link: https://www.amazon.ca/Anti-Static-Electronic-Wristband-Grounding-HPFIX/dp/B07X7VL7VR

## Third-Hand

Link: https://www.amazon.com/Helping-Soldering-Workshop-Non-slip-Weighted/dp/B07MDKXNPC

## Test Clips

Style 1 Link: https://www.amazon.com/Tegg-Electrical-Testing-Multimeter-Grabber/dp/B07NY73PQF

Style 2 Link: https://www.amazon.com/Adapter-oscilloscope-multimeter-Generator-Programmer/dp/B07XNQ8CQW

## Extra Jumper Wires

Link: https://www.amazon.com/Elegoo-EL-CP-004-Multicolored-Breadboard-arduino/dp/B01EV70C78

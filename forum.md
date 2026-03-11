Cafe Husky
 
Forums 
What's new 
Members 
Log inRegister
New posts
4 Stroke Husqvarna Motorcycles Made In Italy - About 1989 to 2014
TE = 4st Enduro & TC = 4st Cross

Hi everyone,
As you all know, Coffee (Dean) passed away a couple of years ago. I am Dean's ex-wife's husband and happen to have spent my career in tech. Over the years, I occasionally helped Dean with various tech issues.

When he passed, I worked with his kids to gather the necessary credentials to keep this site running. Since then (and for however long they worked with Coffee), Woodschick and Dirtdame have been maintaining the site and covering the costs. Without their hard work and financial support, CafeHusky would have been lost.

Over the past couple of weeks, I’ve been working to migrate the site to a free cloud compute instance so that Woodschick and Dirtdame no longer have to fund it. At the same time, I’ve updated the site to a current version of XenForo (the discussion software it runs on). The previous version was outdated and no longer supported.

Unfortunately, the new software version doesn’t support importing the old site’s styles, so for now, you’ll see the XenForo default style. This may change over time.

Coffee didn’t document the work he did on the site, so I’ve been digging through the old setup to understand how everything was running. There may still be things I’ve missed. One known issue is that email functionality is not yet working on the new site, but I hope to resolve this over time.

Thanks for your patience and support!

Husqvarna Motorcycles Husqvarna Motorcycles - Italy 4 Stroke 
449/511 communication with ECU
 Thread starterR. Stephen  Start dateJan 21, 2014
Prev  
1
2
3
4
…
10
  Next
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
Feb 24, 2015
#21
The Keihin ECU is mappable, just that BMW decided to lock it behind a password unlike the Japs (Yamaha, Honda etc)

Tinken said:
The software you have, is it a disk and key or just a folder copy?

The file I have has a key.
gobtald
Husqvarna
AA Class
May 10, 2015
#22
Dangermouse449 said:
Mr. Stephen,

Old thread I know, but did you have any luck talking to the K-line through the diagnosis plug??
I have a copy of the HST software but not the hardware (HVA box & leads).
Wondering if you found any adapters that worked for you?


I have HW/ECU (CCM GP450, TE 499 engine) in it. Can you share your HST SW with me. I'd like to try it with my ECU, with a KKL (FTDI, USB 2 ODBII) interface (if it possible at all).
Normann
Normann
Husqvarna
AA Class
May 11, 2015
#23
gobtald said:
I have HW/ECU (CCM GP450, TE 499 engine) in it. Can you share your HST SW with me. I'd like to try it with my ECU, with a KKL (FTDI, USB 2 ODBII) interface (if it possible at all).

You need BMW GS-911 tool for communication with HVA Keihin adapter.
http://www.hexcode.co.za/products/gs-911/support/faq?full=1
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
May 13, 2015
#24
Does that work Norman?
Normann
Normann
Husqvarna
AA Class
May 13, 2015
#25
Dangermouse449 said:
Does that work Norman?

I don't know about HVA, but it works with G450X (Keihin ECU is same).
Like
Reactions:
Dangermouse449
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
May 13, 2015
#26
Different (round) plug but I guess that could be changed. Interesting :)
Normann
Normann
Husqvarna
AA Class
May 13, 2015
#27
I wrote you about it earlier. Do you remember?
Change plug or use adapter. Protocols are same, not ODBII.
Like
Reactions:
Dangermouse449
gobtald
Husqvarna
AA Class
Jul 12, 2015
#28
Dangermouse449 said:
Mr. Stephen,

Old thread I know, but did you have any luck talking to the K-line through the diagnosis plug??
I have a copy of the HST software but not the hardware (HVA box & leads).
Wondering if you found any adapters that worked for you?


Yes I did. Although my bike is not a Husquarna one but it has the same engine (BMW G450X). It is the very new CCM GP450 (chassis number 37), but I'm absolutely sure it has the same Keihin ECU. Now I'm successfully using that good old ELM327 (pictures in earlier post) but my solution works with any USB to 12V level converter e.g. VAG 409 cable as well. I'm using ELM327 because it is convenient (I don't need to care about headers, checksums, init sequences) and also it is the cheapest diagnostic interface on ebay. It has bluetooth and wifi interfaces so can be accessed from many devices, like tablets and mobile phones as well. There are many bullshits (e.g. around GS-911 and other devices) about that the new bikes needs diagnostic interfaces with newer chips built in. They don't. Aftermarket diagnostic tools are building tricky HW only to save their interests, but the standard K-Line (even most new CAN devices) using KWP2000 protocol needs only simple serial communication.
.
There were many tricks to solve and was taking several weeks but finally I've jailbroken into my/our 449's ECU.

First I needed to understand the low level physical serial protocol, so I should have been traced the K-Line with a protocol/logic analyser. But they are expensive instruments, so I had rather built a software oscilloscope running on a Raspberry Pi computer. Honestly I found such a software on the web but in a very early development phase, moreover I should have modified its code to be able to run on new Raspberry Pi2 devices. I learned that the serial protocol was really a KWP2000 protocol, but -- and this was my first important finding -- it used non standard, but BMW specific address for the ECU. Standard or default setup of ELM327 follows the general OBD2 addressing 0x33 but BMW uses 0x12 for the address of 449's ECU, and the standard 0xF1 for the tester device/program. From that time I was able to communicate with 499's ECU successfully but with a very limited command set and based on that experience I was also be able to use a software USB monitor -- much easier than my earlier software oscilloscope based primitive protocol analyser program -- and progressing faster.

I hoped that I would find a quick solution and tried many freeware (e.g. TuneEcu) and not so freeware but "accessible" (e.g. BMW Rheingold) PC based diagnostic software. I had monitored the communication between the ECU and those SWs. I hoped if I was able to understand and modify their low level protocols and substitute my previously found addresses, I would have saved time and could use their general functions and graphical user interface. But it revealed that it would have been a long and risky journey. BMW software always started by identifying the ECU, so if it did not get ECU specific footprints it dropped the communication. TuneEcu was the most promissing. It was sending familiar OBD commands but in a very early phase it tried to authenticate into the ECU, which was never successful. So it was my second and most difficult task to jailbreak the ECU authentication.

Fortunately I found some information chips in BMW Rheingold software environment, called EDIABAS. There were compiled ECU interface files (.prg) in C:\EDIABAS\ECU folder. BMW G450X's .prg file was mrkmsk16.prg. The 449's ECU is a K16 (KMS K16) ECU. mr... at the beginning of the file name means Motor Rad:) This is the file what all BMW diagnostic software uses to access to a specific ECU. I supposed that this file should have incorporated every know-how between the general diagnostic logic and the specific ECU behaviour. So I needed to crack it or jailbreak into it. I've been browsing several days for more information or tools to get closer to this file format. Finally and thanks for the Providence I found -- by totally chance -- a decompiler for this file. The PRG files are written by BMW specific programming language called BEST. However can you imagine what can you find if you write this word "BEST" into Google? So it was a real challenge how could I phrase my searching topic. I've been subscribing dozens of forums, scanning hundreds and hundreds pages and -- by really totally chance -- something caught my eyes: BESTDIS. But it was only a question of milliseconds not to step forward and miss/lose it. As turned out it was a decompiler for these PRG files written by tacotruck a member of bimmerboost.com. He published its source code as well (http://www.bimmerboost.com/showthread.php?53335-BEST-Disassembler-for-PRG-files). Thank you tacotrack. Without this tool my jailbreak would have been much longer. But it was not so easy even with this very useful tool.

tacotec's BESTDIS program decompiles only to an interim assembler code not to the high level BEST language source code. So with the help of this tool I got a machine assembler code from my mrkmsk16.prg named mrkmsk16.b1v (.b1v format). At least this file could have been be read in a very low machine code level. But the headers of the functions/subroutines or JOBs (in BMW EDIABAS or BEST terminology) contained nearly every information about all the ECU functions and their calling parameters. Wooww, it was already something:) The know-how even in this very low level was open. I should have only needed to authenticate into the ECU in order to use these information.

I had quickly found the authentication JOB/function but it was written by that ugly decompiled assembler code. I knew that the secret clue was there, in that particular JOB/function. So I had started a painful reverse engineering procedure. I should have learnt BMW ugly BEST programming language. Then I did the following procedure repeatedly for days and days: wrote a line of BEST language code, compiled it, then compared its output to the assembler code my mrkmsk16.b1v file (disassembled by BESTDIS decompiler from mrkmsk16.prg). If there was some difference I tried again. Practically I was playing a human software compiler engine between BEST assembler and BEST source code format. Finally I had almost totally learned how the BEST compiler compiles its source file making its interim assembler format. It was a lifetime experience:)

Finally I had decrypted and made the "average human" readable BEST language source code of the important authentication function. BMW uses two access level for communicating 449's ECU. The first one is the standard level. On this level there is only limited number of functions and queries working, like asking VIN number, HW manufacturer number, part number, etc. All useful information are behind the second access level called security level. There are two keys for these two level. These "secret keys" are coded into the program. They cannot identifiable since they are compiled in two phases into the PRG file. Since I had already reverse engineered I can publish these BMW codes now. Based on them you can write a diagnostic software for BMW G450X (and kill some part of the market of GS-911 and others payable aftermarket BMW diagnostic SW). They are 0x5106 for level 1 and 0x1923 for secure level2. But -- as it turned out later -- they are working only for BMW G450's ECU and is not working for my (our) 449's ECU. I think Keihin was asked by BMW to changed them. It is the second magic obstacle why any type of existing BMW or 3rd party diagnostic softwares are not working with our ECU. These softwares and tools are using these keys above and can only access to BMW G450x ECU. The standard OBD2 devices with their standard settings/setup are also not able to authenticate to our 449's ECU.

However there were a third secret in the reverse engineered authentication function. Authentication works as follows: diagnostic program asks a so called SEED from the ECU. SEED is a random two bytes integer. Diagnostic program put this SEED into its internal algorithm/transformation and the result of this transformation (like a dynamic password) is answered/sent back to the ECU. it is the authentication itself. This secret transformation uses those secret keys to generate its result (password). So it is not enough to know the secret keys, I need to know the secret algorithm/transformation using these secret keys. Based on the previous reverse engineering I learned these algorithm/transformation as well. It was not so complicated. At the beginning of reverse engineering I hoped that it would not be a "non reversible RSA algorithm", since these old ECUs computing capacity was quite limited. Decrypted transformation method is the following: 1/ get the SEED (2 bytes), 2/ multiply it with the KEY (2 Bytes), 3/ it gives 4 bytes result, 4/ get the modulo 0x10000 of the previous result (2 byte). Sumarizing SEED x KEY then get the lover 2 byte of the result. It is really simple, as I hoped.

So I had the secret algorithm/transformation itself but I knew only the official BMW secret keys and did not know he new (changed) secret keys for my (our) 449's ECU. What could have been I doing? I wrote a program running also on my Raspberry PI2 which periodically asked a new SEED (pls remember SEEDs are generated randomly by the ECU), then responded always with the same fixed answer to the ECU. I wanted to find a successful "SEED - answer pair" from which I could easily decrypt the secret KEY based on my known secret algorithm/tranformation.

This was a classical brute force algorithm. But those smart BMW/Keihin engineers tried to avoid this. So they put a 10 seconds waiting time (timeout) between the valid SEED request. If you asked a new SEED more frequently you got an error. So I needed to wait exactly ten second between every SEED request and answer. There are 65536 possible variations of SEED-answer pairs. So in a worst case situation I would find a successful SEED-answer pair in 65536*10sec=7.5 days. I got the first successful SEED-answer pair at the 29.934 attempts and the second, the most important one at 32.894 attempts. So it took about one week altogether.

Meantime I built my Rasberry PI2 computer fixed into my bike. After all we are in the era of IOT (Internet of Things). What else could be a REAL THING than a motorcycle. From that time I have been using the built in computer of my bike for many purposes: scanning, sending and saving ECU parameters, popping potential fault code immediately. E.g. till now we have been missing the RPM and Engine temperature gauges and warning lamps from our dashboard, but now I already have the RPM and Engine Temperature values on the display of my ruggedised tablet fixed behind my windscreen. I'm also continuously saving my GPS coordinates in every 10 seconds onto a connected USB drive in a .GPX format. It is for historical purposes, like a black box on airplanes. USB drive can contain data of years and I don't need to care about this function, it is started when I switch the ignition on, and totally automatic. If I need to know where I was 3 months ago, I can plug out the USB drive from my motorcycle and plug it into any map software and I can see it precisely.

So my bike (fitted with this intelligence) staying in my garage, connecting any available wifi around it, this case it connects to the wifi of my house, running that SEED-answer pair looking brute force program on her own. Finally my motorcycle had sent an email (after 3 then another 3 days) to me when it found the successful SEED-answer pairs in its ECU. It was a real experience when I got an email from my motorcycle and read: "My master, I've found a good SEED-answer key for you. BR your bike" :)


Then based on these successful SEED-answer pairs I decrypted the two secret keys from the secret algorithm/transformation (described above). These are the authentication keys of my (our) 449's ECU: 0x6AD5 for level 1 and 0x1EC3 for secure level 2. Practically only the second one needed, since level 1 is the initial default level of ECU.

Then I quickly tried to ask RPM value, Coolant and Air Temperatures, the famous Throttle Position Voltage (in the future you don't need that diagnostic hooking cable for tuning throttle positions and shifting the whole fuel map), Battery voltage, etc., etc. Everything was working perfectly and there were lots of other parameters/values to query and actuator tests to run. As the most important all these stuffs are working on the very simple, old and almost forgotten, extremely cheap ELM327 or any USB/WiFi/BT and 12V Serial converter.

I think it was the tricky part of the job. But the longer part is yet to come. Now everything is working on very low level, not so user friendly, strange ASCII commands entered into terminal windows and the resulting values should also be interpreted. But it is working very well. However it surely needs a more convenient graphical user interface. But in boring development of that user interface program for e.g. a bluetooth connected Android or other platforms I'm not so interested. I thought that I will send these results to TuneEcu programers. They had exactly what I'm missing. All the user interface stuff, most of the standard ECU test algorithms. Building only these new simple authentication algorithm and the found keys into their program wouldn't be a big challenge for them. So they can easily expand their portfolio for our bikes (BMW G450x, Husquarna 449, CCM GP450).

My only concern on these Husky forum whether my decoded authentication keys are really valid for your 449? As it turned out mine is different from BMW and I only suppose that ours (as not original BMW) should be the same. But I cannot try it, since I have no Husquarna bike. However what is absolutely certain that our ECU's HW have the same, authentication methods, so all these information are valid for your 449's ECU. If the secret key would be different based on these information some of you can safely run my really very stupid brute force algorithm and find your secret keys for your authentication.

In my next post I want to share as many concrete decoded ELM327 command sequence as I can with as much explaining info about them as I can. I'm rooting that our ECUs share the same secret keys and you can use those commands and their results immediately.

(sorry for my English)
Like
Reactions:
daddyrat, Big Timmy, Shovelhead85 and 5 others
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
Jul 12, 2015
#29
Gobtald,
I take my hat off to you.
That is a great job. I'd like to message you when I have some time, I may have some files you'd like to look at :)
(Norman knows which ones I mean :) )
Most of the detail from your post is more than I'm aware of, but I understand the basics & aplaude you for sticking with it when nobody else has.
A user tunable ecu software system would be a great thing for many.
Like
Reactions:
Normann
Lon
Lon
Husqvarna
AA Class
Jul 13, 2015
#30
I wonder how much "real" difference there is in the ECU from a 449 and a 511 ;)
Huskynoobee
Huskynoobee
CH Sponsor ZipTy Racing
Staff member
Jul 13, 2015
#31
Gobtald, you have really been working hard on this and those of us with locked ECU units are following!
Like
Reactions:
Dangermouse449
domrvt
domrvt
Husqvarna
AA Class
Jul 13, 2015
#32
Wow, great work. I've got an ELM327, Raspberry Pi, and 449 ECU. I'd love to help out!
Like
Reactions:
Dangermouse449
Shovelhead85
Shovelhead85
Husqvarna
AA Class
Jul 13, 2015
#33
gobtald-

I am amazed at the time & effort you put into this (6 days for a brute force search w/ 10 secs between attempts! on a Raspberry Pi over Wifi- wow. What- do you work at Budapest House or a NSA listening station? impressive:applause: )

Thanks for the effort. ...and I hope you get a Husky (or at least an ECU. Hey, do other Husky's Keihin ECUs use the same algorithm I wonder? Wow- BMW did NOT want anybody to get into that thing.)

Your english is excellent BTW.
Cosmokenney
Cosmokenney
Husqvarna
Pro Class
Jul 14, 2015
#34
gobtald said:
Yes I did.
gobtald, can you write values to the ECU or just read them? My first thought while reading this is I wonder if you can write a different target Air Fuel Ratio that the ECU tries to achieve using the stock O2 sensor?? That would be revolutionary.
gobtald
Husqvarna
AA Class
Jul 14, 2015
#35
Cosmokenney said:
gobtald, can you write values to the ECU or just read them? My first thought while reading this is I wonder if you can write a different target Air Fuel Ratio that the ECU tries to achieve using the stock O2 sensor?? That would be revolutionary.


First of all please don't over-estimate my skills !!! :)

Basically what I've achieved was discovering all functions of our 449's ECU and jailbreaking its authentication. I thought this was the foundation of all further opportunities.

Now I (we) have complete functions and parameters list from that BMW interface file (EDIABAS' PRG file) which contains all functionalities what BMW/Keihin planed into its/our ECU. But in the last couple of days I've only tried around half of them. Only those ones which I was interested in. Here is an example: although I have found many functions around flashing ECU, but I was not interested in modifying ECU's fuel map or other parameters. But I'm sure those functions can do it. Moreover I have not enough information YET about proper format of 449 specific fuel maps, proper addresses of these fuel maps inside the ECU where I should flash them into. But there should be many people who has much better skills than me regarding general ECU architecture. And based on these skills after passing authentication phase he/she can easily flash those fuel maps.

I'm sure that TuneEcu programmers have definitely much deeper knowledge how can these types of ECUs be re-flashed or modified. I think it is very similar to KTM's or Triumph's Keihin ECUs which they can currently manage and support. They need only that simple but hidden before, finally decrypted authentication method and those secret keys, then they can easily built them into their codes, then we can use all of their functionalities. Dangermouse449 also mentioned earlier that he has the Husquarna HST software. It can be another software we should try to "patch", replacing only its authentication method, hence bypassing its dependency from its specific diagnostic HW, then happily using all of its functionalities. I don't want to reinvent what others know much better than me. I wanted to find only the clues into the lock.

My original goals were very simple and low-key: getting only realtime data from ECU like our very needed RPM and Engine temperature values. Then all the functions what dealers are using in its trouble-finding and service/maintenance activities: reading and clearing DTC codes, testing (switching on/off) actuators like fuel pump or oxygen sensor heating, testing whether injector works, reading TPS voltage in order to tune its position, then deleting/reseting lambda adaptation values, etc, etc. All those operations where Workshop Manual redirects/send us to the factory diagnostic devices and procedure. I've already achieved all these goals. I've been successfully trying all functions what GS-911 offers (http://www.hexcode.co.za/products/gs-911/kmsk) even much more. So we have already saved 260 GBP (it is the ebay price of the GS-911 without BT or WIFI). OK if I want to be fair it is not comparable with my low level and strange ELM327 command line sequences. But for me and I think for many others this solution is even more flexible and better value. This is so much low-level that anybody can build their functions and programs on top of it. I'd have liked to use my ECU's real-time data on my on-board tablet. How I was able to dig out those data from GS-911 application and put some of them -- in which I'm most interested at that particular moment -- onto my tablet's screen, e.g at the bottom right corner of my running Navigation application screen. Now I wrote a 100 lines Python script for my Raspberry Pi built in my bike and send those data to my Android tablet (via bluetooth, USB or even WiFi during my journey) fitted behind my windscreen. It was precisely what I needed, not more.

Brief answer for your question. I don't know whether with those functions I found you/we can write different target Air Fuel Ratio, but if it is possible at all, we can/will. It depends on the ECU architecture (which I don't know enough YET) but for this architecture we have really all access functions which was programmed and interfaced for the external professionals by BMW/Keihin. We have functions called ReadMemoryByAddress, WriteMemoryByAddress for any internal ECU variables, and not only Read/Write Data By Global/LocalIdentifier. However I don't know YET whether ECU architecture allows to write this ratio directly and what is the address of the variable of this ratio. Here is another example: I have a function called STATUS_DROSSELKLAPPENWINKEL_2_SOLLWERT (those beautiful german function names:) which means "read value of 2nd throttle target angle" which gives back a 0-80 degrees value of the stepper motor of second throttle valve. I suppose we can overwrite this value provoking richer air/fuel mix but don't hurt the ECU internal architecture and its working logic, risking collapsing ECU and making accident on the road. But I don't understand YET how this value exactly influences your Air Fuel Ratio. So it is why I told: I have not enough information so I'm not smart enough YET.

I can only repeat, please don't over-estimate my skills and our achievements. I want to be familiar with this ECU architecture deeper and deeper (I'm and we are in the beginning of this journey), but I don't want to write software like TuneEcu for all popular operating systems. Moreover definitely don't want to jailbreak or reprogram our ECU internal software architecture. If Air Fuel Ratio can be modified or influenced via standard factory functions -- although I don't interested in performance tuning -- I will find for you how it can be, if it is against the ECU architecture I don't want to hack it.

I'm not a hacker, I only want to maintain my bike totally on my own and don't want to depend on unashamed expensive but "not so talented": BMW or other dealers. I have a CCM bike equipped with this ECU, living 2200 km far from my bike manufacturer which is resident in Bolton UK. They have no dealer/service network in my country or even minimal in Europe. So I wanted to because I should prepare for every electronic and maintenance issues of my bike. For all mechanic ones I hope I'm experienced enough, and got perfect "remote support" from CCM. So I simply needed "to tick" the ability to access to the electronic features of my new bike as well. That's all.

I hope I did not make you confused (e.g. with my poor English) and bitter.

I'm going to back typing my post about those funny ELM327 commands and functions, sharing my findings with your husky community, and involving as many of you as possible. Then based on those info I collect I want to encourage all of you to get further then I am/was able to.

gobftald
Like
Reactions:
Big Timmy, Cosmokenney and Dangermouse449
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
Jul 14, 2015
#36
Cosmokenney said:
gobtald, can you write values to the ECU or just read them? My first thought while reading this is I wonder if you can write a different target Air Fuel Ratio that the ECU tries to achieve using the stock O2 sensor?? That would be revolutionary.


It might be possible in theory, but the original O2 sensor is a narrow band sensor. You would need a wideband sensor for that to work & a probably a heap of coding.....
Like
Reactions:
Normann
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
Jul 14, 2015
#37
gobtald said:
First of all please don't over-estimate my skills !!! :)

Basically what I've achieved was discovering all functions of our 449's ECU and jailbreaking its authentication. I thought this was the foundation of all further opportunities.


I hope I did not make you confused (e.g. with my poor English) and bitter.

I'm going to back typing my post about those ELM327 commands and functions, sharing my findings with your husky community, and involving as many of you as possible. Then based on those info I want to encourage all of you to get further then I am/was able to.

gobftald
Click to expand...


Gobtald,
Please don't under-estimate yourself.:)
What you have done is very clever & time consuming.
It will benefit us all to have even just real-time information from sensors & code reading.
The dealers are becoming harder to find & the HST system will become unsupported.

Thank you for your efforts so far**************************************** :applause::thumbsup:
gobtald
Husqvarna
AA Class
Jul 15, 2015
#38
As I promised now I publish -- or rather started to publish -- my raw ELM327 command sentences and their descriptions in order to encourage you to try them and confirm whether they working on husky 449 or may be 511 as well. If not, please let's try to jailbreak into them with my simple brute force algorithm founding those possible different secret keys for authentication for your husky ECU and for future use.

I suppose the first two steps to access your ECU via ELM327 are the initial intelligence tests for anybody.

1/ You should connect "somehow" ELM327 OBD connector to your 449 diagnostic interface. It is a quite trivial job, described many places all around the web. I have not checked that but maybe somewhere in this cafehusky forum as well. For the sake of completeness I repeat it briefly: You should connect 3 wires, GND, BATTERY 12V and K-LINE of ELM327 OBD2 connector to the same pins of 449' diagnostic connector. For OBD2 connector pls see https://en.wikipedia.org/wiki/On-board_diagnostics (GND = pin 4 and 5, BATTERY 12V = pin 16, K-LINE = pin 7. For the 449's (and also for my CCM GP450') diagnostic connector -- from front view of the diagnostic connector (with release button up) --: GND = bottom middle pin, BATTERY 12V = bottom right pin, K-LINE = top left pin. You can make any type of connection. I made a very elegant one, buying the proper male pair of the diagnostic connector, with plastic inserts and those 3 pins. Because it was a bit special connector I think it was the most expensive part of my full HW investment, since ELM327 was much cheaper than this small plastic gadget.

2/ You can use any type of terminal emulator or terminal program of any type of operating system. Old Windows has "Hyperterminal". OSX Mac, Android, iPhone, Raspberry Pi, as UNIX/Linux machines have the standard "Terminal" application on which you can run the "screen" command line program with the relevant USB device and with 38400 baudrate. On my Macbook this command is "screen /dev/ttyUSB0 38400", on my Raspberry Pi this command is "screen /dev/cu.usbserial 38400". The potential tricky part of this job to install proper FTDI USB-Serial driver (http://www.ftdichip.com/FTDrivers.htm) for these programs, if it has not been already available. This is also very well documented all around the web. My Mac and Raspberry Pi has this driver by default.

ELM237 documentation is available on the following link: http://elmelectronics.com/DSheets/ELM327DS.pdf

After these necessary steps above as a starting point I suppose you get somehow to the ">" prompt of ELM327. So let's start the game. Commands bolded are the commands you should type in. Repeated non-bold parts of the commands are for description purposes. Texts after # are my descriptions. Request (command) and its response indicated by "req", "resp". Spaces between characters is not necessary. But I will put spaces into the commands for better readability. 0x sign before numbers in my description means that it is a hexadecimal number. BTW all data in commands and answers are hexadecimal

req
ATZ # reset ELM327
resp
OK

req
ATL1 # switch LF (line feed) on - after reset ELM327 responses in the same line in which we typed, it could be disturbing, with this command we switched on the normal mode
# getting the responses in the next line
resp
OK

req
AT WM 82 12 F1 3E 01 # set wakeup or "heart beat" message - during connection it will be sent by ELM327 in a frequency defined later, in order to maintain the
# communication with the ECU

WM # Wake up Message, the following five bytes are the "wake up message" itself, which will be sent by ELM327 in the predefined frequency
82 # first 2 bits (8) means we use physical addressing in the communication, the last 6 bits (2) gives the length of the message, after the address bytes
12 # ECU address (it was my first finding, because it is BMW/Keihin specific for our 449's ECU
F1 # Test program/device address (address of ELM327) # ECU use this address in its answers
# the following 2 bytes are the content of the message
3E # testerPresent function code/ID - it means: "I'm living, please don't disconnect":)
01 # I'm waiting for an answer for my request (based on KWP2000 specification 02 would mean: "don't need answer", but it does not work with our ECU
resp
OK

req
AT SW C8 # set wake up frequency to 4000 ms (4 sec) - so ELM327 will send the previously defined "wake up" message in every 4 sec

SW # Set Wake up
C8 # C8 = hexadecimal value (all values in commands are hexadecimal) of frequency
# C8 = 200 in decimal - we can set wake up frequency by 20 msec increment, so 200x20 msec = 4 sec
resp
OK

req
AT SH 81 12 F1

SH # set header
81 # 8 = we will using physical addresses, 1 = length of message value is placed into the first byte of header
12 # ECU address
F1 # test program/device address (address of ELM327) -- from now these addresses will be used constantly in all further communication
# ELM327 will insert these header bytes/addresses automatically at the beginning of our sent messages
resp
OK

req
AT FI # Fast Init - it is the HW initialisation command, making serial line connection between ECU and ELM327
resp
BUS INIT: OK # hardware or serial line or K-LINE connection to our ECU is OK
# if we get BUS INIT: ERROR message something went wrong (e.g. we have forgot to connect ELM327 and ECU or the physical connection is wrong) OR:

Mostly the problem is that our ECU is "sleeping" or more precisely it had switched off itself. So they cannot respond to this initialisation command. This is typical for our BMW or Husky 449 or CCM 450 (449) motorcycle. You should have been experienced that when you switched off ignition after several seconds you can hear two noises. The first one came from the stepping motor in throttle body/house, then later a relay is switched off. This relay gives power to our ECU. And this relay is controlled by the ECU. So our ECU is able to switch off its own power so it is able to put itself in "sleep mode". When ignition is switched on, this relay is not switched on yet. So our ECU cannot get power yet. Only the starter relay/motor will switch on this relay and as a consequence switch on our ECU. So, how can you switch on the ECU and communicate/diagnose it without starting the engine. You should push the starter button very briefly. Don't start the engine but only push the button shortly. It gives power to the ECU but don't start the engine. But after that you should type the AT FI command quickly since there is a timing (around half minute) when ECU will switch off itself again. Naturally if you started and your engine is running the ECU will work normally and yo don't need to hurry:)

After "AT FI" command we've finished the initial "AT" commands (pervious commands beginning with AT are all for ELM327). They were for initial setup purposes. From that time our commands (without AT) will be sent to our ECU (of course via ELM327). In the background ELM327 does its job, puts header bytes, addresses and also checksum to my commands but it manages this automatically. We don't need to care about these details. It is convenient compared to other USB-Serial K-Line interface like VAG 409 cable, for which we need to manage, namely type and send that "message frame bytes" like header, addresses, checksum on our own. It is not a big deal from a program, but inconvenient to calculate and type them every time in every command by hand.

After the succcesful "BUS INIIALISATION" between ELM327 and our ECU, the connection is living. The heart beat messages are automatically sent by ELM327 in every 4 seconds -- you can see it when the leds on ELM327 are flashing -- so communication will not be dropped by ECU. We can send commands to ECU via this maintained communication channel:

req
81 # startCommunication function -- start of diagnostic session
resp
C1 5B 8F # "keyword answer"

# 0xC1 means successful answer for 81 request -- ECU signals OK answer in such a way that it adds 0x40 (hexadecimal 40) to the first -- called -- function byte
# (this case this function byte was 0x81, so 0x81+0x40=0xC1 which means OK for 0x81 function)
# negative answer signalled by an initial 7F byte, then the repeated function byte, then error description byte about the nature of the error (see examples below)
5B 8F # keyword - it is the expectation/specification from ECU what communication parameters it wants to use -- you don't need to care about it
# for professionals: 5B 8F means: 1/ both format byte and additional length byte is possible, 2/ header with target and source addresses, 3/ extended timing

After that command we are in the default access mode, we can ask some basic information from ECU. But let's make authentication and step into the secure access level

req
27 03 # authentication seed request

# 0x27 = authentication function
03 # parameter of authentication function -- 0x03="seed request for access level 2"
resp
67 03 CC 09 # positive response for 0x27 authentication (0x27+0x40=0x67)

03 # OK response always repeats the parameter of the request, in this case it was 0x03
CC 09 # it is the two byte SEED, generated randomly by the ECU, and given us as a response for the previous SEED request
# since we always get random numbers for every request, it is nearly impossible that you get the same bytes which are in this example:)
# this is the number -- what you really got -- which should be substituted into the next authentication calculation

Here comes the "magic" calculation of the answer (password) based on the secret key for access level 2 and using the authentication algorithm/transformation. If we are able to give a correct answer, ECU will let us enter into its secure level. The secret key -- I hope it is not only for my CCM's, but also for your husky 449's ECU -- is the mentioned 0x1EC3 for secure level 2. The transformation is (SEED * 0x1EC3)%0x10000. You need a hexadecimal calculator to calculate directly or convert all numbers into decimal, make calculation, then convert the result back to hexadecimal.
Hexadecimal calculation: 0xCC09*0x1EC3=0x188478DB, then 0x188478DB%0x10000=0x78DB, the lower 16 bit part of the result.
If you have no other possibilities for decimal calculation open an Excel table and use HEX2DEC and DEC2HEX functions, and also Excel % (modulo operator).

In our case/example we've calculated our magic response = 0x78DB which should be sent back as answer/password to the ECU.

req
27 04 78 DB # authentication response

# 0x27 = authentication function
04 # parameter of authentication function -- 0x04="response for access level 2"
78 DB # our calculated answer for ECU, it is our dynamic password for authenticate ourself for accessing secure level 2
resp
67 04 # positive authentication response
# positive response for 0x27 request (0x27+0x40=0x67)
04 # OK response always repeats the parameter of the requested function, in this case it was 0x04

In case of error when ECU don't accept our authentication we can got the following error messages:

resp
7F 27 10 # 7F = error in a previous command
27 # it was the 0x27 authentication function where this error occured
10 # 0x10 means GENERAL_ERROR, which means that ECU cannot accept our responses/password

or
resp
7F 27 37 # 7F = error in a previous command
27 # it was the 0x27 authentication function where this error occured
37 # 0x37 means ERROR_TIME_DELAY_NOT EXPIRED, which means that we've tried to send/repeat answer/password in less than 10 sec

So Guys, if somebody got that 67 04 answer, it means that his/her ECU accepted the password. in this case we have win :). Your husky ECU use the same -- non BMW -- secret key for authentication as my CCM GP450. After this you/we can access all diagnostic and other features of your/our ECU. If you get 7F 27 10 error message, ECU refused your password. There are 3 possibilities: 1 / secret key was OK, but your calculation was false, let's try again, 2/ some time ECU is busy to deal with your request it is why it refuses, let's try again, 3/ secret key is different from CCM changed secret key for the same type of ECU. In this case please try to substitute BMW original secret key (0x1923 instead of 0x1EC3) into the authentication formula. I don't believe but it can be possible that BMW/Keihin did not change the original secret keys for husky's ECU. Please don't give up for the first failure try again and ensure that everything was OK, the password calculation was OK, and you tried it several times.

I assume you were successful. So -- as appetising -- here I tried to document two types of request examples. 1/ with the 0x22 function (ReadDataByCommonIdentifier) we can query many parameters and data. After the 0x22 read function you should specify the identifier of requested data. 2/ with the 0x31 function (StartRoutineByLocalIdentifier) you can make ECU to run its own internal program routines. After the 0x31 run function you should specify the identifier of ECU's internal program routines. BTW these identifiers are the same as in KTM Keihin ECUs.

Let's see some "READ" functions:

req
22 0007 # read BatteryVoltage

# 0x22 = ReadDataByCommonIdentifier function
0007 # identifier of battery voltage -- this is the place where ECU stores the value of current Battery Voltage
resp
62 00 07 00 89 # OK answer for read BatteryVoltage

# OK answer 0x22+0x40=0x62
00 07 # identifier of battery voltage
00 89 # value of current battery voltage
# 0x89 = 137 in decimal
# ECU measure battery voltage in 0.1 V increments, so 137 means that our battery voltage is 13.7 V

req
22 0009 # read engine coolant temperature
# 0x22 = ReadDataByCommonIdentifier function
0009 # identifier of coolant temperature
resp
62 00 09 00 43 # OK answer for read engine coolant temperature

# OK answer 0x22+0x40=0x62
00 09 # identifier of engine coolant temperature
00 43 # value of current engine coolant temperature
# 0x43 = 67 in decimal
# ECU measure engine coolant temperature from -40 degrees, so 67 means that our coolant temperature is 27 degrees

req
22 0001 # read throttle position current angle
# 0x22 = ReadDataByCommonIdentifier function
0001 # identifier of throttle position current angle
resp
62 00 01 00 05 # OK answer for read throttle position current angle

# OK answer 0x22+0x40=0x62
00 01 # identifier of throttle position current angle
00 05 # value of throttle position current angle
# 0x05 = 5 in decimal
# ECU measures the position of throttle from 0 deg to 80 deg on its scale from 0x00 (0) to 0xFF (255).
# So you can calculate the degrees: got value * 80 / 255 -> in my case 5 * 80 / 255 = 1.56 deg
# or you can calculate in %: got value * 100 / 255 -> in my case 5 * 100 / 255 = 1.96%

You can play with this value. Rotate grip and push Enter key on your computer many times quickly. If ELM327 got an Enter in an empty command it repeats the previous command then we can see the response. So hitting the enter key quickly during twisting my throttle grip gives the following result:

62 00 01 00 05 -> 1 degree = 1% (rounded)
62 00 01 00 3B -> 18 degrees = 23%
62 00 01 00 6D -> 34 degrees = 42%
62 00 01 00 AC -> 53 degrees = 67%
62 00 01 00 FF -> 80 degrees = 100% = full gas :)
62 00 01 00 05 -> 1 degree = 1%

I will publicate and explain all other possibly queries later

Let's try some "RUN" functions:

req
31 A501 # start injection valve test - injector repeatedly activated, automatically stops after 10 seconds
# 0x31 = StartRoutineByLocalIdentifier
A501 # identifier of start injection valve test
resp
71 A5 01 # OK answer for injection valve test
# OK answer 0x31+0x40=0x71
A5 01 # identifier of start injection valve test
# you can hear the repeated injector activities for 10 seconds

req
31 A700 # start fuel pump relay test - fuel pump really activated for 10 seconds
# 0x31 = StartRoutineByLocalIdentifier
A700 # identifier of start fuel pump relay test
resp
71 A7 00 # OK answer for start fuel pump relay test
# OK answer 0x31+0x40=0x71
A7 00 # identifier of start fuel pump relay test
# you can hear the repeated fuel pump activities for 10 seconds (in shorter intervals in order not to overload the pump)

I will publicate and explain all other possibly actuator tests later.

It was a long post. Sorry about it. I know that it was bit technical, but I hope you enjoyed this:) As I mentioned earlier on top of this inconvenient command usage of ELM327 any middle skilled programmer can build any type of beautiful applications with graphical gauges, instruments, menus, etc. Let's consider it as a test which should have been passed by somebody in your husky community. Since I have no husky or its ECU to try these commands. As we discussed earlier if you have an authentication success, and have jailbroken into your ECU we will find some more user friendly solution for using these feature of our ECU.

If you test it and not working, we need an entrepreneur to whom I can send my stupid brute force test algorithm. It is safe to run. Only it takes some time (may be some days) to find your ECU's secret key. So during this time somebody is missing its bike. Although if he/she build -- e.g. those tiny credit card size -- computers in his/her bike, my program are able to scan ECU during motorcycling as well:)

gobftald
Like
Reactions:
daddyrat, enyone, Big Timmy and 3 others
Dangermouse449
Dangermouse449
Husqvarna
Pro Class
Jul 16, 2015
#39
Wow!!

This may take some time to digest, but it is very much worth pursuing.
Thanks for sharing your information :)
BigBug
Husqvarna
B Class
Sep 21, 2015
#40
Mr. Gotbald

You are amazing ! Thank you for all those that can understand all that stuff. I can about 50 % .
Prev  
1
2
3
4
…
10
  Next
You must log in or register to reply here.
Share:
LinkedIn
Reddit
Pinterest
Tumblr
WhatsApp
Email
Link
Husqvarna Motorcycles Husqvarna Motorcycles - Italy 4 Stroke 
Contact usTerms and rulesPrivacy policyHelpRSS
Community platform by XenForo® © 2010-2024 XenForo Ltd.
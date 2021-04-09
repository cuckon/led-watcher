![](https://img.shields.io/badge/python-3.7%2B-blue)

### Overview
My personal project to play Raspberry Pi 4B.

It uses 3 LEDs and a buzzer to indicate the events you are interested in. Like what's going on about centralized eventlog server, or specific time is being hit.

### Features
- Indicates warnings and errors respectively using *yellow* and *red*.
- *Blue* is for time reminder.
- Identifiable buzzer output for different level of event.
- "Mark as read" button.
- Lights are blinkly turned on, which makes it easy for you to tell which light it is after you hear the beep and head up.
- Utilized purely with `asyncio`. So everything is cocurrent on a single thread.

### Limitations
- As mentioned earlier the whole point of this project is for personal study purpose which means it's not for production.
- The watchers for now are not implemented as plugins & configurations. So if you want to customize the watcher you have to change the code.
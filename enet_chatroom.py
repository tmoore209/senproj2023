from socket_convenience import *
from dataclasses import dataclass
from datetime import datetime
import json
import base64
import time
import curses
import os
import enet
# https://github.com/aresch/pyenet

@dataclass
class Message:
    system:bool
    user:str
    time:datetime
    text:str

    def FromBytes(msg:bytes) -> 'Message':
        msg = json.loads(msg.decode())
        return Message(msg["system"],msg["user"], msg["time"], msg["text"])

class Chatroom:

    def __init__(self, host:enet.Host, peer:enet.Peer, channel:int, username=""):
        self.host = host
        self.peer = peer
        self.channel = channel

        self.localUser = username
        while self.localUser == "":
            self.localUser = input("Enter your name: ").strip()

        self.log = [Message(False, "System", time.gmtime(), f"Welcome to the chat, {self.localUser}! Connecting you now...")]


    def Listen(self) -> None:
        event = self.host.service(0)
        peer = event.peer
        packet = event.packet

        match event.type:
            case enet.EVENT_TYPE_NONE:
                pass

            case enet.EVENT_TYPE_CONNECT:
                self.log.append(Message(False, "System", time.gmtime(), f"You have connected to {peer.address.host, peer.address.port}"))

            case enet.EVENT_TYPE_DISCONNECT:
                self.log.append(Message(False, "System", time.gmtime(), "You have disconnected"))
                exit("Your peer has left")
                
                
            case enet.EVENT_TYPE_RECEIVE:
                message = Message.FromBytes(packet.data)
                if message.system:
                    pass
                else:
                    self.log.append(message)
                


    def Send(self, message:str, system:bool=False) -> None:
        # Create a local copy of the message
        self.log.append(Message(False, self.localUser, time.gmtime(), message))
        # Create a json copy of the message, encoded in utf8, base64
        msg = json.dumps({"system":system, "user": self.localUser, "text":message, "time": time.gmtime()})
        # Send it
        packet = enet.Packet(msg.encode('utf8'), enet.PACKET_FLAG_RELIABLE)
        self.peer.send(self.channel, packet)


    def SendDisconnect(self) -> None:
        self.peer.disconnect()
        self.host.service(0)


    def DrawLogWindow(self) -> None:
        # Clear any rightward junk that wouldn't be overwritten otherwise
        self.logWindow.clear()
        self.logWindow.move(1,1)
        # Only show past 10 messages
        for m in self.log[-10:]:
            # Show black on white for other user's messages,
            # white on black for ours
            rev = curses.A_REVERSE if m.user != self.localUser else 0
            self.logWindow.addstr(f"{m.user}: {m.text}\n ", rev)
        self.logWindow.border()
        self.logWindow.refresh()

    def DrawMessageWindow(self, currentMessage) -> None:
        self.messageWindow.clear()
        self.messageWindow.addstr(1,1, currentMessage)
        self.messageWindow.border()
        self.messageWindow.refresh()


    def main(self, screen) -> None:
        currentMessage = ""
        self.screen = screen

        y, x = screen.getmaxyx()
        self.logWindow  = screen.subwin(y-3, x, 0, 0)
        self.messageWindow  = screen.subwin(3, x, y-3, 0)

        curses.noecho()
        curses.halfdelay(1)

        while True:
            self.Listen()

            try:
                k = screen.getkey()

                match k:
                    case os.linesep:
                        self.Send(currentMessage)
                        currentMessage = ""

                    case "KEY_BACKSPACE":
                        currentMessage = currentMessage [:-1]

                    case _:
                        currentMessage += k

            except curses.error:
                pass
            except (KeyboardInterrupt):
                os.system('stty sane')
                self.SendDisconnect()
                exit()

            self.DrawLogWindow()
            self.DrawMessageWindow(currentMessage)
            curses.doupdate()

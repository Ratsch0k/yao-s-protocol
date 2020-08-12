import rsa
import secrets
import json
import socket
import time
import math
from obviousTransfer import ObviousTransfer

IP = "127.0.0.1"
PORT = 4005
KEYLEN = 256

def stringToNumber(string):
  return int(string.encode("UTF-8").hex(), 16)

def numberToString(number):
  return number.to_bytes(KEYLEN, byteorder="big").decode(encoding="UTF-8")


ot = ObviousTransfer(IP, PORT, KEYLEN)

choice = input("Sender (0) or Receiver(1)? ")

if choice == "0":
  asString = input("Do you want to send a number(0) or a string(1)? ")

  option0 = input("Option 0: ")
  option1 = input("Option 1: ")

  if asString == "1":
    option0 = stringToNumber(option0)
    option1 = stringToNumber(option1)

  ot.send(option0, option1)
elif choice == "1":
  asString = input("Do you want to receive a number(0) or a string(1)? ")

  decision = input("What's your input? ")
  message = ot.choose(decision)

  if asString == "1":
    message = numberToString(message)

  print("Your received the message", message)

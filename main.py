import rsa
import secrets
import json
import socket
import time
import math

IP = "127.0.0.1"
PORT = 4005
KEYLEN = 256
BUFFER = 2048
messageLen = 32

def obviousTransferSender(option0, option1):
  # Generate rsa key
  # PublicKey(n, e)
  (pub, priv) = rsa.newkeys(KEYLEN)

  # Generate two random message for placeholder for real message
  randomMessage0 = secrets.token_hex(messageLen)
  randomMessage1 = secrets.token_hex(messageLen)


  # Create message
  choiceMessage = {
    "key": {
      "N": pub.n,
      "e": pub.e,
    },
    "0": randomMessage0,
    "1": randomMessage1
  }


  # Establish connection to receiver
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.connect((IP, PORT))    
    
  s.send(str.encode(json.dumps(choiceMessage), encoding="UTF-8"))

  data = s.recv(BUFFER)
  v = int(str(data)[2:-1])

  # Generate k values and add to messages
  k_0 = pow(v - int(randomMessage0,base=16), priv.d, mod=priv.n)
  k_1 = pow(v - int(randomMessage1,base=16), priv.d, mod=priv.n)

  # Calcute messages
  mValues = {
    "0": int(option0) + k_0,
    "1": int(option1) + k_1
  }

  s.send(str.encode(json.dumps(mValues), encoding="UTF-8"))

  s.close()

def obviousTransferReceiver(decision):
  if decision != "0" and decision != "1":
    raise Exception("decision has to be either 0 or 1")

  # Establish connection to sender
  s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  s.bind((IP, PORT))
  s.listen(1)

  print("Waiting for start...")

  conn, addr = s.accept()

  # Await options and public key data
  data = conn.recv(BUFFER)

  # Try to deserialize the data
  choice = json.loads(data)


  # Choose random number
  k = int(secrets.token_hex(messageLen), base=16)


  x_b = int(choice[decision], base=16)
  e = int(choice["key"]["e"])
  N = int(choice["key"]["N"])


  # Calculate response
  v = (x_b + k ** e) % N

  # Send v
  conn.send(bytes(str(v), encoding="UTF-8"))

  # Await k values
  data = conn.recv(BUFFER)

  mValues = json.loads(data)

  # Get the m value of the selected input
  m_ = mValues[decision]

  # Get original message from it
  m = m_ - k

  return m

def stringToNumber(string):
  return int(string.encode("UTF-8").hex(), 16)

def numberToString(number):
  print(number)
  return number.to_bytes(KEYLEN, byteorder="big").decode(encoding="UTF-8")

choice = input("Sender (0) or Receiver(1)? ")

if choice == "0":
  asString = input("Do you want to send a number(0) or a string(1)? ")

  option0 = input("Option 0: ")
  option1 = input("Option 1: ")

  if asString == "1":
    option0 = stringToNumber(option0)
    option1 = stringToNumber(option1)

  obviousTransferSender(option0, option1)
elif choice == "1":
  asString = input("Do you want to receive a number(0) or a string(1)? ")

  decision = input("What's your input? ")
  message = obviousTransferReceiver(decision)

  if asString == "1":
    message = numberToString(message)

  print("Your received the message", message)

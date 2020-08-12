import rsa
import secrets
import json
import socket
import time
import math

class ObviousTransfer:
  def __init__(self, ip, port, keylen):
    self.ip = ip
    self.port = port
    self.keylen = keylen
    self.buffer = keylen * 8
    self.messageLen = int(keylen / 8)

  def send(self, option0, option1):
    # Generate rsa key
    # PublicKey(n, e)
    (pub, priv) = rsa.newkeys(self.keylen)

    # Generate two random message for placeholder for real message
    randomMessage0 = secrets.token_hex(self.messageLen)
    randomMessage1 = secrets.token_hex(self.messageLen)


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
    s.connect((self.ip, self.port))    

    s.send(str.encode(json.dumps(choiceMessage), encoding="UTF-8"))

    data = s.recv(self.buffer)
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

  def choose(self, decision):
    if decision != "0" and decision != "1":
      raise Exception("decision has to be either 0 or 1")

    # Establish connection to sender
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((self.ip, self.port))
    s.listen(1)

    print("Waiting for start...")

    conn, addr = s.accept()

    # Await options and public key data
    data = conn.recv(self.buffer)

    # Try to deserialize the data
    choice = json.loads(data)


    # Choose random number
    k = int(secrets.token_hex(self.messageLen), base=16)


    x_b = int(choice[decision], base=16)
    e = int(choice["key"]["e"])
    N = int(choice["key"]["N"])


    # Calculate response
    v = (x_b + k ** e) % N

    # Send v
    conn.send(bytes(str(v), encoding="UTF-8"))

    # Await k values
    data = conn.recv(self.buffer)

    mValues = json.loads(data)

    # Get the m value of the selected input
    m_ = mValues[decision]

    # Get original message from it
    m = m_ - k

    return m
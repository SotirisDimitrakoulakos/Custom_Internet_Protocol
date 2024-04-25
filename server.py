# -*- coding: utf-8 -*-

from struct import *
import socket
import ctypes
import select

# RECEIVES:

#  0               16                31
#  +----------------+-----------------+
#  |      Type      |      Length     |
#  +----------------+-----------------+
#  |     Value1     |      Value2     |
#  +----------------+--------+--------+
#  |     Value3     |      Value4     |
#  +----------------+--------+--------+
#  |    Math Operation.....|Padding1| |
#  +----------------+--------+--------+


def handle_incoming(conn):
    print("Connected by:", addr)
    print("Server Socket port: ", conn.getsockname())
    print("Client Socket port: ", conn.getpeername())

    msg = conn.recv(4)
    msg_type, msg_length = unpack_from('HH', msg, 0)
    msg_padSize = (4 - msg_length % 4) % 4
    rest_msg = conn.recv(msg_length + msg_padSize - 4)
    msg_value1, msg_value2, msg_value3, msg_value4, msg_math_op = unpack_from('HHHH' + str(msg_length - 3 * 4) +
                                                                              's', rest_msg, 0)
    msg_math_op = msg_math_op.decode('utf-8')

    msg_type = 1  # Response
    flag = False

    # Checking if the numbers are out of bounds here is just for the range 60000-65535 or 30000-65535, because we have
    # already checked that in the client, so we can also be sure that we have sent unsigned short integers (H).
    if msg_math_op == "A":
        print("Math Operation executed is the addition(+) of the numbers:", msg_value1, ",", msg_value2, ",",
              msg_value3, "and", msg_value4)
        msg_result = msg_value1+msg_value2+msg_value3+msg_value4
        if any((n > 60000 or n < 0) for n in [msg_value1, msg_value2, msg_value3, msg_value4]):
            msg_result = "ERROR: Number out of bounds for addition."
    elif msg_math_op == "B":
        print("Math Operation executed is the subtraction(-) of the numbers:", msg_value1, "and", msg_value2)
        msg_result = msg_value1 - msg_value2
        if any((n > 30000 or n < 0) for n in [msg_value1, msg_value2]):
            msg_result = "ERROR: Number out of bounds for subtraction."
    elif msg_math_op == "C":
        print("Math Operation executed is the division(÷) of the numbers:", msg_value1, "and", msg_value2)
        try:
            msg_result = msg_value1 / msg_value2
        except ZeroDivisionError:
            msg_result = "ERROR: Attempted division by zero."
            flag = True
        if any((n > 60000 or n < 0) for n in [msg_value1, msg_value2]):
            if flag:
                msg_result = "ERROR: 1. " + msg_result + " and 2. Number out of bounds for division."
            else:
                msg_result = "ERROR: Number out of bounds for division."
    elif msg_math_op == "D":
        print("Math Operation executed is the multiplication(x) of the numbers:", msg_value1, ",", msg_value2,
              "and", msg_value3)
        msg_result = msg_value1 * msg_value2 * msg_value3
        if any((n > 60000 or n < 0) for n in [msg_value1, msg_value2, msg_value3]):
            msg_result = "ERROR: Number out of bounds for multiplication."
    else:
        print("Math Operation executed is the modulo(%) of the numbers:", msg_value1, "and", msg_value2)
        try:
            msg_result = msg_value1 % msg_value2
        except ZeroDivisionError:
            msg_result = "ERROR: Attempted division by zero, for modulo operation."
            flag = True
        if any((n > 60000 or n < 0) for n in [msg_value1, msg_value2]):
            if flag:
                msg_result = "ERROR: 1. " + msg_result + " and 2. Number out of bounds for modulo."
            else:
                msg_result = "ERROR: Number out of bounds for modulo."

    msg_result = str(msg_result)
    msg_length2 = 1 * 4 + len(msg_result)
    nb = bytes(msg_result, 'utf-8')

    msg_padSize2 = (2 - len(msg_result) % 4) % 4

    message = ctypes.create_string_buffer(msg_length2 + msg_padSize2)

    pack_into('HH', message, 0, msg_type, msg_length2)
    pack_into(str(len(msg_result)) + 's', message, 4, nb)
    if msg_padSize2 > 0:
        pack_into(str(msg_padSize2) + 'x', message, 4 + len(msg_result))

    err = conn.sendall(message)

    print("Errors:", err)  # Prints Errors


serverIP = ''
serverPort = 12345
close = False

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as serverSocket:
    serverSocket.bind((serverIP, serverPort))
    print("The server is ready to receive at port", str(serverPort))
    serverSocket.listen()
    incomingSocks = [serverSocket]
    outgoingSocks = []

    while not close:
        readable, writable, exceptional = select.select(incomingSocks, outgoingSocks, incomingSocks)
        for s in readable:
            if s == serverSocket:
                conn, addr = serverSocket.accept()
                incomingSocks.append(conn)
            else:
                try:
                    handle_incoming(s)
                except:
                    incomingSocks.remove(s)
# SENDS:

#  0               16                31
#  +----------------+-----------------+
#  |      Type      |     Length      |
#  +----------------+-----------------+
#  |        Result.....|Padding1|     |
#  +----------------+--------+--------+

#close = True          # if you want to keep the server open, put those last three lines of code as comments,
#conn.close()          # with '#' character in front of each one, or else the server whil close and it will not
#serverSocket.close()  # accept more requests, after the first one is done. Remove the '#" to close the server.

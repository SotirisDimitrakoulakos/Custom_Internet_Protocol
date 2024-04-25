# -*- coding: utf-8 -*-

from struct import *
import socket
import time
import ctypes

# In the following function we are also checking if the numbers are out of their bounds, because we need to make sure
# that we have sent unsigned short integers (H) for the values, before we pack them (and then unpack them in the server
# in this format).


def assign_values(j, op):
    flag = False
    num = -1
    num1 = 65535
    for i in range(j):
        try:
            num = int(
                input("\nPlease enter integer No." + str(i + 1) + " for " + op + " (between 0 and " + str(
                    num1) + "[should not exceed short integer/2 byte unsigned integer size]): "))
        except ValueError:
            flag = True
        while num < 0 or num > num1 or flag:
            flag = False
            try:
                num = int(input("\nPlease enter integer No." + str(i + 1) + " for " +
                                op + " (between 0 and " + str(num1) + "[should not exceed short integer/2 byte unsigned"
                                                                      " integer size]) [number should be valid]: "))
            except ValueError:
                flag = True
        values[i] = num


# SENDS:

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


serverIP = '192.168.1.7'  # Put your IP here
serverPort = 12345

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
clientSocket.connect((serverIP, serverPort))

operations = {"A": ". Addition of 4 integers (+).", "B": ". Subtraction between 2 integers (-).",
              "C": ". Division between 2 integers (÷)", "D": ". Multiplication of 3 integers (x).",
              "E": ". Modulo between 2 integers (%)."}

while len(operations) > 0:
    print("\n\nPlease enter your preferred Mathematical Operation by letter of choice:\n")
    for key, value in operations.items():
        print(key, value)
    print("(***Enter 'exit' to end the sequence***)")
    math_operation = input("\nYour choice: ")
    if math_operation == 'exit':
        exit()
    while math_operation not in operations:
        print("\n\nPlease enter your preferred Mathematical Operation by letter of choice "
              "\n(that is a valid choice and has not been used already):\n")
        for key, value in operations.items():
            print(key, value)
        print("(***Enter 'exit' to end the sequence***)")
        math_operation = input("\nYour choice: ")
        if math_operation == 'exit':
            exit()
    del operations[math_operation]

    value1 = 0
    value2 = 0
    value3 = 0
    value4 = 0
    values = [0, 0, 0, 0]
    if math_operation == "A":
        assign_values(4, "addition")
    elif math_operation == "B":
        assign_values(2, "subtraction")
    elif math_operation == "C":
        assign_values(2, "division")
    elif math_operation == "D":
        assign_values(3, "multiplication")
    else:
        assign_values(2, "modulo")

    msg_math_op = math_operation
    msg_value1, msg_value2, msg_value3, msg_value4 = [i for i in values]
    msg_type = 0  # Request

    msg_length = 3 * 4 + len(msg_math_op)
    nb = bytes(msg_math_op, 'utf-8')

    msg_padSize = (4 - len(msg_math_op) % 4) % 4

    message = ctypes.create_string_buffer(msg_length + msg_padSize)

    pack_into('HHHHHH', message, 0, msg_type, msg_length, msg_value1, msg_value2, msg_value3, msg_value4)
    pack_into(str(len(msg_math_op))+'s', message, 12, nb)
    if msg_padSize > 0:
        pack_into(str(msg_padSize) + 'x', message, 12 + len(msg_math_op))

    clientSocket.sendall(message)

# RECEIVES:

#  0               16                31
#  +----------------+-----------------+
#  |      Type      |     Length      |
#  +----------------+-----------------+
#  |        Result.....|Padding1|     |
#  +----------------+--------+--------+

    msg2 = clientSocket.recv(4)
    msg_type, msg_length2 = unpack_from('HH', msg2, 0)
    msg_padSize2 = (2 - msg_length2 % 4) % 4
    rest_msg2 = clientSocket.recv(msg_length2 + msg_padSize2 - 4)
    msg_result2 = unpack_from(str(msg_length2 - 1 * 4) + 's', rest_msg2, 0)
    msg_result3 = ''
    for item in msg_result2:
        msg_result3 = msg_result3 + item.decode('utf-8')
    # or msg_result3 = msg_result2[0].decode('utf-8') instead of for. For is used for better explanation of the tuple.

    print("Result:\n" + msg_result3)

    time.sleep(5)

clientSocket.close()


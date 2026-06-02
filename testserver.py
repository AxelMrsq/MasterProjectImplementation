import socket
import pickle
import pandas


nodeManagementDf = pandas.read_csv("testNodeManagement.csv", sep=";")


def newNodeCreation():
    print("new node creation")
    # if nodeManagementDf["token"] == [] :
    #     nodeManagementDf.append({"token": 1})
    pass


def manageMsg(token_part, msg, value) :
    print("managing msg")
    pass


def handleClient(conn, addr, s) :
    try:
        byte_message = b""
        while True:
            packet = s.recv(4096)
            if not packet: break
            byte_message += packet

        clear_message = pickle.loads(byte_message)

        # Expecting format: "TOKEN_ID:COMMAND:VALUE"
        token_part, msg, value = clear_message.split(":", 1)

        if token_part == "NEW" :
            ans = newNodeCreation()

        else : 
            if token_part in nodeManagementDf["token"] :
                ans = manageMsg(token_part, msg, value)

            else :
                conn.sendall("Invalid message format - Expecting format: 'TOKEN_ID:COMMAND:VALUE'")

    except KeyboardInterrupt:
            print("\nConn closed via KeyboardInterrupt")

    except Exception as e:
        print(e)
        conn.sendall("Invalid message format - Expecting format: 'TOKEN_ID:COMMAND:VALUE'")
        conn.close()

    finally:
        conn.close()
        print(f"\nConn closed via end of the handleClient function")
    

def startServer():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        s.bind(('0.0.0.0', 65432))
        s.listen()

        conn, addr = s.accept()

        handleClient(conn, addr, s)

    except KeyboardInterrupt:
        print("\nServer shutting down via KeyboardInterrupt.")

    except Exception as e:
        print(e)
        s.close()

    finally:
        print("\nServer shutting down via end of the startServer function")
        s.close()

startServer()
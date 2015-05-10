GPIO Server

The GPIO Server allows you to control GPIOs through a socket

The following commands are available:
    
    set_direction: Set the direction of the GPIOs
    set_value: Set the pin values on the GPIOs
    get_value: Get the pin values from the GPIOs
    setup_interrupt: Sets up the interrupt to fire off when a button is pressed
        (not implemented yet)


    Commands are issued in the following way:

    Set pin 1 to an output (1):
    "{
        "command":"set_direction",
        "pin":1,
        "direction":1
    }"
    Response:
        "{
            "response":"ok",
        }"



    Set pin 0 to an output, pin 1 to an output, pin 2 to an input, pin 3 to an
        input:
    "{
        "command":"set_direction",
        "pin":[0, 1, 2, 3],
        "direction":[1, 1, 0, 0]
    }"
    Response:
        "{
            "response":"ok",
        }"



    Set pin 1 to low(0):
    "{
        "command":"set_value",
        "pin":1,
        "value":0
    }"
     Response:
        "{
            "response":"ok",
        }"

   

    Set pin 0 to high (1) and pin 1 to high (0):
    "{
        "command":"set_value"
        "pin":[0, 1],
        "value":[1, 0]
    }"
    Response:
        "{
            "response":"ok",
        }"

    Get value of pin 2
    "{
        "command":"get_value",
        "pin":2
    }"
    Response:
        "{
            "response":"ok",
            "value":0
        }"

    Get value of pin 2 and 3
     "{
        "command":"get_value",
        "pin":[2, 3]
    }"
    Response:
        "{
            "response":"ok",
            "value":[0, 1]
        }"

  




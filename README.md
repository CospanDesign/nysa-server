# nysa-server
socket based server to interface with Nysa on a local and remote machines

By default the server will listen on socket 12591 but this can be overriden
when the server is started using the '-p' flag

The first socket opened is the control socket where
user then sends commands down to open addional domain
specific sockets, for example to open up a socket to
receive video images the JSON string


The device will respond with a result JSON string. If a command
is executed successfully it will return a JSON string:

"{
    "response":"ok"
}"



Available Functions:

    Commands:
        Ping the server:
            "{
                "command":"ping"
            }"
        Start a peripheral server
            Starting a new sever is accomplished by sending a start-server
            command the protocol along with any of the configuration data,
            for example the video server is setup with in the following format.

            "{
                "command":"start-server",
                "port":12599,
                "type":"video"
                "args":{
                    "width":480,
                    "height":272,
                    "fourcc":"RGBA"
                }
            }"


        The response will look like the following
        "{
            "response":"ok",
            "port":12599
        }"
        Note if the port is not specified the server will find an available port
        and send this to in the response

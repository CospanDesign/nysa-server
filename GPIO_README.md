Video Controller Server

The Video Controller allows you to control the playback of videos on the server

The following commands are available:
    
    play: play a video file
    stop: stop playing a video file
    display_picture: displays a picture
    status: gets the status

    Commands are issued in the following way:

    Play a video
    "{
        "command":"play",
        "file":"/home/edison/bbb.avi"
    }"
    Response:
        "{
            "response":"ok",
        }"



    Stop Playing a Video
    "{
        "command":"stop"
    }"
    Response:
        "{
            "response":"ok",
        }"



    Display a picture, after the first packet is sent the user should send l
    "{
        "command":"display_picture",
        "size":100
    }"
    [list of bytes]

    Response:
        "{
            "response":"ok",
        }"

    Get Status
    "{
        "command":"status"
    }"
    Response:
        "{
            "response":"ok",
            "status":"status value"
        }"



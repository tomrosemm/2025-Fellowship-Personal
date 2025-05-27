simple Txc1
{
    parameters:
        bool sendMsgOnInit = default(false); // whether the module should send out a message on initialization
        int limit = default(2);   // another parameter with a default value
        @display("i=block/routing"); // add a default icon
    gates:
        input in;
        output out;
}

//
// Make the two module look a bit different with colorization effect.
// Use cyan for `tic', and yellow for `toc'.
//
network Tictoc1
{
    submodules:
        tic: Txc1 {
            parameters:
                sendMsgOnInit = true;
                @display("i=,cyan"); // do not change the icon (first arg of i=) just colorize it
        }
        toc: Txc1 {
            parameters:
                sendMsgOnInit = false;
                @display("i=,gold"); // here too
        }
    connections:
        tic.out --> {  delay = 100ms; } --> toc.in;
        tic.in <-- {  delay = 100ms; } <-- toc.out;
}
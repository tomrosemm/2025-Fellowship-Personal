simple Txc1
{
    parameters:
        bool sendMsgOnInit = default(false);
        int limit = default(2);
        @display("i=block/routing"); // add a default icon
    gates:
        input in;
        output out;
}

simple Tic1 extends Txc1
{
    parameters:
    	sendMsgOnInit = true;
    	@display("i=,cyan");
}

simple Toc1 extends Txc1
{
    parameters:
    	sendMsgOnInit = false;
    	@display("i=,gold");
}

//
// Make the two module look a bit different with colorization effect.
// Use cyan for `tic', and yellow for `toc'.
//
network Tictoc1
{
    submodules:
        tic: Tic1;
        toc: Toc1;
    connections:
        tic.out --> {  delay = 100ms; } --> toc.in;
        tic.in <-- {  delay = 100ms; } <-- toc.out;
}
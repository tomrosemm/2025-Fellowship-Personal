//
// This file is part of an OMNeT++/OMNEST simulation example.
//
// Copyright (C) 2003 Ahmet Sekercioglu
// Copyright (C) 2003-2015 Andras Varga
//
// This file is distributed WITHOUT ANY WARRANTY. See the file
// `license' for details on this and other legal matters.
//

#include <stdio.h>
#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;

/**
 * Derive the Txc1 class from cSimpleModule. In the Tictoc1 network,
 * both the `tic' and `toc' modules are Txc1 objects, created by OMNeT++
 * at the beginning of the simulation.
 */
class Txc1 : public cSimpleModule
{
  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

class Txc2 : public cSimpleModule
{
  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

/**
 * In this class we add a counter, and delete the message after ten exchanges.
 */
class Txc3 : public cSimpleModule
{
  private:
    int counter;  // Note the counter here

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

/**
 * In this step you'll learn how to add input parameters to the simulation:
 * we'll turn the "magic number" 10 into a parameter.
 */
class Txc4 : public cSimpleModule
{
  private:
    int counter;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

class Txc5 : public cSimpleModule
{
  private:
    int counter;

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

/**
 * In the previous models, `tic' and `toc' immediately sent back the
 * received message. Here we'll add some timing: tic and toc will hold the
 * message for 1 simulated second before sending it back. In OMNeT++
 * such timing is achieved by the module sending a message to itself.
 * Such messages are called self-messages (but only because of the way they
 * are used, otherwise they are completely ordinary messages) or events.
 * Self-messages can be "sent" with the scheduleAt() function, and you can
 * specify when they should arrive back at the module.
 *
 * We leave out the counter, to keep the source code small.
 */
class Txc6 : public cSimpleModule
{
  private:
    // Set the pointers to nullptr, so that the destructor won't crash
    // even if initialize() doesn't get called because of a runtime
    // error or user cancellation during the startup process.
    cMessage *event = nullptr;  // pointer to the event object which we'll use for timing
    cMessage *tictocMsg = nullptr;  // variable to remember the message until we send it back

  public:
    virtual ~Txc6();

  protected:
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

// The module class needs to be registered with OMNeT++
Define_Module(Txc1);
Define_Module(Txc2);
Define_Module(Txc3);
Define_Module(Txc4);
Define_Module(Txc5);
Define_Module(Txc6);

Txc6::~Txc6()
{
    // Dispose of dynamically allocated the objects
    cancelAndDelete(event);
    delete tictocMsg;
}

void Txc1::initialize()
{
    // Initialize is called at the beginning of the simulation.
    // To bootstrap the tic-toc-tic-toc process, one of the modules needs
    // to send the first message. Let this be `tic'.

    // Am I Tic or Toc?
    if (strcmp("tic", getName()) == 0) {
        // create and send first message on gate "out". "tictocMsg" is an
        // arbitrary string which will be the name of the message object.
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc2::initialize()
{
    if (strcmp("tic", getName()) == 0) {
        // The `ev' object works like `cout' in C++.
        EV << "Sending initial message\n";
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc3::initialize()
{
    // Initialize counter to ten. We'll decrement it every time and delete
    // the message when it reaches zero.
    counter = 10;

    // The WATCH() statement below will let you examine the variable under
    // Qtenv. After doing a few steps in the simulation, click either
    // `tic' or `toc', and you'll find its `counter' variable and its
    // current value displayed in the inspector panel (bottom left).
    WATCH(counter);

    if (strcmp("tic", getName()) == 0) {
        EV << "Sending initial message\n";
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc4::initialize()
{
    // Initialize the counter with the "limit" module parameter, declared
    // in the NED file (tictoc4.ned).
    counter = par("limit");

    // we no longer depend on the name of the module to decide
    // whether to send an initial message
    if (par("sendMsgOnInit").boolValue() == true) {
        EV << "Sending initial message\n";
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc5::initialize()
{
    // Initialize the counter with the "limit" module parameter, declared
    // in the NED file (tictoc4.ned).
    counter = par("limit");

    // we no longer depend on the name of the module to decide
    // whether to send an initial message
    if (par("sendMsgOnInit").boolValue() == true) {
        EV << "Sending initial message\n";
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc6::initialize()
{
    // Create the event object we'll use for timing -- just any ordinary message.
    event = new cMessage("event");

    // No tictoc message yet.
    tictocMsg = nullptr;

    if (strcmp("tic", getName()) == 0) {
        // We don't start right away, but instead send an message to ourselves
        // (a "self-message") -- we'll do the first sending when it arrives
        // back to us, at t=5.0s simulated time.
        EV << "Scheduling first send to t=5.0s\n";
        tictocMsg = new cMessage("tictocMsg");
        scheduleAt(5.0, event);
    }
}

void Txc1::handleMessage(cMessage *msg)
{
    // The handleMessage() method is called whenever a message arrives
    // at the module. Here, we just send it to the other module, through
    // gate `out'. Because both `tic' and `toc' does the same, the message
    // will bounce between the two.
    send(msg, "out"); // send out the message
}


void Txc2::handleMessage(cMessage *msg)
{
    // msg->getName() is name of the msg object, here it will be "tictocMsg".
    EV << "Received message `" << msg->getName() << "', sending it out again\n";
    send(msg, "out");
}

void Txc3::handleMessage(cMessage *msg)
{
    // Increment counter and check value.
    counter--;
    if (counter == 0) {
        // If counter is zero, delete message. If you run the model, you'll
        // find that the simulation will stop at this point with the message
        // "no more events".
        EV << getName() << "'s counter reached zero, deleting message\n";
        delete msg;
    }
    else {
        EV << getName() << "'s counter is " << counter << ", sending back message\n";
        send(msg, "out");
    }
}

void Txc4::handleMessage(cMessage *msg)
{
    counter--;
    if (counter == 0) {
        EV << getName() << "'s counter reached zero, deleting message\n";
        delete msg;
    }
    else {
        EV << getName() << "'s counter is " << counter << ", sending back message\n";
        send(msg, "out");
    }
}

void Txc5::handleMessage(cMessage *msg)
{
    counter--;
    if (counter == 0) {
        EV << getName() << "'s counter reached zero, deleting message\n";
        delete msg;
    }
    else {
        EV << getName() << "'s counter is " << counter << ", sending back message\n";
        send(msg, "out");
    }
}

void Txc6::handleMessage(cMessage *msg)
{
    // There are several ways of distinguishing messages, for example by message
    // kind (an int attribute of cMessage) or by class using dynamic_cast
    // (provided you subclass from cMessage). In this code we just check if we
    // recognize the pointer, which (if feasible) is the easiest and fastest
    // method.
    if (msg == event) {
        // The self-message arrived, so we can send out tictocMsg and nullptr out
        // its pointer so that it doesn't confuse us later.
        EV << "Wait period is over, sending back message\n";
        send(tictocMsg, "out");
        tictocMsg = nullptr;
    }
    else {
        // If the message we received is not our self-message, then it must
        // be the tic-toc message arriving from our partner. We remember its
        // pointer in the tictocMsg variable, then schedule our self-message
        // to come back to us in 1s simulated time.
        EV << "Message arrived, starting to wait 1 sec...\n";
        tictocMsg = msg;
        scheduleAt(simTime()+1.0, event);
    }
}

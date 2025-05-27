/*
 * txc1.cc
 *
 *  Created on: May 27, 2025
 *      Author: trose
 */

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
private:
    int counter;

  protected:
    // The following redefined virtual function holds the algorithm.
    virtual void initialize() override;
    virtual void handleMessage(cMessage *msg) override;
};

// The module class needs to be registered with OMNeT++
Define_Module(Txc1);

void Txc1::initialize()
{
    // Initialize is called at the beginning of the simulation.
    // To bootstrap the tic-toc-tic-toc process, one of the modules needs
    // to send the first message. Let this be `tic'.

    counter = par("limit");

    // The WATCH() statement below will let you examine the variable under
    // Qtenv. After doing a few steps in the simulation, click either
    // `tic' or `toc', and you'll find its `counter' variable and its
    // current value displayed in the inspector panel (bottom left).
    WATCH(counter);


    if (par("sendMsgOnInit").boolValue() == true) {
        EV << "Sending initial message\n";
        cMessage *msg = new cMessage("tictocMsg");
        send(msg, "out");
    }
}

void Txc1::handleMessage(cMessage *msg)
{
    counter --;
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


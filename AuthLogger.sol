// SPDX-License-Identifier: MIT 
pragma solidity ^0.8.0;

contract AuthLogger {
    event AuthEvent(bytes32 vehicleHash, uint256 timestamp, bool authenticated);

    function logAuth(bytes32 vehicleHash, uint256 timestamp, bool authenticated) public {
        emit AuthEvent(vehicleHash, timestamp, authenticated);
    }
}
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Authentication {
    event AuthAttempt(bytes32 vehicleHash, uint256 timestamp, bool authenticated);

    function logAuth(bytes32 vehicleHash, uint256 timestamp, bool authenticated) public {
        emit AuthAttempt(vehicleHash, timestamp, authenticated);
    }
}
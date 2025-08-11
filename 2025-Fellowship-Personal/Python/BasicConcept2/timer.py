##
# @file timer.py
# @author Tom Rose
#
# @brief
#   Provides a Timer class for creating named timer objects with start, stop, reset, edit, and string representation functionality
#
# @details
#   - Allows creation of named timers for tracking elapsed time
#   - Supports starting, stopping, resetting, editing, and querying elapsed time
#   - Designed for integration in experiments or simulations requiring timing
##

## Imports
# Libraries
import time


##
# @class Timer
# @brief Represents a named timer object for measuring elapsed time
#
# @details
#   - Each Timer instance can be started, stopped, reset, or edited
#   - Elapsed time can be queried at any point
#   - Supports checking if the timer is currently running
#   - Timer can be represented as a string for easy debugging and logging
#
# Usage:
#   timer = Timer("MyTimer")
#   timer.start()
#   ... do work ...
#   timer.stop()
#   elapsed = timer.elapsed()
##
class Timer:
    
    
    ##
    # @brief Initialize a Timer instance
    # @param name Name of the timer
    # @param start_time Initial elapsed time (default 0)
    ##
    def __init__(self, name, start_time=0):
        
        # Store the timer name and initial elapsed time
        self.name = name
        self._elapsed = start_time
        
        # Set initial _start to None and _running to False to represent the timer not running
        self._start = None
        self._running = False


    ##
    # @brief Start the timer
    # @details
    #   Starts timer if not already running
    ##
    def start(self):
        
        # If the timer is not running, set start time and mark as running
        if not self._running:
            self._start = time.time()
            self._running = True


    ##
    # @brief Stop the timer
    # @details
    #   Stops timer if running and accumulates elapsed time
    ##
    def stop(self):
        
        # If the timer is running, calculate elapsed time and mark as stopped
        if self._running:
            self._elapsed += time.time() - self._start
            self._start = None
            self._running = False


    ##
    # @brief Reset the timer
    # @param new_time New elapsed time to set (default 0)
    # @details
    #   Resets elapsed time and stops the timer
    ##
    def reset(self, new_time=0):
        
        # Stop the timer, reset elapsed time to new_time, and clear start time
        self._running = False
        self._elapsed = new_time
        self._start = None
        


    ##
    # @brief Edit the elapsed time
    # @param new_time New elapsed time to set
    # @details
    #   Sets elapsed time; if running, restarts timing from now
    ##
    def edit(self, new_time):
        
        # Set the elapsed time to new_time
        self._elapsed = new_time
        
        # If the timer is running, reset the start time to now
        if self._running:
            self._start = time.time()


    ##
    # @brief Get the current elapsed time
    # @return Elapsed time in seconds (float)
    ##
    def elapsed(self):
        
        # If the timer is running, calculate elapsed time since start and return it. If not running, return the accumulated elapsed time
        if self._running:
            return self._elapsed + (time.time() - self._start)
        
        return self._elapsed


    ##
    # @brief Check if the timer is currently running
    # @return True if running, False otherwise
    ##
    def is_running(self):
        
        # Return the running status of the timer
        return self._running

    ##
    # @brief String representation of the Timer
    # @return String with timer name, elapsed time, and running status
    #
    # @details
    # Usage:
    #   print(timer)  # Outputs: <Timer name=MyTimer, elapsed=5.0, running=True>
    ##
    def __repr__(self):
        return f"<Timer(name={self.name}, elapsed={self.elapsed()}, running={self._running})>"


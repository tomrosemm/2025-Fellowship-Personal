##
# @file timer.py
# @author Tom Rose
#
# @brief
#   Provides a Timer class for creating named timer objects with start, stop, reset, and edit functionality.
#
# @details
#   - Allows creation of named timers for tracking elapsed time.
#   - Supports starting, stopping, resetting, editing, and querying elapsed time.
#   - Designed for integration in experiments or simulations requiring timing.
##

import time

##
# @class Timer
# @brief Represents a named timer object for measuring elapsed time.
#
# @details
#   - Each Timer instance can be started, stopped, reset, or edited.
#   - Elapsed time can be queried at any point.
#   - Supports checking if the timer is currently running.
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
    # @brief Initialize a Timer instance.
    # @param name Name of the timer.
    # @param start_time Initial elapsed time (default 0).
    ##
    def __init__(self, name, start_time=0):
        self.name = name
        self._elapsed = start_time
        self._start = None
        self._running = False

    ##
    # @brief Start the timer.
    # @details
    #   Starts timing if not already running.
    ##
    def start(self):
        if not self._running:
            self._start = time.time()
            self._running = True

    ##
    # @brief Stop the timer.
    # @details
    #   Stops timing and accumulates elapsed time.
    ##
    def stop(self):
        if self._running:
            self._elapsed += time.time() - self._start
            self._start = None
            self._running = False

    ##
    # @brief Reset the timer.
    # @param new_time New elapsed time to set (default 0).
    # @details
    #   Resets elapsed time and stops the timer.
    ##
    def reset(self, new_time=0):
        self._elapsed = new_time
        self._start = None
        self._running = False

    ##
    # @brief Edit the elapsed time.
    # @param new_time New elapsed time to set.
    # @details
    #   Sets elapsed time; if running, restarts timing from now.
    ##
    def edit(self, new_time):
        self._elapsed = new_time
        if self._running:
            self._start = time.time()

    ##
    # @brief Get the current elapsed time.
    # @return Elapsed time in seconds (float).
    ##
    def elapsed(self):
        if self._running:
            return self._elapsed + (time.time() - self._start)
        return self._elapsed

    ##
    # @brief Check if the timer is currently running.
    # @return True if running, False otherwise.
    ##
    def is_running(self):
        return self._running

    ##
    # @brief String representation of the Timer.
    # @return String with timer name, elapsed time, and running status.
    ##
    def __repr__(self):
        return f"<Timer(name={self.name}, elapsed={self.elapsed():.2f}, running={self._running})>"

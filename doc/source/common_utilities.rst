
********************
The utilities module
********************

This module contains convenience functions for quick setup of common
tasks.

.. contents:: Table of Contents
   :depth: 3

Get a logger
============

The :func:`.get_logger` function is a convenience function to setup
logging output. It will return a named logger, which can be used
inside programs, and it will at the same time, setup logging from all
the imported PyExpLabSys components to the same logging location. The
function has the ability to setup logging both to a terminal and to a
log file, including setting up log rotation.

``get_logger`` usage examples
=============================

Logging to terminal and send emails on warnings and above (default)
-------------------------------------------------------------------

To get a named logger that will output logging information to the
terminal and send emails on warnings and above, do the following:

.. code-block:: python

    from PyExpLabSys.common.utilities import get_logger
    LOGGER = get_logger('name_of_my_logger')

where the ``name_of_my_logger`` should be some descriptive name for
what the program/script does e.g. "coffee_machine_count_monitor".

From the returned ``LOGGER``, information can now be logged via the
usual ``.info()``, ``.warning()`` methods etc.

To turn logging to the terminal of (and only use the other configured
logging handlers), set the optional boolean ``terminal_log`` parameter
to ``False``.

The email notification on warnings and above is on-by-default and is
controlled by the two optional boolean parameters
``email_on_warnings`` and ``email_on_errors``. It will send emails on
logged warnings to the warnings list and on logged errors (and above)
to the error list.

Rotating file logger
--------------------

To get a named logger that also logs to a file do:

.. code-block:: python

    from PyExpLabSys.common.utilities import get_logger
    LOGGER = get_logger('name_of_my_logger', file_log=True)

The log will be written to the file ``name_of_my_logger.log``. The
file name can be changed via the option ``file_name``, the same way as
the maximum log file size and number of saved backups can be changed,
as documented :func:`below <.get_logger>`.


Getting the logger to send emails on un-caught exceptions
---------------------------------------------------------

To also make the logger send en email, containing any un-caught
exception, do the following:

.. code-block:: python

    from PyExpLabSys.common.utilities import get_logger
    LOGGER = get_logger('Test logger')

    def main():
	pass  # All your main code that might raise exceptions

    if __name__ == '__main__':
        try:
            main()
        except KeyboardInterrupt:
            pass  # Shut down code here
        except Exception as exception:
            LOGGER.exception(exception)
            # Possibly shut down code here
            raise exception

.. note:: In the example there is a seperate ``except`` for the
    ``KeyboardInterrupt`` exception, to make it possible to use
    keyboard interrupts to shut the program down, without sending an
    exception email about it.


Auto-generated module documentation
===================================

.. autodata:: PyExpLabSys.common.utilities.MAIL_HOST
.. autodata:: PyExpLabSys.common.utilities.WARNING_EMAIL
.. autodata:: PyExpLabSys.common.utilities.ERROR_EMAIL
.. autofunction:: PyExpLabSys.common.utilities.get_logger

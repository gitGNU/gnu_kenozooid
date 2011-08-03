Data Backup
-----------
The simplest approach to access dive computer data is to save its whole
memory (settings, dive log book, etc.) to a binary file. This can be useful
in few situations as memory dump can be

- used as a backup of dive computer data
- sent to software developers to investigate software related problems
- sent to dive computer support team to investigate dive computer related
  problems

Kenozooid allows to perform a dump of whole dive computer memory. For
example, the command

    kenozooid dump ostc backup-20090214.dump

saves OSTC dive computer memory state into ``backup-20090214.dump`` file.

Data Regeneration
-----------------

.. vim: sw=4:et:ai

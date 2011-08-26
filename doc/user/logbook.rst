Dive Logbook
============
Kenozooid supports basic dive logbook functionality, which allows to list,
search, add and remove dives, buddies and dive sites.

.. _logbook-ls:

Listing and Searching
---------------------
Kenozooid supports dive, buddy and dive site listing and searching with
``dive list``, ``buddy list`` and ``site list`` commands.

Adding Buddies and Dive Sites
-----------------------------
Adding buddies and dive sites to a logbook file is possible with ``buddy add``
and ``site add`` commands.

To add dive sites to a dive site or a logbook file::

    kz site add sckg 'Scapa Flow' 'SMS Konig' sites.uddf
    kz site add sckn 'Scapa Flow' 'SMS Koln' sites.uddf
    kz site add scmk 'Scapa Flow' 'SMS Markgraf' sites.uddf

    kz site list sites.uddf

       1 sckg       Scapa Flow           SMS Konig   
       2 sckn       Scapa Flow           SMS Koln    
       3 scmk       Scapa Flow           SMS Markgraf

To add buddies to a buddy or a logbook file::

    kz buddy add tcora "Tom Cora" buddies.uddf
    kz buddy add tex "Thelma Ex" buddies.uddf 
    kz buddy add jn "John Neurosis" buddies.uddf

    kz buddy list buddies.uddf                  

       1 tcora      Tom        Cora                  
       2 tex        Thelma     Ex                    
       3 jn         John       Neurosis       

If output file (``dives.uddf`` and ``buddies.uddf`` above) does not exist, then
it is created by Kenozooid. Before adding data to a file, Kenozooid creates
backup file with ``.bak`` extension, i.e. ``dives.uddf.bak``, ``buddies.uddf.bak``.

Of course, one logbook file (i.e. ``logbook.uddf``) can be used to store dive
sites and buddies information instead of two separate files. However, it is
easier to share your buddies data only with your friends or dive site list with
larger group of unknown people, when separate files are used.

Adding Dives
------------
.. basic data vs. profile data

Removing Data
-------------

.. vim: sw=4:et:ai

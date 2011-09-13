.. _user-logbook:

Dive Logbook
============
Kenozooid supports basic dive logbook functionality, which allows to list,
search, add and remove dives, buddies and dive sites.

.. _user-logbook-ls:

Listing and Searching
---------------------
Kenozooid supports dive, buddy and dive site listing and searching with
``dive list``, ``buddy list`` and ``site list`` commands.

Dives Listing
^^^^^^^^^^^^^
Dive list consists of the following columns

- number of a dive from a file
- date and time
- maximum depth
- duration in minutes
- minimum temperature

To list the dives from a dive computer backup file::

    $ kz dive list backup-ostc-20110728.uddf 
    backup-ostc-20110728.uddf:
        1: 2011-06-12 21:45     40.8m     58:50     5.4°C
        2: 2011-06-19 12:26     58.8m     48:40     6.2°C
        3: 2011-06-24 13:18     94.1m    107:20     5.1°C
        4: 2011-06-26 12:56     85.0m    104:42     5.5°C
        5: 2011-06-29 21:30     42.7m     57:29     6.2°C
        6: 2011-07-07 21:44     27.5m     60:38     7.0°C
        7: 2011-07-20 21:50     49.9m     65:42     5.7°C
        8: 2011-07-28 21:26     60.2m     64:08     5.7°C

Buddies Listing 
^^^^^^^^^^^^^^^
The buddy data list consists of

- buddy number from a file
- buddy id
- first name
- family name
- diving organisation, i.e. CFT, PADI
- diving organisation membership id

To list buddies::

    $ kz buddy list logbook.uddf    
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676   

Search string can be specified after the command to limit the list of
buddies. The search string can be one of

- buddy id
- part of buddy name (first name, family name)
- organisation name, i.e. ``PADI``, ``CMAS``, ``CFT``
- organisation membership id

To find buddy by her or his name, i.e. ``John``::

    $ kz buddy list John logbook.uddf
    logbook.uddf:
       1: jn         Johnny     Neurosis             CFT   1370       
       2: jk         John       Koval                PADI  13676  

To find all ``PADI`` buddies::

    $ kz buddy list PADI logbook.uddf 
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: jk         John       Koval                PADI  13676 

Dive Sites Listing
^^^^^^^^^^^^^^^^^^
The dive site list consists of

- dive site number from a file
- location (city, geographical area), i.e. ``Howth``, ``Scapa Flow``
- dive site name, i.e. 
- coordinates (longitude, latitude)

To list dive sites::

    $ kz site list logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170

The dive site listing can be searched with one of the search string

- id
- part of location, i.e. ``Scapa``
- part of name, i.e. ``Lough``

To find dive sites by location containing ``Scapa`` string::

    $ kz site list Scapa logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig   
       2: sckn       Scapa Flow           SMS Koln    
       3: scmk       Scapa Flow           SMS Markgraf

To find dive sites with name containing ``Lough`` string::

    $ kz site list Lough logbook.uddf
    logbook.uddf:
       1: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090


Adding Buddies and Dive Sites
-----------------------------
Adding buddies and dive sites to a logbook file is possible with ``buddy add``
and ``site add`` commands.

To add a dive site to a logbook file::

    $ kz site add bath Bathroom Bath logbook.uddf

    $ kz site list logbook.uddf      
    examples/logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170
       6: bath       Bathroom             Bath 


To add a buddy to a logbook file::

    $ kz buddy add frog "John Froggy" logbook.uddf                     

    $ kz buddy list logbook.uddf     
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676      
       5: frog       John       Froggy 


If logbook file (``logbook.uddf`` above) does not exist, then it is created
by Kenozooid. Before adding data to a file, Kenozooid creates backup file
with ``.bak`` extension, i.e. ``logbook.uddf.bak``.

Adding Dives
------------
.. basic data vs. profile data

Removing Data
-------------
To remove a buddy or a dive site use ``buddy del`` or ``site del``
commands. Identify buddy or dive site to be removed with its id.

For example, to remove ``John Froggy`` buddy::

    $ kz buddy del frog logbook.uddf

    $ kz buddy list logbook.uddf
    logbook.uddf:
       1: tcora      Tom        Cora                 PADI  1374       
       2: tex        Thelma     Ex                    
       3: jn         Johnny     Neurosis             CFT   1370       
       4: jk         John       Koval                PADI  13676 


To remove ``Bathroom`` dive site::

    $ kz site del bath logbook.uddf

    $ kz site list logbook.uddf
    logbook.uddf:
       1: sckg       Scapa Flow           SMS Konig           
       2: sckn       Scapa Flow           SMS Koln            
       3: scmk       Scapa Flow           SMS Markgraf        
       4: bmlh       Baltimore            Lough Hyne            -9.29718000, 51.5008090
       5: hie        Howth                Ireland's Eye         -6.06416900, 53.4083170

.. vim: sw=4:et:ai

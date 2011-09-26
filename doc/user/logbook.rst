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

To list the dives from a logbook file or from a dive computer backup file::

    $ kz dive list logbook.uddf
    logbook.uddf:
        1: 2009-10-22 15:32     30.3m     64:16    29.0°C
        2: 2010-10-29 06:02     29.4m     61:30    26.7°C

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
Kenozooid supports two modes of adding dives into logbook file

- adding basic dive data (date and time of dive, maximum depth, dive duration)
- copying dive data from another file (i.e. dive computer backup file)

To add a dive with basic data use ``dive add`` command::

    kz dive add '2011-10-12 13:14' 32.5 51 logbook.uddf                              
    kz dive list logbook.uddf
    logbook.uddf:
        1: 2009-10-22 15:32     30.3m     64:16    29.0°C
        2: 2010-10-29 06:02     29.4m     61:30    26.7°C
        3: 2011-10-12 13:14     32.5m     51:00 


To copy dive from another file use ``dive copy`` command. For example, to
add 4th dive from dive computer backup file to logbook file::

    $ kz dive copy 4 backup-ostc-20110728.uddf logbook.uddf

    $ kz dive list logbook.uddf
    logbook.uddf:
        1: 2009-10-22 15:32     30.3m     64:16    29.0°C
        2: 2010-10-29 06:02     29.4m     61:30    26.7°C
        3: 2011-06-26 12:56     85.0m    104:42     5.5°C

Copying a dive and adding dive site and buddy data at the same time is also
supported. For example, to copy a dive with ``Ireland's Eye`` dive site and
buddies ``Johnny Neurosis`` and ``John Koval``::

    $ kz dive copy 4 backup-ostc-20110728.uddf -s hie -b jn jk -- logbook.uddf

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

=================
Python AMI Client
=================

.. image:: https://travis-ci.org/ettoreleandrotognoli/python-ami.svg?branch=master
    :target: https://travis-ci.org/ettoreleandrotognoli/python-ami

.. image:: https://codecov.io/gh/ettoreleandrotognoli/python-ami/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/ettoreleandrotognoli/python-ami

.. image:: https://badge.fury.io/py/asterisk-ami.svg
    :target: https://badge.fury.io/py/asterisk-ami

A simple Python AMI client
http://programandonoaquario.blogspot.com.br

Install
-------

Install asterisk-ami

.. code-block:: shell

    pip install asterisk-ami

Install latest asterisk-ami

.. code-block:: shell

    pip install git+https://github.com/ettoreleandrotognoli/python-ami

Usage
-----

Connect
~~~~~~~

.. code-block:: python

    from asterisk.ami import AMIClient
    
    client = AMIClient(address='127.0.0.1',port=5038)
    client.login(username='username',secret='password')
    
Disconnect
~~~~~~~~~~

.. code-block:: python

    client.logoff()


Send an action
~~~~~~~~~~~~~~

.. code-block:: python

    from asterisk.ami import SimpleAction
    
    action = SimpleAction(
        'Originate',
        Channel='SIP/2010',
        Exten='2010',
        Priority=1,
        Context='default',
        CallerID='python',
    )
    client.send_action(action)


Send an action with adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    from asterisk.ami import AMIClientAdapter
    
    adapater = AMIClientAdapter(client)
    adapter.Originate(
        Channel='SIP/2010',
        Exten='2010',
        Priority=1,
        Context='default',
        CallerID='python',
    )
    
Synchronous Response
~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    #without adapter
    future = client.send_action(action)
    response = future.response
    
    #with adapter
    future = adapter.Originate(...)
    response = future.response
    

Asynchronous Response
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def callback_response(response):
        print(response)

    #without adapter
    future = client.send_action(action,callback=callback_response)
    
    #with adapter
    future = adapter.Originate(...,_callback=callback_response)
    
    #you can use the future to wait the callback execute
    reponse = future.response

Listen Events
~~~~~~~~~~~~~

.. code-block:: python

    def event_listener(event,**kwargs):
        print(event)

    client.add_event_listener(event_listener)
    

Filter Events
~~~~~~~~~~~~~

With a custom class

.. code-block:: python

    from asterisk.ami import EventListener

    class RegistryEventListener(EventListener):
    
        def on_Registry(event,**kwargs):
            print('Registry Event',event)
            
    client.add_event_listener(RegistryEventListener())
    
    class AllEventListener(EventListener):
    
        def on_event(event,**kwargs):
            print('Event',event)
    
    client.add_event_listener(AllEventListener())

With black or white list

.. code-block:: python

    def event_listener(event,**kwargs):
        print(event)
        
    client.add_event_listener(
        EventListener(white_list=['Registry','PeerStatus'])
    )
    
    client.add_event_listener(
        EventListener(black_list=['VarSet'])
    )
            
Like a custom class

.. code-block:: python

    def event_listener(event,**kwargs):
        print(event)
        
    client.add_event_listener(
        EventListener(on_VarSet=event_listener,on_ExtensionStatus=event_listener)
    )
    
    client.add_event_listener(
        EventListener(on_event=event_listener)
    )
    

Filter Event Value
~~~~~~~~~~~~~~~~~~

.. code-block:: python

    def event_listener(event,**kwargs):
        print('Ringing',event)
        
    
    client.add_event_listener(
        EventListener(
            on_event=event_listener,
            white_list='Newstate',
            ChannelStateDesc='Ringing',
            ConnectedLineNum='2004',
        )
    )
    
Filter with regex
~~~~~~~~~~~~~~~~~

.. code-block:: python

    import re
    
    def event_listener(event,**kwargs):
        print(event)
        
    client.add_event_listener(
        EventListener(
            on_Newstate=event_listener,
            white_list=re.compile('.*'),
            ChannelStateDesc=re.compile('^Ring.*'),
        )
    )
    
    

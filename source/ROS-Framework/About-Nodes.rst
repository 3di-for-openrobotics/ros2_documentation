.. redirect-from::

    Concepts/Basic/About-Nodes

Nodes
=====

.. toctree::
   :maxdepth: 1
   :hidden:

   nodes/About-Discovery
   nodes/About-Domain-ID
   nodes/About-Logging/About-Logging
   nodes/About-Composition
   nodes/Working-with-nodes

Nodes are processes that perform computation and can communicate with other nodes using topics, services, and actions. 
This article explains what nodes are and how they work.  

[Area: Framework | Content-type: concept | Experience: beginner]

.. contents:: Table of Contents
   :local:

Summary
-------

Each node does one logical thing.
Nodes can function as:

* A :doc:`publisher <interfaces/About-Topics>` to deliver data to other nodes.
* A :doc:`subscriber <interfaces/About-Topics>` to get data from other nodes.
* A :doc:`service client <interfaces/About-Services>` to have another node perform a computation on their behalf.
* A :doc:`service server <interfaces/About-Services>` to provide functionality to other nodes.
* An :doc:`action client <interfaces/About-Actions>` to have another node perform a long-running computation on their behalf.
* An :doc:`action server <interfaces/About-Actions>` to provide functionality to other nodes. 

Nodes
-----
A node is a participant in the ROS 2 graph, which uses a :doc:`client library <About-Client-Libraries>` to communicate with other nodes.
Nodes can communicate with other nodes within the same process, in a different process, or on a different machine.
Nodes are typically the unit of computation in a ROS graph; each node should do one logical thing.

Nodes can :doc:`publish <interfaces/About-Topics>` to named topics to deliver data to other nodes, or :doc:`subscribe <interfaces/About-Topics>` to named topics to get data from other nodes.
They can also act as a :doc:`service client <interfaces/About-Services>` to have another node perform a computation on their behalf, or as a :doc:`service server <interfaces/About-Services>` to provide functionality to other nodes.
For long-running computations, a node can act as an :doc:`action client <interfaces/About-Actions>` to have another node perform it on their behalf, or as an :doc:`action server <interfaces/About-Actions>` to provide functionality to other nodes.
Nodes can provide configurable :doc:`parameters <About-Parameters>` to change behavior during run-time.

Nodes are often a complex combination of publishers, subscribers, service servers, service clients, action servers, and action clients, all at the same time.

Connections between nodes are established through a distributed :doc:`discovery <nodes/About-Discovery>` process.

Related content
---------------
* :doc:`nodes/About-Discovery`
* :doc:`nodes/About-Domain-ID`
* :doc:`nodes/About-Logging/About-Logging`
* :doc:`nodes/About-Composition`
* :doc:`nodes/Working-with-nodes`   

FAQs
----

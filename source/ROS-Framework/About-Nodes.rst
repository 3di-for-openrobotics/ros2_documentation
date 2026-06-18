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

A node is a single process that performs computation and can communicate with other nodes using topics, services, and actions.
This article describes what nodes do and how they interconnect.

**[Area: Framework | Content-type: concept | Experience: beginner]**

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
* An :doc:`action server <interfaces/About-Actions>` to provide long-running functionality to other nodes.

Nodes
-----
A node is a unit of computation in a ROS graph.
Each node is an independent processes that handles a specific task, such as reading sensor data, processing an algorithm, or driving a motor.

Each node runs separately in its own runtime environment and uses a :doc:`client library <About-Client-Libraries>` to allow it to communicate with other nodes, even if other nodes are not written in the same language.
Nodes can communicate with other nodes within the same process, in a different process, or on a different machine.

Typically, nodes are written in C++ or Python.
C++ is commonly used for low-level drivers and processes that require fast execution.
Python offers faster development time with some runtime overhead.

ROS is based on object-oriented programming principles.
Individual nodes are written as subclasses of the Node class, inheriting properties from it as defined by ROS.
Nodes can provide configurable :doc:`parameters <About-Parameters>` to change behavior during run-time.

ROS nodes typically communicate through the following three types of interfaces:

* Topics, for continuous data streams:

   Nodes can :doc:`publish <interfaces/About-Topics>` to named topics to deliver data to other nodes, or :doc:`subscribe <interfaces/About-Topics>` to named topics to get data from other nodes
   Publishers and subscribers are object instances within these nodes.

* Services, for synchronous request/response interactions (short tasks which happen immediately):

   Nodes can act as a :doc:`service client <interfaces/About-Services>` to have another node perform a discrete computation on their behalf, or as a :doc:`service server <interfaces/About-Services>` to provide a function to other nodes.

* Actions, for long-running tasks with feedback (tasks that may take some time to complete):

   A node can act as an :doc:`action client <interfaces/About-Actions>` to have another node perform it on their behalf, or as an :doc:`action server <interfaces/About-Actions>` to provide a long-running function to other nodes.

Nodes are often a complex combination of publishers, subscribers, service servers, service clients, action servers, and action clients, all at the same time.

Connections between nodes are established through a distributed :doc:`discovery <nodes/About-Discovery>` process.

Related content
---------------
* :doc:`nodes/About-Discovery`
* :doc:`About-Client-Libraries`
* :doc:`About-Parameters`
* :doc:`interfaces/Topics-Services-Actions`
* :doc:`nodes/Working-with-nodes`   

FAQs
----

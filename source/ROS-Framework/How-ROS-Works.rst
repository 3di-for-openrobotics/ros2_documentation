How ROS works
=============

.. toctree::
   :maxdepth: 1
   :hidden:

ROS systems use a network of modular software elements, called nodes, which process data concurrently and can communicate with each other through defined interfaces.
The ROS graph refers to the network of nodes.
This article provides a high-level overview of how ROS works

**[Area: Framework | Content-type: concept | Experience: beginner]**

.. contents:: Table of Contents
   :local:

Summary
-------
ROS systems use a network of modular software elements, called nodes, which process data concurrently and can communicate with each other through defined interfaces.
The ROS graph refers to the network of nodes.

Elements of a ROS system
------------------------

In ROS 2, a single executable (C++ program, Python program, etc.) can contain one or more nodes.
Each node in ROS should be responsible for a single, modular purpose, such as controlling a motor or publishing sensor data.
See: :doc:`About-Nodes`

Each node can then send and receive data from other nodes via topics, services, actions, or parameters.
See: :doc:`Interfaces-Topics-Services-Actions`, :doc:`About-Client-Libraries`, and :doc:`About-Parameters`

Communication between nodes is uses Data Distrtibution Service (DDS) middleware. 
See: :doc:`nodes/About-Discovery` and :doc:`client-libraries/About-Middleware-Implementations`

ROS Graph
---------

The ROS graph is a decentralised network of modular software elements, nodes, that process data concurrently.

.. image:: nodes/Working-with-nodes/Understanding-ROS2-Nodes/images/Nodes-TopicandService.gif

A full robotic system is comprised of many nodes working in concert and the ROS graph describes how they relate to each other.



Related content
---------------
* :doc:`nodes/About-Discovery`
* :doc:`About-Client-Libraries`
* :doc:`About-Parameters`
* :doc:`Interfaces-Topics-Services-Actions`
* :doc:`nodes/Working-with-nodes`   

FAQs
----

How ROS works
=============

.. toctree::
   :maxdepth: 1
   :hidden:

Coming Soon

**[Area: Framework | Content-type: concept | Experience: beginner]**

.. contents:: Table of Contents
   :local:

Summary
-------
The ROS graph refers to the network of ROS nodes.

ROS Graph
---------

The ROS graph is a network of ROS 2 elements processing data together at the same time.
A full robotic system is comprised of many nodes working in concert.
In ROS 2, a single executable (C++ program, Python program, etc.) can contain one or more nodes.
It encompasses all executables and the connections between them if you were to map them all out and visualize them.

Each node in ROS should be responsible for a single, modular purpose, e.g. controlling the wheel motors or publishing the sensor data from a laser range-finder.
Each node can send and receive data from other nodes via topics, services, actions, or parameters.

.. image:: nodes/images/Nodes-TopicandService.gif



Related content
---------------
* :doc:`nodes/About-Discovery`
* :doc:`About-Client-Libraries`
* :doc:`About-Parameters`
* :doc:`Interfaces-Topics-Services-Actions`
* :doc:`nodes/Working-with-nodes`   

FAQs
----

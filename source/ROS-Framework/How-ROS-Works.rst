.. meta::
   :contentType: about
   :experience: beginner
   :area: framework
   :distribution: {DISTRO}
   :product: {PRODUCT}

How ROS works
=============

.. short-description::
   ROS systems use modular software elements that process data concurrently and communicate through defined interfaces.
   This article provides a high-level overview of how ROS works, including nodes, the ROS graph, communication patterns, and the tools used to inspect and interact with a system.

.. showmeta::
   :order: area, contentType, experience
   :labels: area=Area, contentType=Content type, experience=Level

.. toctree::
   :hidden:

Coming Soon

.. contents:: Table of Contents
   :depth: 2
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
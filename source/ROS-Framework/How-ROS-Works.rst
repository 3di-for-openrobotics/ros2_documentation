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
See :doc:`About-Nodes`

Each node can then send and receive data from other nodes via topics, services, actions, or parameters.
See :doc:`Interfaces-Topics-Services-Actions`, :doc:`About-Client-Libraries`, and :doc:`About-Parameters`

Communication between nodes is uses Data Distrtibution Service (DDS) middleware. 
See :doc:`nodes/About-Discovery` and :doc:`client-libraries/About-Middleware-Implementations`


ROS CLI and ROS API
^^^^^^^^^^^^^^^^^^^

If you are new to ROS, it is important to familiarise yourself with the ROS CLI. Working with the CLI will help you understand ROS elements and how to interact with them.
See :doc:`../First-Steps`.

After you are familiar with the ROS CLI, the ROS API will allow you to create your own ROS components.
See :doc:`client-libraries/About-Internal-Interfaces/About-Internal-Interfaces`.

ROS Graph
---------

A full robotic system is comprised of many nodes working in concert and the ROS graph describes the nodes in a system and their relationship to each other.

The ROS graph can be visualised in multiple ways. For example, the visualised ROS graph using rqt in :doc:`interfaces/topics/Understanding-ROS2-Topics/Understanding-ROS2-Topics` shows two nodes, ``turtlesim`` and ``teleop_turtle``.
The ``/teleop_turtle`` node publishes data to the ``/turtle1/cmd_vel`` topic, and the ``/turtlesim`` node is subscribed to that topic to receive the data.

.. image:: interfaces/topics/Understanding-ROS2-Topics/images/rqt_graph.png

Related content
---------------
* :doc:`nodes/About-Discovery`
* :doc:`About-Client-Libraries`
* :doc:`About-Parameters`
* :doc:`Interfaces-Topics-Services-Actions`
* :doc:`nodes/Working-with-nodes`   

FAQs
----

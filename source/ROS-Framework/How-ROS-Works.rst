How ROS works
=============

A ROS system is a network of cooperating processes that exchange data.
This article explains the ROS graph and how the main framework pieces relate to one another.

**Area: Framework | Content-type: about | Experience: beginner**

.. contents:: Table of Contents
   :depth: 2
   :local:

Summary
-------

The ROS system combines nodes, communication interfaces, and parameters, along with the tools and libraries used to build and inspect ROS applications.

At the heart of any ROS 2 system is the ROS graph. The ROS graph is the network of running nodes and the connections between them.
Each :doc:`node <About-Nodes>` does one logical job and communicates through :doc:`topics <interfaces/About-Topics>`, :doc:`services <interfaces/About-Services>`, and :doc:`actions <interfaces/About-Actions>`.
:doc:`Parameters <About-Parameters>` configure node behaviour.
:doc:`Client libraries <About-Client-Libraries>` provide the APIs used to create these components in code.

Topics handle continuous data streams.
Services handle short request and response calls.
Actions handle longer tasks with feedback or cancellation.
ROS command-line tools allow you to explore a live graph before writing your own nodes, while client libraries let you implement the same concepts in code.

The ROS graph
-------------

The ROS graph is the set of running nodes and the connections between them.
Those connections carry data and requests through the system while the nodes run together.

A full robotic system is usually many nodes working together.
In ROS, a single executable, for example a C++ or Python program, can contain one or more nodes.

.. mermaid::

   flowchart LR
      N1[Node A] -->|topic| N2[Node B]
      N1 -->|service| N3[Node C]
      N2 -->|action| N4[Node D]

This diagram is simplified.
Real systems often combine several of these patterns inside the same nodes.

Nodes
-----

Each node is typically responsible for one modular purpose, for example, controlling wheel motors or publishing laser range-finder data.
Nodes can communicate with other nodes in the same process, in another process, or on another machine.

A node can publish and subscribe to topics, act as a service client or server, act as an action client or server, and expose parameters, often all at once.

.. image:: nodes/Working-with-nodes/Understanding-ROS2-Nodes/images/Nodes-TopicandService.gif
   :alt: Diagram of nodes connected by a topic and a service

Nodes find one another through distributed :doc:`discovery <nodes/About-Discovery>`.

For more information, see :doc:`About nodes <About-Nodes>`.

Topics
------

Topics are the main way continuous data moves through the graph.
They use a publish and subscribe pattern: publishers send messages on a named topic, and subscribers receive those messages.

A node may publish to any number of topics and subscribe to any number of topics at the same time.
Typical uses of topics include sensor streams, robot state, and velocity commands.

.. image:: interfaces/topics/Understanding-ROS2-Topics/images/Topic-SinglePublisherandSingleSubscriber.gif
   :alt: One publisher sending messages to one subscriber over a topic

.. image:: interfaces/topics/Understanding-ROS2-Topics/images/Topic-MultiplePublisherandMultipleSubscriber.gif
   :alt: Multiple publishers and subscribers sharing topics

Because any number of subscribers can listen to the same topic, introspection tools such as ``ros2 topic echo`` can inspect the stream without changing the original publishers or subscribers.

For more information, see :doc:`About topics <interfaces/About-Topics>`.

Services
--------

Services use a call-and-response model.
A client sends a request, and a server returns a single response.

Use topics when you need continuous updates.
Use services when you need an on-demand result for a short task, such as spawning an entity or asking for a quick computation.

.. image:: interfaces/services/Working-with-services/Understanding-ROS2-Services/images/Service-SingleServiceClient.gif
   :alt: One service client calling one service server

.. image:: interfaces/services/Working-with-services/Understanding-ROS2-Services/images/Service-MultipleServiceClient.gif
   :alt: Multiple service clients calling the same service server

For more information, see :doc:`About services <interfaces/About-Services>`.

Actions
-------

Actions are for long-duration tasks.
They consist of a goal, feedback while the task runs, and a result when it finishes.
Unlike a service call, an action goal can be cancelled while it is still running.

An action client sends a goal to an action server.
The server acknowledges the goal, streams feedback, and returns a result.

.. image:: interfaces/actions/Working-with-actions/Understanding-ROS2-Actions/images/Action-SingleActionClient.gif
   :alt: Action client sending a goal to an action server and receiving feedback

Typical uses of actions include navigating to a pose or running any procedure that takes noticeable time and needs progress updates.

For more information, see :doc:`About actions <interfaces/About-Actions>` and :doc:`Interfaces (topics, services, actions) <Interfaces-Topics-Services-Actions>`.

Parameters
----------

A parameter is a configuration value of a node.
You can think of parameters as node settings.

A node can store parameters as integers, floats, booleans, strings, and lists.
In ROS, each node maintains its own parameters.
You can set them at startup and often change them while the node is running, without changing the node code.

Parameters configure behaviour in the graph.
They are not a data stream like a topic.

For more information, see :doc:`About parameters <About-Parameters>`.

Command-line tools and APIs
---------------------------

The ROS command-line interface (CLI) and the ROS application programming interfaces (APIs) both interact with the ROS graph, but they are different tools with different purposes.

The CLI lets you work with a live graph: list nodes, inspect topics, call services, send action goals, and set parameters.
When you are learning the framework, learn the CLI first.
It shows you the core ROS concepts and how to interact with them before you create those pieces yourself.

:doc:`Client libraries <About-Client-Libraries>` provide the APIs you use to write nodes and other ROS components in languages such as C++ and Python.
Nodes written with different client libraries can still communicate because they share the same interface definitions and middleware.

Related content
---------------

* :doc:`About nodes <About-Nodes>`
* :doc:`About discovery <nodes/About-Discovery>`
* :doc:`Interfaces (topics, services, actions) <Interfaces-Topics-Services-Actions>`
* :doc:`About topics <interfaces/About-Topics>`
* :doc:`About services <interfaces/About-Services>`
* :doc:`About actions <interfaces/About-Actions>`
* :doc:`About parameters <About-Parameters>`
* :doc:`About client libraries <About-Client-Libraries>`

FAQs
----

What is the ROS graph?
   The ROS graph is the set of running nodes in a ROS system and the connections between them.
   Those connections are mainly topics, services, and actions, while parameters configure individual nodes.

What is the difference between a node and an executable?
   An executable is a program you run.
   That program can contain one or more nodes.
   The graph is concerned with the nodes and how they communicate, not only with the process that hosts them.

When should I use a topic, a service, or an action?
   Use a topic for continuous data that may have many publishers or subscribers.
   Use a service for a short request that expects one response.
   Use an action for a longer task that needs feedback or may need to be cancelled.
   See :doc:`Interfaces (topics, services, actions) <Interfaces-Topics-Services-Actions>` for a side-by-side comparison.

Do I need to learn the CLI before the client library APIs?
   Yes, when you are learning the framework.
   The CLI shows the same concepts you later create in code: nodes, interfaces, and parameters in a live system.
   Client libraries are the APIs for building those components yourself.

Are parameters a communication interface like topics?
   No.
   Parameters configure a node.
   Topics, services, and actions are the main ways nodes exchange data with each other.

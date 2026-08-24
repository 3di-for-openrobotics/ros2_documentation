.. redirect-from::

    About-ROS-2-Parameters
    Concepts/About-ROS-2-Parameters
    Concepts/Basic/About-Parameters

Parameters
==========

.. toctree::
   :maxdepth: 1
   :hidden:

   parameters/Working-with-parameters

Parameters are configuration values stored by each node in the ROS graph.
Parameters are used to configure nodes at startup and during runtime, without changing the code.
This article describes parameters and their role in ROS. 


**[Area: Framework | Content-type: Concept | Experience: Beginner]**

.. contents:: Table of Contents
   :depth: 2
   :local:

Summary
-------

Parameters are used to configure nodes at startup and during runtime, without changing the code.
Parameters are addressed by node name, node namespace (optional), parameter name, and parameter namespace.

Each parameter consists of:

* a key - a string
* a value - one of the following types: ``bool``, ``int64``, ``float64``, ``string``, ``byte[]``, ``bool[]``, ``int64[]``, ``float64[]`` or ``string[]``.
* a descriptor - empty by default, but can contain parameter descriptions, value ranges, type information, and additional constraints.

The ``ros2 param`` command and client libraries allow you to set and change parameters.

For a hands-on tutorial with ROS parameters see :doc:`/parameters/Working-with-parameters/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters`.

Core ROS packages
-----------------
Client library support includes:
 * **C++ (rclcpp)**: see :doc:`../client-libraries/Working-with-Client-Libraries/Using-Parameters-In-A-Class-CPP` and :doc:`../parameters/Working-with-parameters/Monitoring-For-Parameter-Changes-CPP`.
 * **Python (rclpy)**: see :doc:`../client-libraries/Working-with-Client-Libraries/Using-Parameters-In-A-Class-Python` and :doc:`../parameters/Working-with-parameters/Monitoring-For-Parameter-Changes-Python`.


Parameters
----------
Parameters in ROS are associated with individual nodes.
Parameters are used to configure nodes at startup and during runtime, without changing the code.
The lifetime of a parameter is tied to the lifetime of the node (though the node could implement some sort of persistence to reload values after restart).

Parameters are addressed by node name, node namespace (optional), parameter name, and parameter namespace.

Each parameter on a ROS 2 node has one of the pre-defined parameter types:
* ``bool``
* ``int64``
* ``float64``
* ``string``
* ``byte[]``
* ``bool[]``
* ``int64[]``
* ``float64[]``
* ``string[]``

By default all descriptors are empty, but can contain parameter descriptions, value ranges, type information, and additional constraints.

Startup and runtime
^^^^^^^^^^^^^^^^^^^



Parameter callbacks
^^^^^^^^^^^^^^^^^^^

A ROS node can optionally register three different types of callbacks to be informed when changes are happening to parameters.

* Pre-set parameter callback When it is called, it can modify the ``Parameter`` list to change, add, or remove entries.
* Set parameter callback The main purpose of this callback is to give the user the ability to inspect the upcoming change to the parameter and explicitly reject the change.
* Post-set parameter callback The main purpose of this callback is to give the user the ability to react to changes from parameters that have successfully been accepted.

Related content
---------------
* :doc:`parameters/Working-with-parameters/Understanding-ROS2-Parameters/Understanding-ROS2-Parameters`
* :doc:`../Developer-Tools/Launch/Launch-Main``

FAQs
----
<placeholder>
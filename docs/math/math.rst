=============
Math Overview
=============

The underpinings of validation in Schematics can be described as a composition
of functions that are applied over the input to generate the output data.

These functions include transformations on both the field values and the field
names such that the program has complete control over how the input data is
mapped to the system model, and how the system model is mapped to external
output.


TLA+
====

To represent the algorithm the TLA+ logic is used, since it allows for the easy
representation of states and the description of the algorithm in PlusCal, a
pseudocode replacement language that converts to the formal TLA+. The final
program can then be model checked for debugging and correctness.


Algorithm
=========

A :download:`pretty-print version <schematics.pdf>` can be downloaded, it uses
the mathematical symbols to render the functions.

The TLA+ source can be seen below:

.. literalinclude:: schematics.tla
  :linenos:


Models
------

Given the program we can then for example prove the model such that for the
given input constants:

.. code-block:: none

  InputSet == { <<"key1", "val1">>, <<"in_key2", "val2">> }
  InputMap == { <<"in_key2", "key2">> }
  AllowSet == { "key2" }
  OutputMap == { <<"key2", "out_key2">> }

The final state of the ``OutputSet`` will be: ``{<<"out_key2", "val2">>}``.

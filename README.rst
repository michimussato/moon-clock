.. These are examples of badges you might want to add to your README:
   please update the URLs accordingly

    .. image:: https://api.cirrus-ci.com/github/<USER>/moon-clock.svg?branch=main
        :alt: Built Status
        :target: https://cirrus-ci.com/github/<USER>/moon-clock
    .. image:: https://readthedocs.org/projects/moon-clock/badge/?version=latest
        :alt: ReadTheDocs
        :target: https://moon-clock.readthedocs.io/en/stable/
    .. image:: https://img.shields.io/coveralls/github/<USER>/moon-clock/main.svg
        :alt: Coveralls
        :target: https://coveralls.io/r/<USER>/moon-clock
    .. image:: https://img.shields.io/pypi/v/moon-clock.svg
        :alt: PyPI-Server
        :target: https://pypi.org/project/moon-clock/
    .. image:: https://img.shields.io/conda/vn/conda-forge/moon-clock.svg
        :alt: Conda-Forge
        :target: https://anaconda.org/conda-forge/moon-clock
    .. image:: https://pepy.tech/badge/moon-clock/month
        :alt: Monthly Downloads
        :target: https://pepy.tech/project/moon-clock
    .. image:: https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter
        :alt: Twitter
        :target: https://twitter.com/moon-clock

.. image:: https://img.shields.io/badge/-PyScaffold-005CA0?logo=pyscaffold
    :alt: Project generated with PyScaffold
    :target: https://pyscaffold.org/

|

==========
moon-clock
==========


    Add a short description here!


A longer description of your project goes here...


Installation
============

.. code-block:: console

   pip install moon-clock


Usage
=====

.. code-block:: python3

   import moon_clock
   clock = moon_clock.MoonClock().get_clock()
   clock.save(r'moon_clock.png')


Examples
========

Shortly before 11 PM, with the moon at it's highest:
 .. image:: docs/media/clock.png
     :alt: Moon Night

About 4:15 PM, shortly before sunset:
 .. image:: docs/media/moon_clock.png
     :alt: Moon Afternoon


.. _pyscaffold-notes:

Note
====

This project has been set up using PyScaffold 4.6. For details and usage
information on PyScaffold see https://pyscaffold.org/.

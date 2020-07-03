scikit-surgeryutils
===============================

.. image:: https://github.com/UCL/scikit-surgeryutils /raw/master/project-icon.png
   :height: 128px
   :width: 128px
   :target: https://github.com/UCL/scikit-surgeryutils 
   :alt: Logo

.. image:: https://github.com/UCL/scikit-surgeryutils/workflows/.github/workflows/ci.yml/badge.svg
   :target: https://github.com/UCL/scikit-surgeryutils/actions
   :alt: GitHub Actions CI statuss

.. image:: https://coveralls.io/repos/github/UCL/scikit-surgeryutils/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/UCL/scikit-surgeryutils?branch=master
    :alt: Test coverage

.. image:: https://readthedocs.org/projects/scikit-surgeryutils /badge/?version=latest
    :target: http://scikit-surgeryutils .readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

scikit-surgeryutils is a python project containing small demo apps,
and small command apps, the sort of thing that probably doesn't warrant
its own project.

* sksurgeryvideolag.py - shows a millisecond timer and video image to measure lag.
* sksurgerycharucotest.py - extracts charuco points and annotates video image with each id detected.
* sksurgeryrendermodelslikecamera.py - renders a VTK model, using OpenCV camera intrinsics.

scikit-surgeryutils is part of the `SNAPPY`_ software project, developed at the `Wellcome EPSRC Centre for Interventional and Surgical Sciences`_, part of `University College London (UCL)`_.


Installing
----------

You can pip install directly from the repository as follows:

::

    pip install git+https://github.com/UCL/scikit-surgeryutils


Developing
----------

Cloning
^^^^^^^

You can clone the repository using the following command:

::

    git clone https://github.com/UCL/scikit-surgeryutils


Running the tests
^^^^^^^^^^^^^^^^^

You can run the unit tests by installing and running tox:

::

    pip install tox
    tox

Encountering Problems?
^^^^^^^^^^^^^^^^^^^^^^
Please check list of `common issues`_.

Contributing
^^^^^^^^^^^^

Please see the `contributing guidelines`_.


Useful links
^^^^^^^^^^^^

* `Source code repository`_
* `Documentation`_


Licensing and copyright
-----------------------

Copyright 2018 University College London.
scikit-surgeryutils is released under the BSD-3 license. Please see the `license file`_ for details.


Acknowledgements
----------------

Supported by `Wellcome`_ and `EPSRC`_.


.. _`Wellcome EPSRC Centre for Interventional and Surgical Sciences`: http://www.ucl.ac.uk/weiss
.. _`source code repository`: https://github.com/UCL/scikit-surgeryutils
.. _`Documentation`: https://scikit-surgeryutils.readthedocs.io
.. _`SNAPPY`: https://weisslab.cs.ucl.ac.uk/WEISS/PlatformManagement/SNAPPY/wikis/home
.. _`University College London (UCL)`: http://www.ucl.ac.uk/
.. _`Wellcome`: https://wellcome.ac.uk/
.. _`EPSRC`: https://www.epsrc.ac.uk/
.. _`contributing guidelines`: https://github.com/UCL/scikit-surgeryutils/blob/master/CONTRIBUTING.rst
.. _`license file`: https://github.com/UCL/scikit-surgeryutils/blob/master/LICENSE
.. _`common issues`: https://weisslab.cs.ucl.ac.uk/WEISS/SoftwareRepositories/SNAPPY/scikit-surgery/wikis/Common-Issues

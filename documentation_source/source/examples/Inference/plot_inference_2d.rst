.. only:: html

    .. note::
        :class: sphx-glr-download-link-note

        Click :ref:`here <sphx_glr_download_examples_Inference_plot_inference_2d.py>`     to download the full example code
    .. rst-class:: sphx-glr-example-title

    .. _sphx_glr_examples_Inference_plot_inference_2d.py:


2D Posterior analysis of the Bayesian inference
-----------------------------------------------

All plotting in GeoBIPy can be carried out using the 3D inference class


.. code-block:: default

    import matplotlib.pyplot as plt
    from geobipy import example_path
    from geobipy import Inference3D
    import numpy as np









Inference for a line of inferences
++++++++++++++++++++++++++++++++++

We can instantiate the inference handler by providing a path to the directory containing
HDF5 files generated by GeoBIPy.

The InfereceXD classes are low memory.  They only read information from the HDF5 files
as and when it is needed.

The first time you use these classes to create plots, expect long initial processing times.
I precompute expensive properties and store them in the HDF5 files for later use.


.. code-block:: default

    results_3d = Inference3D(directory=example_path, system_file_path=example_path+"//../../Data")








We can grab the results for an entire line of data


.. code-block:: default

    results_2d = results_3d.line(30060.0)








Plot a location map of the data point locations along the line


.. code-block:: default

    plt.figure()
    results_2d.scatter2D()




.. image:: /examples/Inference/images/sphx_glr_plot_inference_2d_001.png
    :alt: plot inference 2d
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none


    (<AxesSubplot:xlabel='Easting (m)', ylabel='Northing (m)'>, <matplotlib.collections.PathCollection object at 0x12f4c8dc0>, <matplotlib.colorbar.Colorbar object at 0x12f542640>)



Before we start plotting cross sections, lets set some common keywords


.. code-block:: default

    xAxis = 'y'
    kwargs = { "log" : 10, # I want to plot the log conductivity
               "reciprocateParameter" : True, # Plot resistivity instead?
               "vmin" : 1.0, # Set the minimum colour bar range in log space
               "vmax" : np.log10(500.0), # Set the maximum colour bar range in log space
               "xAxis" : xAxis # Set the axis along which to display attributes
               }









We can show a basic cross-section of the parameter inverted for


.. code-block:: default

    plt.figure()
    plt.subplot(311)
    results_2d.plotMeanModel(**kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);

    # By adding the useVariance keyword, we can make regions of lower confidence more transparent
    plt.subplot(312)
    results_2d.plotMeanModel(useVariance=True, **kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);

    # We can also choose to keep parameters above the DOI opaque.
    plt.subplot(313)
    results_2d.plotMeanModel(useVariance=True, only_below_doi=True, **kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);




.. image:: /examples/Inference/images/sphx_glr_plot_inference_2d_002.png
    :alt: plot inference 2d
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')
    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')
    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')

    (900.0, 1400.0)



We can plot the parameter values that produced the highest posterior


.. code-block:: default

    plt.figure()
    plt.subplot(311)
    results_2d.plotBestModel(**kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);

    # By adding the useVariance keyword, we can shade regions of lower confidence
    plt.subplot(312)
    results_2d.plotBestModel(useVariance=True, **kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);

    # We can also choose to keep parameters above the DOI opaque.
    plt.subplot(313)
    results_2d.plotBestModel(useVariance=True, only_below_doi=True, **kwargs);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);




.. image:: /examples/Inference/images/sphx_glr_plot_inference_2d_003.png
    :alt: plot inference 2d
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')
    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')
    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("viridis"))
      kwargs['cmap'].set_bad(color='white')

    (900.0, 1400.0)



Now we can start plotting some more interesting posterior properties.
How about the confidence?


.. code-block:: default

    plt.figure(figsize=(12, 4))
    results_2d.plotConfidence(xAxis=xAxis);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);





.. image:: /examples/Inference/images/sphx_glr_plot_inference_2d_004.png
    :alt: plot inference 2d
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("plasma"))
      kwargs['cmap'].set_bad(color='white')
    /Users/nfoks/codes/repositories/geobipy/geobipy/src/inversion/Inference2D.py:1303: UserWarning: FixedFormatter should only be used together with FixedLocator
      cb.ax.set_yticklabels(['Less', '', '', '', '', 'More'])

    (900.0, 1400.0)



We can take the interface depth posterior for each data point,
and display an interface probability cross section
This posterior can be washed out, so the clim_scaling keyword lets me saturate
the top and bottom 0.5% of the colour range


.. code-block:: default

    plt.figure(figsize=(12, 4))
    results_2d.plotInterfaces(xAxis=xAxis, cmap='Greys', clim_scaling=0.5);
    results_2d.plotDataElevation(linewidth=0.3, xAxis=xAxis);
    results_2d.plotElevation(linewidth=0.3, xAxis=xAxis);
    plt.ylim([900.0, 1400.0]);




.. image:: /examples/Inference/images/sphx_glr_plot_inference_2d_005.png
    :alt: plot inference 2d
    :class: sphx-glr-single-img


.. rst-class:: sphx-glr-script-out

 Out:

 .. code-block:: none

    /Users/nfoks/codes/repositories/geobipy/geobipy/src/base/customPlots.py:649: MatplotlibDeprecationWarning: You are modifying the state of a globally registered colormap. In future versions, you will not be able to modify a registered colormap in-place. To remove this warning, you can make a copy of the colormap first. cmap = copy.copy(mpl.cm.get_cmap("Greys"))
      kwargs['cmap'].set_bad(color='white')

    (900.0, 1400.0)



We can plot the posteriors along the line as a shaded histogram


.. code-block:: default


    # results_2d.nLayers










.. rst-class:: sphx-glr-timing

   **Total running time of the script:** ( 0 minutes  33.478 seconds)


.. _sphx_glr_download_examples_Inference_plot_inference_2d.py:


.. only :: html

 .. container:: sphx-glr-footer
    :class: sphx-glr-footer-example



  .. container:: sphx-glr-download sphx-glr-download-python

     :download:`Download Python source code: plot_inference_2d.py <plot_inference_2d.py>`



  .. container:: sphx-glr-download sphx-glr-download-jupyter

     :download:`Download Jupyter notebook: plot_inference_2d.ipynb <plot_inference_2d.ipynb>`


.. only:: html

 .. rst-class:: sphx-glr-signature

    `Gallery generated by Sphinx-Gallery <https://sphinx-gallery.github.io>`_

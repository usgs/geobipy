""" @Histogram_Class
Module describing an efficient histogram class
"""
from ...classes.mesh.RectilinearMesh1D import RectilinearMesh1D
from ...classes.core import StatArray
from ...base import customFunctions as cF
from ...base import customPlots as cP
from .Distribution import Distribution
import numpy as np
import matplotlib.pyplot as plt
import sys

from scipy.signal import find_peaks
from scipy.optimize import curve_fit
from scipy.stats import norm

from copy import deepcopy


class Histogram1D(RectilinearMesh1D):
    """1D Histogram class that updates efficiently.

    Fast updating relies on knowing the bins ahead of time.

    Histogram1D(values, bins, binCentres, log, relativeTo)

    Parameters
    ----------
    bins : geobipy.StatArray or array_like, optional
        Specify the bin edges for the histogram. Can be regularly or irregularly increasing.
    binCentres : geobipy.StatArray or array_like, optional
        Specify the bin centres for the histogram. Can be regular or irregularly sized.
    log : 'e' or float, optional
        Entries are given in linear space, but internally bins and values are logged.
        Plotting is in log space.
    relativeTo : float, optional
        If a float is given, updates will be relative to this value.

    Returns
    -------
    out : Histogram1D
        1D histogram

    """

    def __init__(self, bins=None, binCentres=None, log=None, relativeTo=0.0, values=None):
        """ Initialize a histogram """

        # Allow an null instantiation
        if (bins is None and binCentres is None):
            self._counts = None
            return

        # Initialize the parent class
        super().__init__(cellEdges=bins, cellCentres=binCentres, log=log, relativeTo=relativeTo)

        self._counts = StatArray.StatArray(self.nCells, 'Frequency', dtype=np.int64)

        if not values is None:
            self.update(values)


    def __getitem__(self, slic):
        """Slice into the class. """

        assert np.shape(slic) == (), ValueError("slic must have one dimension.")


        bins = super().__getitem__(slic).cellEdges

        out = Histogram1D()

        out._cellEdges = bins
        out.log = self.log
        out._relativeTo = self._relativeTo

        out._counts = self.counts[slic]
        return out


    @property
    def cdf(self):
        out = np.cumsum(self.counts)
        out = out / out[-1]
        return out

    @property
    def counts(self):
        return self._counts

    @property
    def bins(self):
        return self.cellEdges

    @bins.setter
    def bins(self, values):
        self.cellEdges = values

    @property
    def binCentres(self):
        return self.cellCentres

    @binCentres.setter
    def binCentres(self, values):
        self.cellCentres = values

    @property
    def nBins(self):
        return self.nCells

    @property
    def nSamples(self):
        return self._counts.sum()


    def __deepcopy__(self, memo):
        out = type(self)()
        out._cellCentres = self._cellCentres.deepcopy()
        out._cellEdges = self._cellEdges.deepcopy()
        out.isRegular = self.isRegular
        out.dx = self.dx
        out._counts = self._counts.deepcopy()
        out.log = self.log
        out._relativeTo = self._relativeTo

        return out


    def combine(self, other):
        """Combine two histograms together.

        Using the bin centres of other, finds the corresponding bins in self.  The counts of other are then added to self.

        Parameters
        ----------
        other : geobipy.Histogram1D
            A histogram to combine.

        """

        cc = other.cellCentres

        cc = cF._power(cc, other.log)

        iBin = self.cellIndex(cc, clip=True)
        self._counts[iBin] = self._counts[iBin] + other.counts


    def credibleIntervals(self, percent=95.0, log=None):
        """Gets the credible intervals.

        Parameters
        ----------
        percent : float
            Confidence percentage.
        log : 'e' or float, optional
            Take the log of the credible intervals to a base. 'e' if log = 'e', or a number e.g. log = 10.

        Returns
        -------
        med : array_like
            Contains the median. Has size equal to arr.shape[axis].
        low : array_like
            Contains the lower interval.
        high : array_like
            Contains the upper interval.

        """

        total = self._counts.sum()
        p = 0.01 * percent
        cs = np.cumsum(self._counts / total)

        ixM = np.searchsorted(cs, 0.5)
        ix1 = np.searchsorted(cs, (1.0 - p))
        ix2 = np.searchsorted(cs, p)

        x = self.bins.internalEdges()
        med = x[ixM]
        low = x[ix1]
        high = x[ix2]

        if (not log is None):
            med, dum = cF._log(med, log=log)
            low, dum = cF._log(low, log=log)
            high, dum = cF._log(high, log=log)

        return (med, low, high)


    def estimatePdf(self):
        return StatArray.StatArray(np.divide(self._counts, np.sum(self._counts)), name='Density')


    def findPeaks(self, width, **kwargs):
        """Identify peaks in the histogram.

        See Also
        --------
        scipy.spatial.find_peaks

        """

        return find_peaks(self.estimatePdf(),  width=width, **kwargs)


    def _sum_of_gaussians(self, x, *params):
        y = np.zeros_like(x)

        nG = np.int(len(params)/3)

        for i in range(nG):
            i1 = i*3
            y += params[i1 + 2] * norm.pdf(x, params[i1], params[i1+1])

        return y


    def fit_mixture(self, mixture_type='gaussian', nSamples=100000, log=None, mean_bounds=None, variance_bounds=None, k=[1, 10], tolerance=0.05):
        """Uses Gaussian mixture models to fit the histogram.

        Starts at the minimum number of clusters and adds clusters until the BIC decreases less than the tolerance.

        Parameters
        ----------
        nSamples

        log

        mean_bounds

        variance_bounds

        k : ints
            Two ints with starting and ending # of clusters

        tolerance

        """

        from sklearn.mixture import GaussianMixture
        from smm import SMM

        if mixture_type.lower() == 'gaussian':
            mod = GaussianMixture
        else:
            mod = SMM

        # Samples the histogram
        X = self.sample(nSamples)[:, None]
        X, _ = cF._log(X, log)

        # of clusters
        k_ = k[0]

        best = mod(n_components=k_).fit(X)
        # best = GaussianMixture(k_).fit(X)
        BIC0 = best.bic(X)

        k_ += 1
        go = k_ < k[1]

        while go:
            model = mod(n_components=k_).fit(X)
            # model = GaussianMixture(k_).fit(X)
            BIC1 = model.bic(X)

            percent_reduction = np.abs((BIC1 - BIC0)/BIC0)

            go = True
            if BIC1 < BIC0:
                best = model
                BIC0 = BIC1

            else:
                go = False

            if (percent_reduction < tolerance):
                go = False

            k_ += 1
            go = go & (k_ < k[1])


        active = np.ones(best.n_components, dtype=np.bool)

        means = np.squeeze(best.means_)
        try:
            variances = np.squeeze(best.covariances_)
        except:
            variances = np.squeeze(best.covariances)

        if not mean_bounds is None:
            active = (mean_bounds[0] <= means) & (means <= mean_bounds[1])

        if not variance_bounds is None:
            active = (variance_bounds[0] <= variances) & (variances <= variance_bounds[1]) & active

        return best, np.atleast_1d(active)


    def fitMajorPeaks(self, log=None, mean_bounds=None, constrain_loc = True, variance_upper_bound=None, maxDistributions = None, tolerance=0.05):
        """Iteratively fits the histogram with an increasing number of distributions until the fit changes by less than a tolerance.

        """

        if not mean_bounds is None:
            assert np.size(mean_bounds) == 2, ValueError("mean_bounds must have size 2")

        x, dum = cF._log(self.binCentres, log)
        yData = self.estimatePdf()

        # First find the maximum width that finds a peak
        width = self.nBins + 1

        go = True
        while go:
            width -= 1
            iPeaks = self.findPeaks(width=width)[0]

            if not mean_bounds is None:
                keepPeaks = np.where((mean_bounds[0] < x[iPeaks]) & (x[iPeaks] < mean_bounds[1]))[0]
                iPeaks = iPeaks[keepPeaks]
            nPeaks = np.size(iPeaks)
            go = nPeaks == 0

        # Carry out the first fitting.
        guess = np.ones(nPeaks * 3)
        lowerBounds = np.zeros(nPeaks * 3)
        upperBounds = np.full(nPeaks * 3, np.inf)
        i = 3 * np.arange(nPeaks)
        guess[i] = x[iPeaks]

        if constrain_loc:
            lowerBounds[i] = x[iPeaks] - 1e-6
            upperBounds[i] = x[iPeaks] + 1e-6

        if not variance_upper_bound is None:
            upperBounds[1::3] = variance_upper_bound
            guess[1::3] = 0.5 * (lowerBounds[1::3] + upperBounds[1::3])

        bounds = (lowerBounds, upperBounds)

        iWhere = np.where(yData > 0.0)[0]

        xd = x[iWhere]
        yd = yData[iWhere]

        # Fit with a single distribution
        model, pcov = curve_fit(self._sum_of_gaussians, xdata=xd, ydata=yd, p0=guess, bounds=bounds)
        model = np.asarray(model)

        yFit = self._sum_of_gaussians(x, *model)
        fit0 = np.linalg.norm((yData - yFit))

        go = True
        while go:

            # Find the next width that produces more peaks.
            no_new_peaks = True
            n_new_peaks = nPeaks
            while no_new_peaks and width > 1:
                width -= 1
                iPeaks = self.findPeaks(width=width)[0]
                if not mean_bounds is None:
                    keepPeaks = np.where((mean_bounds[0] < x[iPeaks]) & (x[iPeaks] < mean_bounds[1]))[0]
                    iPeaks = iPeaks[keepPeaks]
                n_new_peaks = np.size(iPeaks)
                no_new_peaks = nPeaks == n_new_peaks

            nPeaks = n_new_peaks

            # Perform the new fit
            guess = np.ones(nPeaks * 3)
            lowerBounds = np.zeros(nPeaks * 3)
            upperBounds = np.full(nPeaks * 3, np.inf)

            i = 3 * np.arange(nPeaks)
            guess[i] = x[iPeaks]

            if constrain_loc:
                lowerBounds[i] = x[iPeaks] - 1e-6
                upperBounds[i] = x[iPeaks] + 1e-6

            if not variance_upper_bound is None:
                upperBounds[1::3] = variance_upper_bound
                guess[1::3] = 0.5 * (lowerBounds[1::3] + upperBounds[1::3])

            bounds = (lowerBounds, upperBounds)
            new_model, pcov = curve_fit(self._sum_of_gaussians, xdata=xd, ydata=yd, p0=guess, bounds=bounds)
            new_model = np.asarray(new_model)

            yFit = self._sum_of_gaussians(x, *new_model)
            fit = np.linalg.norm((yData - yFit))

            # if the new fit is better than the old one by a suitable increase in percentage, keep it.
            # otherwise, quit.
            fitChange = np.abs(fit0 - fit)
            percentChange = fitChange / fit0

            width_gt_one = width > 1
            good_change = percentChange > tolerance

            # Continue if we have a width > 1, and the change is still good
            go = width_gt_one and good_change
            if not maxDistributions is None:
                go = go and nPeaks < maxDistributions

            if go:
                model = new_model.copy()
                fit0 = fit

        dists = []
        for i in range(np.int(len(model)/3)):
            dists.append(Distribution("normal", model[3*i], model[(3*i)+1]))

        return dists, model[2::3]


    def sample(self, nSamples):
        """Generates samples from the histogram.

        A uniform distribution is used for each bin to generate samples.
        The number of samples generated per bin is scaled by the count for that bin using the requested number of samples.

        parameters
        ----------
        nSamples : int
            Number of samples to generate.

        Returns
        -------
        out : geobipy.StatArray
            The samples.

        """
        values = np.random.rand(np.int(nSamples)) * self.cdf[-1]
        return np.interp(values, np.hstack([0, self.cdf]), self.bins)


    def update(self, values, clip=True, trim=False):
        """Update the histogram by counting the entry of values into the bins of the histogram.

        Updates the bin counts in the histogram using fast methods.
        The values are clipped so that values outside the bins are forced inside.
        Optionally, one can trim the values so that those outside the bins are not counted.

        Parameters
        ----------
        values : array_like
            Increments the count for the bin that each value falls into.
        trim : bool
            A negative index which would normally wrap will clip to 0 and self.bins.size instead.

        """
        iBin = np.atleast_1d(self.cellIndex(values, clip=clip, trim=trim))
        tmp = np.bincount(iBin, minlength = self.nBins)

        self._counts += tmp


    def pcolor(self, **kwargs):
        """pcolor the histogram

        Other Parameters
        ----------------
        alpha : scalar or array_like, optional
            If alpha is scalar, behaves like standard matplotlib alpha and opacity is applied to entire plot
            If array_like, each pixel is given an individual alpha value.
        log : 'e' or float, optional
            Take the log of the colour to a base. 'e' if log = 'e', and a number e.g. log = 10.
            Values in c that are <= 0 are masked.
        equalize : bool, optional
            Equalize the histogram of the colourmap so that all colours have an equal amount.
        nbins : int, optional
            Number of bins to use for histogram equalization.
        xscale : str, optional
            Scale the x axis? e.g. xscale = 'linear' or 'log'
        yscale : str, optional
            Scale the y axis? e.g. yscale = 'linear' or 'log'.
        flipX : bool, optional
            Flip the X axis
        flipY : bool, optional
            Flip the Y axis
        grid : bool, optional
            Plot the grid
        noColorbar : bool, optional
            Turn off the colour bar, useful if multiple customPlots plotting routines are used on the same figure.
        trim : bool, optional
            Set the x and y limits to the first and last non zero values along each axis.

        See Also
        --------
        geobipy.customPlots.pcolor : For additional keywords

        """
        kwargs['y'] = self.bins
        return super().pcolor(self._counts, **kwargs)


    def plot(self, rotate=False, flipX=False, flipY=False, trim=True, normalize=False, **kwargs):
        """ Plots the histogram """

        ax = cP.hist(self.counts, self.bins, rotate=rotate, flipX=flipX, flipY=flipY, trim=trim, normalize=normalize, **kwargs)
        return ax


    def plot_as_line(self, rotate=False, flipX=False, flipY=False, trim=True, normalize=False, **kwargs):

        x = self.binCentres

        ax = self.counts.plot(x=x, **kwargs)


    def hdfName(self):
        """ Reprodicibility procedure """
        return('Histogram1D()')


    def createHdf(self, parent, myName, withPosterior=True, nRepeats=None, fillvalue=None):
        """ Create the hdf group metadata in file
        parent: HDF object to create a group inside
        myName: Name of the group
        """
        # create a new group inside h5obj
        grp = parent.create_group(myName)
        grp.attrs["repr"] = self.hdfName()

        self._counts.createHdf(grp, 'counts', nRepeats=nRepeats, fillvalue=fillvalue)

        if not self.log is None:
            grp.create_dataset('log', data = self.log)

        self._cellEdges.toHdf(grp, 'bins')
        self.relativeTo.createHdf(grp, 'relativeTo', nRepeats=nRepeats, fillvalue=fillvalue)


    def writeHdf(self, parent, myName, withPosterior=True, index=None):
        """ Write the StatArray to an HDF object
        parent: Upper hdf file or group
        myName: object hdf name. Assumes createHdf has already been called
        create: optionally create the data set as well before writing
        """
        self._counts.writeHdf(parent, myName+'/counts', index=index)

        self.relativeTo.writeHdf(parent, myName+'/relativeTo', index=index)
        # self._cellEdges.writeHdf(parent, myName+'/bins', index=index)


    def toHdf(self, h5obj, myName):
        """ Write the StatArray to an HDF object
        h5obj: :An HDF File or Group Object.
        """
        # Create a new group inside h5obj
        grp = h5obj.create_group(myName)
        grp.attrs["repr"] = self.hdfName()
        self._cellEdges.toHdf(grp, 'bins')
        self._counts.toHdf(grp, 'counts')
        if not self.log is None:
            grp.create_dataset('log', data = self.log)
        self.relativeTo.toHdf(grp, 'relativeTo')


    def fromHdf(self, grp, index=None):
        """ Reads in the object froma HDF file """

        try:
            item = grp.get('relativeTo')
            obj = eval(cF.safeEval(item.attrs.get('repr')))
            relativeTo = obj.fromHdf(item, index=index)
        except:
            relativeTo = 0.0

        item = grp.get('bins')
        obj = eval(cF.safeEval(item.attrs.get('repr')))
        bins = obj.fromHdf(item)

        if np.ndim(bins) == 2:
            bins = bins[0, :]

        item = grp.get('counts')
        obj = eval(cF.safeEval(item.attrs.get('repr')))

        if (index is None):
            counts = obj.fromHdf(item)
        else:
            counts = obj.fromHdf(item, index=index)

        try:
            log = np.asscalar(np.asarray(grp.get('log')))
        except:
            log = None

        if bins.shape[-1] == counts.shape[-1]:
            Hist = Histogram1D(binCentres = bins)
        else:
            Hist = Histogram1D(bins = bins)

        Hist._counts = counts
        Hist.log = log
        Hist.relativeTo = relativeTo

        return Hist


    def summary(self, out=False):

        msg = ("{}\n"
              "Bins: \n{}"
              "Counts:\n{}"
              "Values are logged to base {}\n"
              "Relative to: {}").format(type(self), RectilinearMesh1D.summary(self, True), self.counts.summary(True), self.log, self.relativeTo)

        return msg if out else print(msg)


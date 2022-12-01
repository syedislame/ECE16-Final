from ECE16Lib.CircularList import CircularList
import ECE16Lib.DSP as filt
import numpy as np

"""
A class to enable a simple step counter
"""
class Pedometer:
  """
  Encapsulated class attributes (with default values)
  """
  __steps = 0        # the current step count
  __jumps = 0        # the current jump count
  __l1 = None        # CircularList containing L1-norm
  __filtered = None  # CircularList containing filtered signal
  __num_samples = 0  # The length of data maintained
  __new_samples = 0  # How many new samples exist to process
  __fs = 0           # Sampling rate in Hz
  __b = None         # Low-pass coefficients
  __a = None         # Low-pass coefficients
  __thresh_low = 10   # Threshold from Tutorial 2
  __thresh_high = 120 # Threshold from Tutorial 2
  __thresh_low_jumps = 120    # Lower threshold for jumping
  __thresh_high_jumps = 1000   # Upper threshold for jumping

  """
  Initialize the class instance
  """
  def __init__(self, num_samples, fs, data=None):
    self.__steps = 0
    self.__jumps = 0
    self.__num_samples = num_samples
    self.__fs = fs
    self.__l1 = CircularList(data, num_samples)
    self.__filtered = CircularList([], num_samples)
    self.__b, self.__a = filt.create_filter(3, 1, "lowpass", fs)

  """
  Add new samples to the data buffer
  Handles both integers and vectors!
  """
  def add(self, ax, ay, az):
    l1 = filt.l1_norm(ax, ay, az)
    if isinstance(ax, int):
      num_add = 1
    else:
      num_add = len(ax)
      l1 = l1.tolist()

    self.__l1.add(l1)
    self.__new_samples += num_add

  """
  Process the new data to update step count
  """
  def process(self):
    # Grab only the new samples into a NumPy array
    x = np.array(self.__l1[ -self.__new_samples: ]) # convert l1 CircularList to an ndarray

    # Filter the signal (detrend, LP, MA, etc…)
    # ...
    # ...
    # ...
    x = filt.detrend(x) # detrend the data
    self.__b, self.__a = filt.create_filter(3, 1, btype="lowpass", fs=self.__fs)  # create lowpass filter
    x = filt.filter(self.__b, self.__a, x)  # filter data using lowpass filter

    # Store the filtered data
    self.__filtered.add(x.tolist()) # add filtered data back to "filtered" CircularList 

    # Count the number of peaks in the filtered data
    count_steps, peaks = filt.count_peaks(x,self.__thresh_low,self.__thresh_high) # count the peaks of the filtered data
      # with the threshold values set

    # Count the number of peaks in the filtererd data for jumps (removed for Complete Wearable)
    #count_jumps, peaks = filt.count_peaks(x,self.__thresh_low_jumps,self.__thresh_high_jumps)

    # Update the step count and reset the new sample count
    self.__steps += count_steps
    #self.__jumps += count_jumps
    self.__new_samples = 0

    # Return the step count, peak locations, and filtered data
    return self.__steps, self.__jumps, peaks, np.array(self.__filtered)
    #return self.__steps, peaks, np.array(self.__filtered)


  """
  Clear the data buffers and step count
  """
  def reset(self):
    self.__steps = 0
    self.__l1.clear()
    self.__filtered = np.zeros(self.__num_samples)
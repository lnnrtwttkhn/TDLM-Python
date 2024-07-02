# -*- coding: utf-8 -*-
"""
Created on Wed Mar 27 15:10:07 2024

util functions for Temporally Delayed Linear Modelling

@author: simon.kern
"""
import hashlib
import math
import numpy as np
import pandas as pd

def hash_array(arr, dtype=np.int64, truncate=8):
    """
    create a persistent hash for a numpy array based on the byte representation
    only the last `truncate` (default=8) characters are returned for simplicity

    Parameters
    ----------
    arr : np.ndarray
        DESCRIPTION.
    dtype : type, optional
        which data type to use. smaller type will be faster. 
        The default is np.int64.

    Returns
    -------
    str
        unique hash for that array.

    """
    arr = arr.astype(dtype)
    sha1_hash = hashlib.sha1(arr.flatten("C")).hexdigest()
    return sha1_hash[:truncate]


def unique_permutations(X, k=None):
    """
    #uperms: unique permutations of an input vector or rows of an input matrix
    # Usage:  nPerms              = uperms(X)
    #        [nPerms pInds]       = uperms(X, k)
    #        [nPerms pInds Perms] = uperms(X, k)
    #
    # Determines number of unique permutations (nPerms) for vector or matrix X.
    # Optionally, all permutations' indices (pInds) are returned. If requested,
    # permutations of the original input (Perms) are also returned.
    #
    # If k < nPerms, a random (but still unique) subset of k of permutations is
    # returned. The original/identity permutation will be the first of these.
    #
    # Row or column vector X results in Perms being a [k length(X)] array,
    # consistent with MATLAB's built-in perms. pInds is also [k length(X)].
    #
    # Matrix X results in output Perms being a [size(X, 1) size(X, 2) k]
    # three-dimensional array (this is inconsistent with the vector case above,
    # but is more helpful if one wants to easily access the permuted matrices).
    # pInds is a [k size(X, 1)] array for matrix X.
    #
    # Note that permutations are not guaranteed in any particular order, even
    # if all nPerms of them are requested, though the identity is always first.
    #
    # Other functions can be much faster in the special cases where they apply,
    # as shown in the second block of examples below, which uses perms_m.
    #
    # Examples:
    #  uperms(1:7),       factorial(7)        # verify counts in simple cases,
    #  uperms('aaabbbb'), nchoosek(7, 3)      # or equivalently nchoosek(7, 4).
    #  [n pInds Perms] = uperms('aaabbbb', 5) # 5 of the 35 unique permutations
    #  [n pInds Perms] = uperms(eye(3))       # all 6 3x3 permutation matrices
    #
    #  # A comparison of timings in a special case (i.e. all elements unique)
    #  tic; [nPerms P1] = uperms(1:20, 5000); T1 = toc
    #  tic; N = factorial(20); S = sample_no_repl(N, 5000);
    #  P2 = zeros(5000, 20);
    #  for n = 1:5000, P2(n, :) = perms_m(20, S(n)); end
    #  T2 = toc # quicker (note P1 and P2 are not the same random subsets!)
    #  # For me, on one run, T1 was 7.8 seconds, T2 was 1.3 seconds.
    #
    #  # A more complicated example, related to statistical permutation testing
    #  X = kron(eye(3), ones(4, 1));  # or similar statistical design matrix
    #  [nPerms pInds Xs] = uperms(X, 5000); # unique random permutations of X
    #  # Verify correctness (in this case)
    #  G = nan(12,5000); for n = 1:5000; G(:, n) = Xs(:,:,n)*(1:3)'; end
    #  size(unique(G', 'rows'), 1)    # 5000 as requested.
    #
    # See also: randperm, perms, perms_m, signs_m, nchoosek_m, sample_no_repl
    # and http://www.fmrib.ox.ac.uk/fsl/randomise/index.html#theory

    # Copyright 2010 Ged Ridgway
    # http://www.mathworks.com/matlabcentral/fileexchange/authors/27434
    """
    # Count number of repetitions of each unique row, and get representative x
    X = np.array(X).squeeze()
    assert len(X) > 1

    if X.ndim == 1:
        uniques, uind, c = np.unique(X, return_index=True, return_counts=True)
    else:
        # [u uind x] = unique(X, 'rows'); % x codes unique rows with integers
        uniques, uind, c = np.unique(X, axis=0, return_index=True, return_counts=True)

    uniques = uniques.tolist()
    x = np.array([uniques.index(i) for i in X.tolist()])

    c = sorted(c)
    nPerms = np.prod(np.arange(c[-1] + 1, np.sum(c) + 1)) / np.prod([math.factorial(x) for x in c[:-1]])
    nPerms = int(nPerms)
    # % computation of permutation
    # Basics
    n = len(X);
    if k is None or k > nPerms:
        k = nPerms;  # default to computing all unique permutations

    # % Identity permutation always included first:
    pInds = np.zeros([int(k), n]).astype(np.uint32)
    Perms = pInds.copy();
    pInds[0, :] = np.arange(0, n);
    Perms[0, :] = x;

    # Add permutations that are unique
    u = 0;  # to start with
    while u < k - 1:
        pInd = np.random.permutation(int(n));
        pInd = np.array(pInd).astype(int)  # just in case MATLAB permutation was monkey patched
        if x[pInd].tolist() not in Perms.tolist():
            u += 1
            pInds[u, :] = pInd
            Perms[u, :] = x[pInd]
    # %
    # Construct permutations of input
    if X.ndim == 1:
        Perms = np.repeat(np.atleast_2d(X), k, 0)
        for n in np.arange(1, k):
            Perms[n, :] = X[pInds[n, :]]
    else:
        Perms = np.repeat(np.atleast_3d(X), k, axis=2);
        for n in np.arange(1, k):
            Perms[:, :, n] = X[pInds[n, :], :]
    return (nPerms, pInds, Perms)


def char2num(seq):
    """convert list of chars to integers eg ABC=>012"""
    if isinstance(seq, str):
        seq = list(seq)
    assert ord('A')-65 == 0
    nums = [ord(c.upper())-65 for c in seq]
    assert all([0<=n<=90 for n in nums])
    return nums


def num2char(arr):
    """convert list of ints to alphabetical chars eg 012=>ABC"""
    if isinstance(arr, int):
        return chr(arr+65)
    arr = np.array(arr, dtype=int)
    return np.array([chr(x+65) for x in arr.ravel()]).reshape(*arr.shape)


def tf2seq(TF):
    """from transition matrix to alphanumerical sequence"""
    raise NotImplementedError
    seq = ''
    for i, row in enumerate(TF):
        for j, col in enumerate(row):
            np.where()
    return seq

def seq2tf(sequence, n_states=None):
    """
    create a transition matrix from a sequence string,
    e.g. ABCDEFG
    Please note that sequences will not be wrapping automatically,
    i.e. a wrapping sequence should be denoted by appending the first state.

    :param sequence: sequence in format "ABCD..."
    :param seqlen: if not all states are part of the sequence,
                   the number of states can be specified
                   e.g. if the sequence is ABE, but there are also states F,G
                   n_states would be 7

    """

    seq = char2num(sequence)
    if n_states is None:
        n_states = max(seq)+1
    # assert max(seq)+1==n_states, 'not all positions have a transition'
    TF = np.zeros([n_states, n_states], dtype=int)
    for i, p1 in enumerate(seq):
        if i+1>=len(seq): continue
        p2 = seq[(i+1) % len(seq)]
        TF[p1, p2] = 1
    return TF.astype(float)

def seq2TF_2step(seq, n_states=None):
    """create a transition matrix with all 2 steps from a sequence string,
    e.g. ABCDEFGE. """
    import pandas as pd
    triplets = []
    if n_states is None:
        n_states = max(char2num(seq))+1
    TF2 = np.zeros([n_states**2, n_states], dtype=int)
    for i, p1 in enumerate(seq):
        if i+2>=len(seq): continue
        triplet = seq[i] + seq[(i+1) % len(seq)] + seq[(i+2)% len(seq)]
        i = char2num(triplet[0])[0] * n_states + char2num(triplet[1])[0]
        j = char2num(triplet[2])
        TF2[i, j] = 1
        triplets.append(triplet)

    seq_set = num2char(np.arange(n_states))
    # for visualiziation purposes
    df = pd.DataFrame({c:TF2.T[i] for i,c in enumerate(seq_set)})
    df['index'] = [f'{y}{x}' for y in seq_set for x in seq_set]
    df = df.set_index('index')
    TF2 = df.loc[~(df==0).all(axis=1)]
    return TF2


def simulate_eeg_resting_state(n_samples, alpha_freq=10.0, alpha_strength=1.0,
                               noise=1.0, n_channels=64):
    raise NotImplementedError()
    
def simulate_eeg_localizer(n_samples, n_classes, noise=1.0, n_channels=64):
    raise NotImplementedError()

def insert_events(data, insert_data, insert_labels, sequence, n_events, 
                  lag=7, jitter=0, n_steps=2, distribution='constant',
                  return_onsets=False):
    """
    inject decodable events into M/EEG data according to a certain pattern.


    Parameters
    ----------
    data : TYPE
        DESCRIPTION.
    insert_data : TYPE
        DESCRIPTION.
    insert_labels : TYPE
        DESCRIPTION.
    lag : TYPE, optional
        Sample space distance individual reactivation events events. 
        The default is 7 (e.g. 70 ms replay speed time lag).
    jitter : int, optional
        By how many sample points to jitter the events (randomly). 
        The default is 0.
    n_steps : int, optional
        Number of events to insert. The default is 2
    distribution : str | np.ndarray, optional
        How replay events should be distributed throughout the time series.
        Can either be 'constant', 'increasing' or 'decreasing' or a p vector
        with probabilities for each sample point in data.
        The default is 'constant'.

    Raises
    ------
    ValueError
        DESCRIPTION.
    Exception
        DESCRIPTION.

    Returns
    -------
    data : np.ndarray (shape=data.shape)
        data with inserted events.
    """
    import logging
    assert len(insert_data) == len(insert_labels), 'each data point must have a label'
    assert insert_data.ndim in [2, 3]
    assert insert_labels.ndim == 1
    assert data.ndim==2
    assert data.shape[1] == insert_data.shape[1]
    
    if isinstance(distribution, np.ndarray):
        assert len(distribution) == len(data)
        assert distribution.ndim == 1
        assert np.isclose(distribution.sum(), 1), 'Distribution must sum to 1, but {distribution.sum()=}'

    # convert data to 3d
    if insert_data.ndim==2:
        insert_data = insert_data.reshape([*insert_data.shape, 1])   
    
    # get reproducible seed
    seed = int(''.join(([str(x) if x.isdigit() else str(ord(x)) for x in hash_array(data)])))
    np.random.seed(seed)

    # Define default parameters for replay generation
    # defaults = {'dist':7,
    #             'n_events':250,
    #             'tp':31,
    #             'seqlen':3,
    #             'direction':'fwd',
    #             'distribution':'constant',
    #             'trange': 0}

    # Extract parameters for further use
    # trange = params['trange']

    # Calculate mean values that should be inserted per class
    class_mean = []
    for label in set(insert_labels):
        class_mean += [insert_data[insert_labels==label, :, :].mean(0)]
    class_mean = np.stack(class_mean)
   
    # Calculate probability distribution based on the specified distribution type
    if distribution=='constant':
        p = np.ones(len(data))
        p = p/p.sum()
    elif distribution=='decreasing':
        p = np.linspace(1, 0, len(data))**2
        p = p/p.sum()
    elif distribution=='increasing':
        p = np.linspace(0, 1, len(data))**2
        p = p/p.sum()
    else:
        raise Exception(f'unknown distribution {distribution}')

    # Calculate length of the replay sequence
    padding = n_steps*lag + data.shape[-1]
    p[-padding:] = 0  # can't insert events starting here, would be too long
    p = p/p.sum()

    replay_start_idxs = []
    all_idx = np.arange(len(data))
    
    # iteratively select starting index for replay event 
    # such that replay events are not overlapping
    for i in range(n_events):
        np.random.choice(all_idx, p=p)
        
        # next set all indices of p to zero where events will be inserted
        # this way we can prevent overlap of replay event trains
        # Find available indices where events can be inserted
        available_indices = np.where(p > 0)[0]

        # Ensure that there are enough available indices to choose from
        if len(available_indices) < n_events - i:
            raise ValueError(f"Not enough available indices to insert all events without overlap, {n_events=} too high")

        # Choose a random index from the available indices
        start_idx = np.random.choice(all_idx, p=p)

        # this is the calculated end index
        end_idx = start_idx + lag * n_steps + insert_data.shape[-1]
        assert end_idx<len(p)
        # Update the p array to zero out the region around the chosen index to prevent overlap
        p[start_idx:end_idx] = 0
        
        # normalize to create valid probability distribution 
        p = p/p.sum()  

        # Append the chosen index to the list of starting indices
        replay_start_idxs.append(start_idx)
        
    data_sim = data.copy()  # work on copy of array to prevent mutable changes
    
    # save data about inserted events here and return if requested
    events = {'idx': [], 
              'pos': [],
              'step': [],
              'class_idx': [],
              'span': [],
              'jitter': []}
    
    for idx,  start_idx in enumerate(replay_start_idxs):
        smp_jitter = 0  # starting with no jitter
        pos = start_idx  # pos indicates where in data we insert the next event
        
        # choose the starting class such that the n_steps can actually be taken
        # at that position to finish the sequence without looping to beginning
        seq_i = np.random.choice(np.arange(len(sequence)-n_steps))
        for step in range(n_steps+1):
            # choose which item should be inserted based on sequence order
            class_idx = sequence[seq_i] 
            data_sim[pos:pos+class_mean.shape[-1], :] += class_mean[class_idx].T
            logging.debug(f'{start_idx=} {pos=} {class_idx=}')
            
            events['idx'] += [idx]
            events['pos'] += [pos]
            events['step'] += [step]
            events['class_idx'] += [class_idx]
            events['span'] += [class_mean.shape[-1]]
            events['jitter'] += [smp_jitter]
            
            # increment pos to select position of next reactivation event
            smp_jitter = np.random.randint(-jitter, jitter+1) if jitter else 0
            pos += lag + smp_jitter  # add next sequence step
            seq_i += 1  # increment sequence id for next step
            
    if return_onsets:
        df_onsets = pd.DataFrame(events)
        return (data_sim, df_onsets) 
    
    return data_sim

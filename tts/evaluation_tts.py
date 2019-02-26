# coding: utf-8
"""Evaluation script for GAN-based text-to-speech synthesis.

options:
    --fs=<fs>                   Sampling frequency [default: 16000].
    --disable-duraton-gen       Disable duration generation.
    --post-filter               Apply Merlin's post filter to spectral features.
"""
import numpy as np

import torch
from torch.autograd import Variable

from scipy.io import wavfile
import pyworld
import pysptk

from os.path import join

from nnmnkwii import preprocessing as P
from nnmnkwii import paramgen
from nnmnkwii.io import hts
from nnmnkwii.frontend import merlin as fe
from nnmnkwii.postfilters import merlin_post_filter

import gantts
from hparams import tts_acoustic as hp_acoustic
from hparams import tts_duration as hp_duration


use_cuda = torch.cuda.is_available()

binary_dict, continuous_dict = hts.load_question_set(hp_acoustic.question_path)


def gen_parameters(y_predicted, Y_mean, Y_std, mge_training=True):
    mgc_dim, lf0_dim, vuv_dim, bap_dim = hp_acoustic.stream_sizes

    lf0_start_idx = mgc_dim
    vuv_start_idx = lf0_start_idx + lf0_dim
    bap_start_idx = vuv_start_idx + vuv_dim

    windows = hp_acoustic.windows

    ty = "acoustic"

    # MGE training
    if mge_training:
        # Split acoustic features
        mgc = y_predicted[:, :lf0_start_idx]
        lf0 = y_predicted[:, lf0_start_idx:vuv_start_idx]
        vuv = y_predicted[:, vuv_start_idx]
        bap = y_predicted[:, bap_start_idx:]

        # Perform MLPG on normalized features
        mgc = paramgen.mlpg(mgc, np.ones(mgc.shape[-1]), windows)
        lf0 = paramgen.mlpg(lf0, np.ones(lf0.shape[-1]), windows)
        bap = paramgen.mlpg(bap, np.ones(bap.shape[-1]), windows)

        # When we use MGE training, denormalization should be done after MLPG.
        mgc = P.inv_scale(mgc, Y_mean[ty][:mgc_dim // len(windows)], Y_std[ty][:mgc_dim // len(windows)])
        lf0 = P.inv_scale(lf0, Y_mean[ty][lf0_start_idx:lf0_start_idx + lf0_dim // len(windows)], Y_std[ty][lf0_start_idx:lf0_start_idx + lf0_dim // len(windows)])
        bap = P.inv_scale(bap, Y_mean[ty][bap_start_idx:bap_start_idx + bap_dim // len(windows)], Y_std[ty][bap_start_idx:bap_start_idx + bap_dim // len(windows)])
        vuv = P.inv_scale(vuv, Y_mean[ty][vuv_start_idx], Y_std[ty][vuv_start_idx])
    else:
        # Denormalization first
        y_predicted = P.inv_scale(y_predicted, Y_mean, Y_std)

        # Split acoustic features
        mgc = y_predicted[:, :lf0_start_idx]
        lf0 = y_predicted[:, lf0_start_idx:vuv_start_idx]
        vuv = y_predicted[:, vuv_start_idx]
        bap = y_predicted[:, bap_start_idx:]

        # Perform MLPG
        Y_var = Y_std[ty] * Y_std[ty]
        mgc = paramgen.mlpg(mgc, Y_var[:lf0_start_idx], windows)
        lf0 = paramgen.mlpg(lf0, Y_var[lf0_start_idx:vuv_start_idx], windows)
        bap = paramgen.mlpg(bap, Y_var[bap_start_idx:], windows)

    return mgc, lf0, vuv, bap


def gen_waveform(y_predicted, Y_mean, Y_std, post_filter=False, coef=1.4,
                 fs=16000, mge_training=True):
    alpha = pysptk.util.mcepalpha(fs)
    fftlen = fftlen = pyworld.get_cheaptrick_fft_size(fs)
    frame_period = hp_acoustic.frame_period

    # Generate parameters and split streams
    mgc, lf0, vuv, bap = gen_parameters(y_predicted, Y_mean, Y_std, mge_training)

    if post_filter:
        mgc = merlin_post_filter(mgc, alpha, coef=coef)

    spectrogram = pysptk.mc2sp(mgc, fftlen=fftlen, alpha=alpha)
    aperiodicity = pyworld.decode_aperiodicity(bap.astype(np.float64), fs, fftlen)
    f0 = lf0.copy()
    f0[vuv < 0.5] = 0
    f0[np.nonzero(f0)] = np.exp(f0[np.nonzero(f0)])

    generated_waveform = pyworld.synthesize(
        f0.flatten().astype(np.float64),
        spectrogram.astype(np.float64),
        aperiodicity.astype(np.float64),
        fs, frame_period
    )
    # Convert range to int16
    generated_waveform = generated_waveform / np.max(np.abs(generated_waveform)) * 32767

    # return features as well to compare natural/genearted later
    return generated_waveform, mgc, lf0, vuv, bap


def _generator_input(hp, x, seed=None):
    if seed is not None:
        torch.manual_seed(seed)
    if hp.generator_add_noise:
        z = torch.rand(x.size(0), x.size(1), hp.generator_noise_dim)
        z = Variable(z)
        return torch.cat((x, z), -1)
    return x


def gen_duration(label_path, duration_model, X_min, X_max, Y_mean, Y_std):
    # Linguistic features for duration
    hts_labels = hts.load(label_path)
    duration_linguistic_features = fe.linguistic_features(
        hts_labels,
        binary_dict, continuous_dict,
        add_frame_features=hp_duration.add_frame_features,
        subphone_features=hp_duration.subphone_features
    ).astype(np.float32)

    # Apply normali--post-filterzation
    ty = "duration"
    duration_linguistic_features = P.minmax_scale(
        duration_linguistic_features,
        X_min[ty],
        X_max[ty],
        feature_range=(0.01, 0.99)
    )

    # Apply models
    duration_model.eval()

    #  Apply model
    x = Variable(torch.from_numpy(duration_linguistic_features)).float()
    xl = len(x)
    x = x.view(1, -1, x.size(-1))
    x = _generator_input(hp_duration, x)
    x = x.cuda() if use_cuda else x
    duration_predicted = duration_model(x, [xl]).data.cpu().numpy()
    duration_predicted = duration_predicted.reshape(-1, duration_predicted.shape[-1])

    # Apply denormalization
    duration_predicted = P.inv_scale(duration_predicted, Y_mean[ty], Y_std[ty])
    duration_predicted = np.round(duration_predicted)

    # Set minimum state duration to 1
    #  print(duration_predicted)
    duration_predicted[duration_predicted <= 0] = 1
    hts_labels.set_durations(duration_predicted)

    return hts_labels


def tts_from_label(models, label_path, X_min, X_max, Y_mean, Y_std,
                   post_filter=False,
                   apply_duration_model=True, coef=1.4, fs=16000,
                   mge_training=True):
    duration_model, acoustic_model = models["duration"], models["acoustic"]

    if use_cuda:
        duration_model = duration_model.cuda()
        acoustic_model = acoustic_model.cuda()

    # Predict durations
    if apply_duration_model:
        duration_modified_hts_labels = gen_duration(
            label_path, duration_model, X_min, X_max, Y_mean, Y_std)
    else:
        duration_modified_hts_labels = hts.load(label_path)

    # Linguistic features
    linguistic_features = fe.linguistic_features(
        duration_modified_hts_labels,
        binary_dict,
        continuous_dict,
        add_frame_features=hp_acoustic.add_frame_features,
        subphone_features=hp_acoustic.subphone_features
    )
    # Trim silences
    indices = duration_modified_hts_labels.silence_frame_indices()
    linguistic_features = np.delete(linguistic_features, indices, axis=0)

    # Apply normalization
    ty = "acoustic"
    linguistic_features = P.minmax_scale(
        linguistic_features,
        X_min[ty],
        X_max[ty],
        feature_range=(0.01, 0.99)
    )

    # Predict acoustic features
    acoustic_model.eval()
    x = Variable(torch.from_numpy(linguistic_features)).float()
    xl = len(x)
    x = x.view(1, -1, x.size(-1))
    x = _generator_input(hp_duration, x)
    x = x.cuda() if use_cuda else x
    acoustic_predicted = acoustic_model(x, [xl]).data.cpu().numpy()
    acoustic_predicted = acoustic_predicted.reshape(-1, acoustic_predicted.shape[-1])
    # q.d()
    return gen_waveform(acoustic_predicted, Y_mean, Y_std, post_filter, coef=coef, fs=fs, mge_training=mge_training)


def load_checkpoint(model, optimizer, checkpoint_path):
    print("Load checkpoint from: {}".format(checkpoint_path))
    checkpoint = torch.load(checkpoint_path, map_location="cpu")
    model.load_state_dict(checkpoint["state_dict"])
    if optimizer is not None:
        optimizer.load_state_dict(checkpoint["optimizer"])


def init(acoustic_checkpoint, duration_checkpoint, data_dir):
    post_filter = False
    disable_duration_gen = False
    fs = 16000

    # Collect stats and create models
    X_min = {}
    X_max = {}
    Y_mean = {}
    Y_var = {}
    Y_std = {}
    models = {"acoustic": {}, "duration": {}}

    for typ in ["acoustic", "duration"]:
        X_min[typ] = np.load(join(data_dir, "X_{}_data_min.npy".format(typ)))
        X_max[typ] = np.load(join(data_dir, "X_{}_data_max.npy".format(typ)))
        Y_mean[typ] = np.load(join(data_dir, "Y_{}_data_mean.npy".format(typ)))
        Y_var[typ] = np.load(join(data_dir, "Y_{}_data_var.npy".format(typ)))
        Y_std[typ] = np.sqrt(Y_var[typ])

        hp = hp_acoustic if typ == "acoustic" else hp_duration
        if hp.generator_params["in_dim"] is None:
            D = X_min[typ].shape[-1]
            if hp.generator_add_noise:
                D = D + hp.generator_noise_dim
            hp.generator_params["in_dim"] = D
        if hp.generator_params["out_dim"] is None:
            hp.generator_params["out_dim"] = Y_mean[typ].shape[-1]

        models[typ] = getattr(gantts.models, hp.generator)(**hp.generator_params)
        checkpoint_path = hp == hp_duration and duration_checkpoint or acoustic_checkpoint
        load_checkpoint(models[typ], None, checkpoint_path)

    print(models)

    def do_tts(label_path, dst_path):

        waveform, mgc, lf0, vuv, bap = tts_from_label(
            models, label_path, X_min, X_max, Y_mean, Y_std,
            apply_duration_model=not disable_duration_gen,
            post_filter=post_filter, fs=fs
        )
        wavfile.write(dst_path, fs, waveform.astype(np.int16))

    return do_tts

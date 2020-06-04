import cv2 as cv
import numpy as np
import q
import sys
import ubelt

models = {
    "instance_norm_mosaic": "./core/models/instance_norm/mosaic.t7",
    "instance_norm_candy": "./core/models/instance_norm/candy.t7",
    "instance_norm_the_scream": "./core/models/instance_norm/the_scream.t7",
    "instance_norm_feathers": "./core/models/instance_norm/feathers.t7",
    "instance_norm_la_muse": "./core/models/instance_norm/la_muse.t7",
    "instance_norm_udnie": "./core/models/instance_norm/udnie.t7",
    "eccv16_starry_night": "./core/models/eccv16/starry_night.t7",
    "eccv16_la_muse": "./core/models/eccv16/la_muse.t7",
    "eccv16_composition_vii": "./core/models/eccv16/composition_vii.t7",
    "eccv16_the_wave": "./core/models/eccv16/the_wave.t7",
}


def apply_model(frame, model_name="eccv16_the_wave"):
    """
        -(120, 120, 120) 相当于模糊细节
        +(120, 120, 120) 相当于增加一个白色蒙版
    """
    net = cv.dnn.readNetFromTorch(models[model_name])
    net.setPreferableBackend(cv.dnn.DNN_BACKEND_OPENCV)

    inp = cv.dnn.blobFromImage(
        frame,
        1.0,
        (frame.shape[1], frame.shape[0]),
        (103.939, 116.779, 123.68),
        swapRB=False,
        crop=False
    )

    net.setInput(inp)
    out = net.forward()

    out = out.reshape(3, out.shape[2], out.shape[3])
    out[0] += 103.939
    out[1] += 116.779
    out[2] += 123.68
    out = out.transpose(1, 2, 0)
    if out.shape != frame.shape:
        out = out[:frame.shape[0], :frame.shape[1], :frame.shape[2]]

    return out

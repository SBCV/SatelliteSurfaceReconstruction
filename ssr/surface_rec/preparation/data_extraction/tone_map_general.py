#  ===============================================================================================================
#  Copyright (c) 2019, Cornell University. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without modification, are permitted provided that
#  the following conditions are met:
#
#      * Redistributions of source code must retain the above copyright otice, this list of conditions and
#        the following disclaimer.
#
#      * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and
#        the following disclaimer in the documentation and/or other materials provided with the distribution.
#
#      * Neither the name of Cornell University nor the names of its contributors may be used to endorse or
#        promote products derived from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED
#  WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
#  A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDERS OR CONTRIBUTORS BE LIABLE
#  FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
#  TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#  HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
#   NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY
#  OF SUCH DAMAGE.
#
#  Author: Kai Zhang (kz298@cornell.edu)
#
#  The research is based upon work supported by the Office of the Director of National Intelligence (ODNI),
#  Intelligence Advanced Research Projects Activity (IARPA), via DOI/IBC Contract Number D17PC00287.
#  The U.S. Government is authorized to reproduce and distribute copies of this work for Governmental purposes.
#  ===============================================================================================================


import numpy as np
import imageio
import os
from ssr.utility.logging_extension import logger


def read_hdr_image(in_hdr_png):
    # =========================================================================
    # https://github.com/imageio/imageio/issues/204
    # Read with FreeImage instead of Pillow is MANDATORY TO READ 16 bit color
    # pngs correctly!!!!
    hdr_img = imageio.imread(in_hdr_png, "PNG-FI").astype(dtype=np.float64)
    # =========================================================================

    if hdr_img.ndim == 3:
        red_channel = hdr_img[:, :, 0]
        green_channel = hdr_img[:, :, 1]
        blue_channel = hdr_img[:, :, 2]
        assert np.amax(red_channel) > 7
        assert np.amax(green_channel) > 7
        assert np.amax(blue_channel) > 7

    return hdr_img


def write_as_ldr_image(hdr_img, ofp):
    if os.path.exists(ofp):
        os.remove(ofp)
    imageio.imwrite(ofp, hdr_img.astype(dtype=np.uint8))


def write_as_hdr_image(hdr_img, ofp):
    if os.path.exists(ofp):
        os.remove(ofp)
    imageio.imwrite(ofp, hdr_img.astype(dtype=np.uint16))


def split_msi(in_png, r_out_png, g_out_png, b_out_png, target_dtype=np.uint8):
    im = imageio.imread(in_png)

    imageio.imwrite(r_out_png, im[:, :, 0].astype(dtype=target_dtype))
    imageio.imwrite(g_out_png, im[:, :, 1].astype(dtype=target_dtype))
    imageio.imwrite(b_out_png, im[:, :, 2].astype(dtype=target_dtype))


def combine_msi(b_out_png, g_out_png, r_out_png, out_png, target_dtype=np.uint8):
    image_b = imageio.imread(b_out_png)
    image_g = imageio.imread(g_out_png)
    image_r = imageio.imread(r_out_png)

    combined_np = np.dstack((np.array(image_r), np.array(image_g), np.array(image_b)))

    imageio.imwrite(out_png, combined_np.astype(dtype=target_dtype))


def tone_map_channel(channel, percentile=0.5, exp=1.0 / 2.2):

    # =========================================================================
    # Use QGIS to examine the PNG result (i.e. color range of the created file)
    # =========================================================================

    # gamma correction
    # Could be also computed with GDAL
    # https://gdal.org/programs/gdal_translate.html#cmdoption-gdal-translate-exponent
    tone_mapped_channel = np.power(channel, exp)

    # cut off the small values
    below_thres = np.percentile(tone_mapped_channel.reshape((-1, 1)), percentile)
    tone_mapped_channel[tone_mapped_channel < below_thres] = below_thres
    # cut off the big values
    above_thres = np.percentile(tone_mapped_channel.reshape((-1, 1)), 100 - percentile)
    tone_mapped_channel[tone_mapped_channel > above_thres] = above_thres

    # Put in range 0 - 255
    tone_mapped_channel = (
        255 * (tone_mapped_channel - below_thres) / (above_thres - below_thres)
    )
    return tone_mapped_channel


def tone_map_separate(im, percentile=0.5, exp=1.0 / 2.2):
    red_channel = im[:, :, 0]
    green_channel = im[:, :, 1]
    blue_channel = im[:, :, 2]

    red_channel = tone_map_channel(red_channel, percentile, exp)
    green_channel = tone_map_channel(green_channel, percentile, exp)
    blue_channel = tone_map_channel(blue_channel, percentile, exp)

    hdr_result_tone_mapped = np.dstack(
        (
            np.array(red_channel),
            np.array(green_channel),
            np.array(blue_channel),
        )
    )

    return hdr_result_tone_mapped


def rgb_2_gray(rgb):
    weights = get_rgb_2_gray_weights()
    return (
        weights[0] * rgb[..., 0] + weights[1] * rgb[..., 1] + weights[2] * rgb[..., 2]
    )


def get_rgb_2_gray_weights(use_luminance_weights=True):
    # https://brohrer.github.io/convert_rgb_to_grayscale.html
    #   Channel-dependent luminance perception
    #       Y_linear = 0.2126 R + 0.7152 G + 0.0722 B
    #   Gamma compression
    #       ...
    #   Linear approximation
    #       Y' = 0.299 + 0.587 G + 0.114 B
    #   Which one should I use?
    #      If close is good enough or if you really care about speed, use the
    #      linear approximation of gamma correction.
    #      This is the approach used by MATLAB, Pillow, and OpenCV

    # https://stackoverflow.com/questions/12201577/how-can-i-convert-an-rgb-image-into-grayscale-in-python
    #   gray = 0.2989 * r + 0.5870 * g + 0.1140 * b
    if use_luminance_weights:
        return [0.2989, 0.5870, 0.1140]
    else:
        return [1.0 / 3.0, 1.0 / 3.0, 1.0 / 3.0]


def tone_map_joint(im, percentile=0.5, exp=1.0 / 2.2):

    # https://en.wikipedia.org/wiki/Gamma_correction
    # gamma correction
    im = np.power(im, exp)

    im_gray = rgb_2_gray(im)

    im_gray_1d = im_gray.reshape((-1, 1))

    # cut off the small values
    below_thres = np.percentile(im_gray_1d, percentile)
    below_thresh_indices = im_gray < below_thres
    below_thres_arr = np.full_like(im_gray, below_thres)

    below_scale_factor_arr = np.divide(below_thres_arr, im_gray)
    r_below_scaled = np.multiply(im[:, :, 0], below_scale_factor_arr)
    g_below_scaled = np.multiply(im[:, :, 1], below_scale_factor_arr)
    b_below_scaled = np.multiply(im[:, :, 2], below_scale_factor_arr)

    im[below_thresh_indices, 0] = r_below_scaled[below_thresh_indices]
    im[below_thresh_indices, 1] = g_below_scaled[below_thresh_indices]
    im[below_thresh_indices, 2] = b_below_scaled[below_thresh_indices]

    # cut off the big values
    above_thres = np.percentile(im_gray_1d, 100 - percentile)
    above_thresh_indices = im_gray > above_thres
    above_thres_arr = np.full_like(im_gray, above_thres)

    above_scale_factor_arr = np.divide(above_thres_arr, im_gray)
    r_above_scaled = np.multiply(im[:, :, 0], above_scale_factor_arr)
    g_above_scaled = np.multiply(im[:, :, 1], above_scale_factor_arr)
    b_above_scaled = np.multiply(im[:, :, 2], above_scale_factor_arr)

    im[above_thresh_indices, 0] = r_above_scaled[above_thresh_indices]
    im[above_thresh_indices, 1] = g_above_scaled[above_thresh_indices]
    im[above_thresh_indices, 2] = b_above_scaled[above_thresh_indices]

    # === Verify results ===
    # logger.info(f'below_thres {below_thres}')
    # logger.info(f'above_thres {above_thres}')
    # im_gray_ref = rgb_2_gray(im)
    # im_gray_ref_1d = im_gray_ref.reshape((-1, 1))
    # below_thres_ref = np.percentile(im_gray_ref_1d, percentile)
    # above_thres_ref = np.percentile(im_gray_ref_1d, 100 - percentile)
    # logger.info(f'below_thres_ref {below_thres_ref}')
    # logger.info(f'above_thres_ref {above_thres_ref}')
    # assert np.allclose(below_thres, below_thres_ref)
    # assert np.allclose(above_thres, above_thres_ref)

    # log_value(im, 0, print_min=True)
    # log_value(im, 1, print_min=True)
    # log_value(im, 2, print_min=True)
    #
    # log_value(im, 0, print_min=False)
    # log_value(im, 1, print_min=False)
    # log_value(im, 2, print_min=False)

    # Put in range 0 - 255
    # logger.info(
    #   f'min values: {np.amin(im)}, {np.amin(im[:, :, 0])}, {np.amin(im[:, :, 1])}, {np.amin(im[:, :, 2])}'
    # )
    # logger.info(
    #   f'max values: {np.amax(im)}, {np.amax(im[:, :, 0])}, {np.amax(im[:, :, 1])}, {np.amax(im[:, :, 2])}'
    # )
    # === ===

    # im = rescale_im_or_chan(im)
    im[:, :, 0] = rescale_im_or_chan(im[:, :, 0])
    im[:, :, 1] = rescale_im_or_chan(im[:, :, 1])
    im[:, :, 2] = rescale_im_or_chan(im[:, :, 2])
    return im


def rescale_im_or_chan(im_or_chan):
    min_val = np.amin(im_or_chan)
    max_val = np.amax(im_or_chan)
    im_or_chan = 255 * (im_or_chan - min_val) / (max_val - min_val)
    return im_or_chan


def log_value(im, chan_idx, print_min):
    logger.info("------------------")
    logger.info(f"chan_idx {chan_idx}")
    logger.info(f"print_min {print_min}")
    chan = im[:, :, chan_idx]
    if print_min:
        val = chan.argmin()
    else:
        val = chan.argmax()

    idx_2d = np.unravel_index(val, chan.shape)
    weights = get_rgb_2_gray_weights()
    rgb = im[idx_2d]
    gray_ref = np.dot(weights, rgb)

    logger.info(f"idx_2d {idx_2d}")
    logger.info(f"chan value {chan[idx_2d]}")
    logger.info(f"rgb value {rgb}")
    logger.info(f"gray_ref {gray_ref}")
    logger.info("------------------")


# hdr_img is 16-bit, while ldr_img is 8 bit
def tone_map_hdr_to_ldr_general(
    hdr_img_ifp,
    ldr_img_ofp,
    joint_tone_mapping=True,
    percentile=0.5,
    exp=1.0 / 2.2,
):

    im = read_hdr_image(hdr_img_ifp)

    # A single (PAN chromatic / grey) channel has 2 spatial dimension
    if im.ndim == 2:
        hdr_result_tone_mapped = tone_map_channel(im, percentile, exp)

    # A MSI / color image has 3 channels
    elif im.ndim == 3:
        if joint_tone_mapping:
            hdr_result_tone_mapped = tone_map_joint(im, percentile, exp)
        else:
            hdr_result_tone_mapped = tone_map_separate(im, percentile, exp)
    else:
        assert False

    write_as_ldr_image(hdr_result_tone_mapped, ldr_img_ofp)

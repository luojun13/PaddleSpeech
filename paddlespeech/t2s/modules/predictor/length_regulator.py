# Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Modified from espnet(https://github.com/espnet/espnet)
"""Length regulator related modules."""
import numpy as np
import paddle
from paddle import nn


class LengthRegulator(nn.Layer):
    """Length regulator module for feed-forward Transformer.

    This is a module of length regulator described in
    `FastSpeech: Fast, Robust and Controllable Text to Speech`_.
    The length regulator expands char or
    phoneme-level embedding features to frame-level by repeating each
    feature based on the corresponding predicted durations.

    .. _`FastSpeech: Fast, Robust and Controllable Text to Speech`:
        https://arxiv.org/pdf/1905.09263.pdf

    """

    def __init__(self, pad_value=0.0):
        """Initilize length regulator module.

        Args:
            pad_value (float, optional): Value used for padding.

        """
        super().__init__()
        self.pad_value = pad_value

    # expand_numpy is faster than expand
    def expand_numpy(self, encodings: paddle.Tensor,
                     durations: paddle.Tensor) -> paddle.Tensor:
        """
        encodings: (B, T, C)
        durations: (B, T)
        """
        batch_size, t_enc = durations.shape
        durations = durations.numpy()
        slens = np.sum(durations, -1)
        t_dec = np.max(slens)
        M = np.zeros([batch_size, t_dec, t_enc])
        for i in range(batch_size):
            k = 0
            for j in range(t_enc):
                d = durations[i, j]
                M[i, k:k + d, j] = 1
                k += d
        M = paddle.to_tensor(M, dtype=encodings.dtype)
        encodings = paddle.matmul(M, encodings)
        return encodings

    def expand(self, encodings: paddle.Tensor,
               durations: paddle.Tensor) -> paddle.Tensor:
        """
        encodings: (B, T, C)
        durations: (B, T)
        """
        batch_size, t_enc = paddle.shape(durations)
        slens = paddle.sum(durations, -1)
        t_dec = paddle.max(slens)
        M = paddle.zeros([batch_size, t_dec, t_enc])
        for i in range(batch_size):
            k = 0
            for j in range(t_enc):
                d = durations[i, j]
                # If the d == 0, slice action is meaningless and not supported in paddle
                if d >= 1:
                    M[i, k:k + d, j] = 1
                k += d
        encodings = paddle.matmul(M, encodings)
        return encodings

    def forward(self, xs, ds, alpha=1.0, is_inference=False):
        """Calculate forward propagation.

        Args:
            xs (Tensor): Batch of sequences of char or phoneme embeddings (B, Tmax, D).
            ds (Tensor(int64)): Batch of durations of each frame (B, T).
            alpha (float, optional): Alpha value to control speed of speech.

        Returns:
            Tensor: replicated input tensor based on durations (B, T*, D).
        """

        if alpha != 1.0:
            assert alpha > 0
            ds = paddle.round(ds.cast(dtype=paddle.float32) * alpha)
        ds = ds.cast(dtype=paddle.int64)
        if is_inference:
            return self.expand(xs, ds)
        else:
            return self.expand_numpy(xs, ds)

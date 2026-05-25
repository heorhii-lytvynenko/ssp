import numpy as np

from signal_utils import time_axis_ms, to_mono


def _normalize(sig):
    mu = np.mean(sig)
    std = np.std(sig) + 1e-12
    return (sig - mu) / std, mu, std


def _make_dataset(sig, order):
    x = []
    y = []
    for i in range(order, len(sig)):
        x.append(sig[i - order : i])
        y.append(sig[i])
    return np.array(x), np.array(y)


def _mse(y, yhat):
    return float(np.mean((y - yhat) ** 2))


class ModelingLogic:
    @staticmethod
    def build(segment, samplerate, order=12, hidden=16, epochs=120, lr=0.02):
        sig = to_mono(segment)
        # Keep modeling responsive when a very long segment is selected in the UI.
        max_samples = 24000
        if len(sig) > max_samples:
            sig = sig[:max_samples]
        if len(sig) < order + 5:
            return {
                "mode": "modeling",
                "error": "Segment too short for modeling.",
            }

        sig_n, mu, std = _normalize(sig)
        x, y = _make_dataset(sig_n, order)
        split = max(1, int(len(x) * 0.8))
        xtr, ytr = x[:split], y[:split]
        xte, yte = x[split:], y[split:]
        if len(xte) == 0:
            xte, yte = xtr, ytr

        # Linear predictor (perceptron style: single linear layer).
        w_lin, *_ = np.linalg.lstsq(xtr, ytr, rcond=None)
        yhat_lin = xte @ w_lin
        mse_lin = _mse(yte, yhat_lin)

        # Nonlinear predictor (small 1-hidden-layer ANN, fixed topology).
        rng = np.random.default_rng(42)
        w1 = rng.normal(0, 0.1, size=(order, hidden))
        b1 = np.zeros(hidden)
        w2 = rng.normal(0, 0.1, size=(hidden, 1))
        b2 = np.zeros(1)

        for _ in range(epochs):
            z1 = xtr @ w1 + b1
            h1 = np.tanh(z1)
            yhat = (h1 @ w2 + b2).reshape(-1)
            err = yhat - ytr

            d_y = (2.0 / len(xtr)) * err
            d_w2 = h1.T @ d_y.reshape(-1, 1)
            d_b2 = np.sum(d_y)
            d_h1 = d_y.reshape(-1, 1) @ w2.T
            d_z1 = d_h1 * (1.0 - np.tanh(z1) ** 2)
            d_w1 = xtr.T @ d_z1
            d_b1 = np.sum(d_z1, axis=0)

            w2 -= lr * d_w2
            b2 -= lr * d_b2
            w1 -= lr * d_w1
            b1 -= lr * d_b1

        z1t = xte @ w1 + b1
        h1t = np.tanh(z1t)
        yhat_nonlin = (h1t @ w2 + b2).reshape(-1)
        mse_nonlin = _mse(yte, yhat_nonlin)

        # denormalize for plotting
        yte_d = yte * std + mu
        yhat_lin_d = yhat_lin * std + mu
        yhat_nonlin_d = yhat_nonlin * std + mu
        err_lin = yte_d - yhat_lin_d
        err_nonlin = yte_d - yhat_nonlin_d

        t0 = order + split
        t = time_axis_ms(len(yte_d), samplerate, start_ms=t0 / samplerate * 1000.0)
        return {
            "mode": "modeling",
            "time_ms": t,
            "actual": yte_d,
            "pred_linear": yhat_lin_d,
            "pred_nonlinear": yhat_nonlin_d,
            "err_linear": err_lin,
            "err_nonlinear": err_nonlin,
            "mse_linear": mse_lin,
            "mse_nonlinear": mse_nonlin,
            "order": order,
            "hidden": hidden,
        }

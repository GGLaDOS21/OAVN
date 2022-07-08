import scipy
import matplotlib.pyplot as plt
import numpy as np
import math


class Main:

                                                               # plot bitrate/gsnr
    BER = 0.001
    Rs = 32 * 1000000000  # rate simbolico del light path, in hertz (32 GHz)
    Bn = 12.5 * 1000000000  # larghezza di banda del rumore, in hertz (12.5 GHz)

    t1 = 2 * (scipy.special.erfcinv(2 * BER)) ** 2 * (Rs / Bn)
    t2 = (14 / 3) * (scipy.special.erfcinv((3 / 2) * BER)) ** 2 * (Rs / Bn)
    t3 = 10 * (scipy.special.erfcinv((8 / 3) * BER)) ** 2 * (Rs / Bn)

    GSNR = np.linspace(0, 500)
    BR1 = []
    BR2 = []
    BR3 = []
    for i in GSNR:
        if i >= t1:
            BR1.append(100)
        else:
            BR1.append(0)

    for i in GSNR:
        if i < t1:
            BR2.append(0)
        elif t1 <= i < t2:
            BR2.append(100)
        elif t2 <= i < t3:
            BR2.append(200)
        else:
            BR2.append(400)

    for i in GSNR:
        BR3.append(2 * Rs * math.log(1 + i * (Rs / Bn), 2))

    #creating GSNR list for plotting
    l_GSNR = []
    for i in GSNR:
        l_GSNR.append(i)

    fig, ax = plt.subplots()
    ax.plot(l_GSNR, BR1)
    ax.plot(l_GSNR, BR2)
    ax.plot(l_GSNR, BR3)
    plt.show()

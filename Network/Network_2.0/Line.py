import math
import scipy.constants as con
import numpy as np


class Line:
    def __init__(self, label, length, in_node, out_node):
        self.opt_pow = 0.0
        self.ase = 0.0
        self.label = label
        self.length = length
        self.in_node = in_node
        self.out_node = out_node
        self.successive = {}
        self.state = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.n_amplifier = (length // 80000) + 2 #un amplificatore ogni 80 km, più quelli agli estremi
        self.gain = 16 #dB
        self.noiseFigure = 3 #dB    -> F
        #self.noiseFigure = 5 #dB    -> F
        self.Bn = pow(12.5, 9)
        self.in_service = 1     #1->in service  0-> out of service

        #attributi fisici della fibra
        self.alpha_dB = 0.2 * 0.001  #dB/m
        self.alpha = self.alpha_dB/(10* math.log10(np.e))
        self.L_eff = 1/self.alpha
        self.beta2_module = 2.13*pow(10, -26)  #(m*Hz^2)^-1
        #self.beta2_module = 0.26*pow(10, -26)
        self.gamma = 1.27*pow(10, -3)  #(m*W)^-1
        self.Rs = 32*pow(10, 9)    #Hz, giga
        self.df = 50*pow(10, 9)    #Hz, giga
        self.Nch = len(self.state)

        #self.nu_nli = 16 / (27 * np.pi) * np.log((np.pi**2) / 2 * (self.beta2_module * (self.Rs**2)) / self.alpha * pow(self.Nch, 2 * self.Rs / self.df)) * pow(self.gamma, 2) / (4 * self.alpha * self.beta2_module) * 1 / pow(self.Rs, 3)
        self.nu_nli = 16 / (27 * np.pi) * np.log(np.pi**2 * self.beta2_module * self.Rs**2 * self.Nch**(2*self.Rs/self.df) / (2 * self.alpha)) * self.gamma**2 / (4 * self.alpha * self.beta2_module *self.Rs**3)
        self.ase_Generation()   #ase statico
        #self.optimized_launch_power()

    def getLabel(self):
        return self.label

    def latency_generation(self, signal):
        signal.latencyUpdate(self.length/200000)

    def noise_generation(self, signal):
        # signal.noisePowUpdate(signal.signal_power * self.length * math.pow(10, -9)) vecchia versione
        #nuova versione:

        signal.noisePowUpdate(self.ase + self.nli_generation(signal.getPower()))


    def propagate(self, signal):
        self.latency_generation(signal)
        self.optimized_launch_power()
        self.nli_generation(signal.getPower())
        signal.setPower(self.opt_pow)
        self.noise_generation(signal)

        if self.state[signal.getChannel()] == 0:    #l'update dello stato del canale viene fatto altrove, nella occupy
            print("Errore propagazione: canale occupato")
            return

        self.out_node.propagate(signal)

    def getState(self):
        return self.state

    def getRs(self):
        return self.Rs

    def get_optimal_power(self):
        return self.opt_pow

    def occupy_state(self, freq):
        self.state[freq] = 0

    def getInNode(self):
        return self.in_node

    def getOutNode(self):
        return self.out_node


    def probe(self, path, pathLenght, signal):      #usato per creare la weightened table
        pathLenght[0] += self.length
        self.latency_generation(signal)
        self.optimized_launch_power()
        self.nli_generation(signal.getPower())
        signal.setPower(self.opt_pow)
        self.noise_generation(signal)
        self.out_node.probe(path, pathLenght, signal)
        return

    def ase_Generation(self):                                                   #NOTA: il rumore ase (Amplified Spontaneus Emission)  è il risultato dell'amplifiazione della luce nella
        freq = 193.414e12 #Hz, in questo caso teraHertz                   #fibra dall'EDFA; l'amplificatore intrduce contempranemante un guadagno e un rumore
        h = con.h
        Bn = 12.5e9 # noise bandwith, in Hz
        NF = 10 ** (self.noiseFigure / 10)
        G = 10 ** (self.gain / 10)

        self.ase = self.n_amplifier * (h * freq * Bn * NF * (G - 1))

    def nli_generation(self, power):   #NLI=Non Linear Inteference

        Bn = 12.5 * pow(10,9)
        Nspan = self.n_amplifier - 1     #"number of fiber span" -> ovvero il numero di tratti di fibra della linea = numero mplificatori - 1
        NLI = (float(power)**3) * self.nu_nli * Nspan * Bn
        return NLI

    def optimized_launch_power(self):
        F = 10 ** (self.noiseFigure / 10)
        G = 10 ** (self.gain / 10)
        f0 = 193.414 * pow(10,12)
        Nspan = self.n_amplifier - 1
        Bn = 12.5 * pow(10,9)

        #pow1 = ( (F * f0 * con.h * G) / (2 * self.nu_nli)) **(1/3)
        pow2 = (-self.ase / (self.nu_nli - 3 * self.nu_nli * Nspan *Bn)) ** (1/3)       #formula calcolata derivando la potenza e poenendola uguale a 0
        self.opt_pow = pow2

    def setOutOfOrder(self):
        self.in_service = 0

    def getServiceStatus(self):
        return self.in_service

    def resetChannel(self, ch):
        self.state[ch] = 1

    def no_ch_avail(self):
        for i in range(0,10):
            self.state[i] = 0

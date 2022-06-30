import math
import scipy.constants as con


class Line:
    def __init__(self, label, length):
        self.NLI = 0.0
        self.ase = 0.0
        self.label = label
        self.length = length
        self.successive = {}
        self.state = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.n_amplifier = (length // 80) + 2 #un amplificatore ogni 80 km, più quelli agli estremi
        self.gain = 16 #dB
        self.noiseFigure = 3 #dB    -> F

        #attributi fisici della fibra
        self.alpha_dB = pow(0.2, -3)   #dB/m
        self.alpha = self.alpha_dB/(20* math.log10(con.e))
        self.L_eff = 1/self.alpha
        self.beta2_module = pow(2.13, -26)  #(m*Hz^2)^-1
        self.gamma = pow(1.27, -3)  #(m*W)^-1
        self.Rs = pow(32, 9)    #Hz, giga
        self.df = pow(50, 9)    #Hz, giga
        self.Nch = len(self.state)
        self.nu_nli = 16/(23 * con.pi) * math.log10(pow( (con.pi), 2)/2 * (self.beta2_module * pow(self.Rs, 2)) /self.alpha * Nch * (self.Rs /self.df)) * pow(self.gamma, 2) / (4* self.alpha * self.beta2_module) * 1/pow(self.Rs, 3)
        self.ase_Generation()   #l'ase dipende solo dai parametri fisici, quindi è fisso per ogni linea

    def latency_generation(self, signal):
        signal.latencyUpdate(self.length/200000)

    def noise_generation(self, signal):
        # signal.noisePowUpdate(signal.signal_power * self.length * math.pow(10, -9)) vecchia versione

        #nuova versione:
        self.nli_generation(signal.getPower())
        signal.noisePowUpdate(signal.signal_power * self.NLI * self.ase)    #di questo non sono assolutamente sicuro

    def propagate(self, signal):
        self.noise_generation(signal)
        self.latency_generation(signal)
        if self.state[signal.getChannel()] == 1:
            self.state[signal.getChannel()] = 0
        else:
            print("Errore propagazione: canale occupato")
            return
        node = signal.nextHop()
        self.successive[node].propagate(signal)

    def getState(self):
        return self.state

    #def occupy(self):
    #    self.state = 0

    def probe(self, path, pathLenght):
        pathLenght[0] += self.length
        if len(path) == 0:
            return
        nextNode = path.pop(0)
        for nodes in self.successive:
            if nodes == nextNode:
                self.successive[nextNode].probe(path, pathLenght)
                break
        return

    def ase_Generation(self):                                                   #NOTA: il rumore ase (Amplified Spontaneus Emission)  è il risultato dell'amplifiazione della luce nella
        freq = pow(193.414, 12) #Hz, in questo caso teraHertz                   #fibra dall'EDFA; l'amplificatore intrduce contempranemante un guadagno e un rumore
        h = con.h
        Bn = pow(12.5, 9) # noise bandwith, in Hz

        self.ase = self.n_amplifier * (h * freq * Bn * self.noiseFigure * (self.gain - 1))

    def nli_generation(self, power):   #NLI=Non Linear Inteference

        Bn = pow(12.5,9)
        Nspan = self.n_amplifier - 1     #"number of fiber span" -> ovvero il numero di tratti di fibra della linea = numero mplificatori - 1
        self.NLI = pow(power, 3) * nu_nli * Nspan * Bn

    def optimized_launch_power(self):       #NOTA: problema: nelle richieste delle slide, viene detto di chiamare il metodo in propagate di Node; tuttavia, calcolato in questo modo, il launch power
                                            #è indipendente dal nodo o dal segnale specifico da cui è lanciato; non ha dunque senso ricalcolarlo ad ogni propagate
        #                            F                  L                      Gase
        #                           \/                  \/                      \/
        self.opt_pow=pow( (self.noiseFigure * (self.alpha * self.length) * self.ase) / (2 * self.nu_nli), 1/3)
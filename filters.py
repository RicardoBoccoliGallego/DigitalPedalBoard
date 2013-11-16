# -*- coding: utf-8 -*-
"""
Arquivo para guardar os filtros criados.
Todo filtro é uma instância da classe Filtro, que além
da função que trata o sinal, contém outras informações,
como parâmetros, nome, uso do pedal de expressão.
"""
from audiolazy import *
rate = 44100
s,Hz = sHz(rate)

"""
Funções que retornam Stream seguidas pela função que instancia o seu filtro com
seus parâmetros, nome, etc.
"""

 
def amp(signal, ganho, ganho_max):
    return ((ganho_max/2)*(ganho+1)) * signal
def amplificador(ganho_max=5.0):
    """
    Filtro que amplifica o sinal (ganho>1)
    """    
    dic = {u"Valor máximo da Amplificação":(5.0,float,(0.1,10))}
    inst = Filtro(amp, dic, u"Amplificador", True)
    inst.vparams[0] = ganho_max
    return inst
def low_pass (signal, cutoff):
        filt = lowpass(cutoff/(float(cutoff)))
        return filt(signal)
def passa_baixas(cutoff=700):
    """ 
    Filtro que atenua altas frequências
    """
    dic = {u"Frquência de Corte (Hz)":(700,int,(0,20000))}
    inst = Filtro(low_pass, dic, u"Passa Baixas")
    inst.vparams[0] = cutoff
    return inst

def echo (sig, echo_time):
        sig = thub(sig, 2)
        smixer = Streamix()
        smixer.add(0,sig)
        smixer.add(echo_time*s,sig)
        return smixer
def eco(delay=0.001):
    """
    Retorna uma instância do Eco
    """
    dic = {u"Intervalo (s)":(0.2,float,(0,5))}
    inst = Filtro(echo, dic, u"Eco")
    inst.vparams[0] = delay
    return inst

def high_pass (signal,cutoff):
        filt = highpass(cutoff*Hz)
        return filt(signal)
def passa_altas(cutoff=700):
    """  
    Filtro que atenua baixas frequências
    """
    dic = {u"Frquência de Corte (Hz)":(700,int,(0,20000))}
    inst = Filtro(high_pass, dic, u"Passa Altas")
    inst.vparams[0] = cutoff
    return inst
    
def all_pass (signal, cutoff):
        c = (tan(cutoff*pi/rate) - 1)/(tan(cutoff*pi/rate) + 1)
        filt = (z**-1 + c)/(1 + c*z**-1)
        return filt(signal)
def passa_tudo(cutoff=700):
    """ 
    Filtro que não muda a intensidade, apenas a fase da sua entrada
    """
   
    dic = {u"Frquência de 'Corte' (Hz)":(700,int,(0,20000))}
    inst = Filtro(all_pass, dic, u"Passa Tudo")
    inst.vparams[0] = cutoff
    return inst
    
def the_limiter(sig,threshold):
        sig = thub(sig, 2)
        size=256
        env=envelope.rms
        cutoff=pi/2048
        return sig * Stream( 1. if el <= threshold else threshold / el
               for el in maverage(size)(env(sig, cutoff=cutoff)) )

def limitador(threshold=.5):
    """ Filtro limitador. Limita as amplitudes ao limiar
    """
    dic = {u"Limiar":(.5,float,(0,1))}
    inst = Filtro(the_limiter, dic, u"Limitador")
    inst.vparams[0] = threshold
    return inst

def the_compressor(sig,threshold,slope):
        sig = thub(sig, 2)
        size=256
        env=envelope.rms
        cutoff=pi/2048
        return sig * Stream(1. if el <= threshold else (slope + threshold*(1 - slope)/el)
                for el in maverage(size)(env(sig, cutoff=cutoff)) )
def compressor(threshold=.5, slope=.5):
    """ Atenua os sons a partir de certo limiar com uma tangente
    """
    dic = {u"Limiar":(.5,float,(0,1)),
           u"Tangente":(.5,float,(0,1))}
    inst = Filtro(the_compressor, dic, u"Compressor")
    inst.vparams[0] = threshold
    inst.vparams[1] = slope
    return inst
    
@tostream
def distwire(sig,threshold):
        for el in sig:
            if builtins.abs(el) < threshold: yield el
            else: yield el/builtins.abs(el) - el
def dist_wire(threshold=.5):
    """ Distorção Wire
    """
    dic = {u"Limiar":(.5,float,(0,1))}
    inst = Filtro(distwire, dic, u"Distwire")
    inst.vparams[0] = threshold
    return inst


# Variável ControlStream (ou inteiro) com a entrada do pedal
pedal = 0.5
     
class Filtro:
    """ 
    Classe para os filtros
    params: Contém o dicionário que caracteriza o filtro
    vparams: Valores padrão dos parâmetros
    name: nome do filtro
    usa_pedal: Indica se o filtro usa ou não o valor do pedal de expressão
      
    """
    def __init__(self, fun, dic, name, usa_pedal=False):
        """        
        fun: Uma função que recebe um Stream e retorna outro Stream (além de outros parametros)
        dic: Dicionário que dá um nome para cada parametro do filtro e 
        o seu valor é uma tupla que contém (valor_padrao, tipo, (valor_inicial,valor_final))
         é uma tupla com os valores dos parâmetros
        
        A variável estatica filtros contém um dicionário definido pelo grupo de filtros e por uma tupla contendo
        as funções que instanciam os filtros
        """
        
        self.params = dic
        self.__fun = fun
        self.vparams = [valor[0] for valor in dic.values()]
        self.name = name
        self.usa_pedal=usa_pedal
   
    def __call__ (self, sig):
        if not self.usa_pedal:
            return (self.__fun(sig, *(tuple(self.vparams))))
        else:
            return (self.__fun(sig, pedal, *(tuple(self.vparams))))


    filtros = {u"Filtros Básicos": (passa_altas,passa_baixas,passa_tudo, amplificador)
            , u"Limitadores": (limitador,compressor)
    
                , u"Distorções": (dist_wire,)
                , u"Delays": (eco,)                
                }
        




  
def the_resonator (signal,freq,band):
    res = resonator(freq*Hz,band*Hz)
    return res(signal)
    

"""
Atenua as partes abaixo de certo limite
"""
def expander(sig,threshold,slope):
      sig = thub(sig, 2)
      size=256
      env=envelope.rms
      cutoff=pi/2048
      return sig * Stream(slope if el <= threshold else 0
                      for el in maverage(size)(env(sig, cutoff=cutoff)) )

"""
Atenua partes do sinal maior do que certo limite
"""



def phaser (sig, cutoff):
   # sig = thub(sig/2, 2)
    #func = (lambda sig: all_pass(sig,cutoff*Hz))
    return CascadeFilter(lambda signal: all_pass(signal,cutoff*(6+5*sinusoid(2*Hz))*Hz ) for param in xrange(7,8))(sig)
  #  return sig + all_pass(all_pass(all_pass(all_pass(sig,cutoff*1.2*Hz),cutoff*0.8*Hz),cutoff*1.05*Hz),cutoff*Hz)

def teste (samplefreq=44100):
      return (pi*samplefreq)/((pi*samplefreq)*2 + z**2)
            
def distortion1 (sig):
    gen = 10 + 5*sinusoid(5*Hz)    
    return atan(sig*gen)/(pi/2)

#Flanger -> Sinal + sinal c/ delay variante
def flanger (sig):
    variante = line(10.0*s,10.0*s/1000.0,30.0*s/1000.0)
    sig = thub(sig, 2)
    return sig 


"""digital_filters = {"lowpass": ["Passa-baixas",low_pass,("Frequência de Corte (Hz)"),(500)]
, "highpass": ["Passa-altas",high_pass,("Frequência de Corte (Hz)"),(800)]
, "ressonator": ["Ressonador",th  sig = thub(sig, 2)e_resonator,("Frequência Ressonante (Hz)","Tamanho da Banda (Hz)"),(800,100)]
, "limiter": ["Limitador",the_limiter,("Início (0-1)"),(0.5) ]
, "echo": ["Eco",echo,("Tempo de Eco (s)"),(0.05) ]
, "expander": ["Expansor",expander,("Fim (0-1), Fator (0-1)"),(0.5,0.001) ]
, "compressor": ["Compressor",compressor,("Início (0-1), Fator (0-1)"),(0.5,0.001) ]

    }
"""


""" #Teste de sexta
vabs = builtins.abs
@tostream
def distwire(sig):
    for el in sig:
        if vabs(el) < .5: yield el
        else: yield el/vabs(el) - el

with AudioIO(True) as saida:
    data = sinusoid(440*Hz)
    output = phaser(distwire(data),400) 
    saida.play(output)


"""


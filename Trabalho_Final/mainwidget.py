from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup, Leitura
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread, Lock
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph

from pymodbus.payload import BinaryPayloadBuilder, BinaryPayloadDecoder
from pymodbus.constants import Endian

class MainWidget(BoxLayout):
    """
    Widget principal da aplicação.
    """
    _updateThread = None
    _updateWidgets = True
    _tags={}
    _max_points = 20

    
    def __init__(self, **kwargs):
        """
        Construtor do widget principal da aplicação.
        """
        super().__init__()
        self._scan_time = kwargs.get('scan_time')
        self._serverIP = kwargs.get('server_ip')
        self._serverPort = kwargs.get('server_port') 
        self._modbusPopup = ModbusPopup(self._serverIP,self._serverPort)
        self._scanPopup = ScanPopup(self._scan_time)
        self._modbusClient = ModbusClient(host=self._serverIP,port=self._serverPort)
        self._meas={}
        self._meas['timestamp']=None
        self._meas['values']={}
        self._lock=Lock()
        self._leitura=Leitura()
        for key,value in kwargs.get('modbus_addrs').items():
            if key == 'Temperatura':
                plot_color = (1,0,0,1)
            else:
                plot_color = (random.random(), random.random(), random.random(), 1)
            self._tags[key] = {'addr': value, 'color': plot_color}
        self._graph = DataGraphPopup(self._max_points, self._tags['Temperatura']['color'])
        

    def startDataRead(self, ip, port):
        """
        Método utilizado para a configuração do IP e porta do servidor MODBUS e
        inicializar uma thread para a leitura dos dados e atualização da interface 
        gráfica
        """
        self._serverIP = ip
        self._serverPort = port
        self._modbusClient.host = self._serverIP
        self._modbusClient.port = self._serverPort
        try:
            Window.set_system_cursor("wait")
            self._modbusClient.open()
            Window.set_system_cursor("arrow")
            if self._modbusClient.is_open:
               self._updateThread = Thread(target=self.updater)
               self._updateThread.start()
               self.ids.img_con.source = 'imgs/conectado.png'
               self._modbusPopup.setInfo("")
               self._modbusPopup.dismiss()
            else:
               self._modbusPopup.setInfo("Falha na conexão com o servidor")
        except Exception as e:
            print("Erro: ",e.args)

    def updater(self):
        """
        Método que invoca as rotinas de leitura dos dados, atualização da interface
        inserção dos dados no Banco de dados
        """
        try:  
            while self._updateWidgets:
                self.readData()
                self.updateGUI()
                sleep(self._scan_time/1000)
        except Exception as e:
            self._modbusClient.close()
            print("Erro: ", e.args)

    def readData(self):
        """
        Método para a leitura dos dados por meio do protocolo MODBUS
        """
        self._meas['timestamp'] = datetime.now()
        for key,value in self._tags.items():
            self._meas['values'][key] = self.read_float_point(self._tags[key]["addr"])

    def read_float_point(self, endereco):
        leitura= self._modbusClient.read_holding_registers(endereco,2)
        decoder = BinaryPayloadDecoder.fromRegisters(leitura, byteorder = Endian.BIG, wordorder = Endian.LITTLE)

        return decoder.decode_32bit_float()

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos
        """
        # Atualização das labels específicas
        if 'Velocidade_saida_ar' in self.ids:
            self.ids.Velocidade_saida_ar.text = f"{round(self._meas['values']['Velocidade_saida_ar'],2)} m/s"
        
        if 'Vazao_saida_ar' in self.ids:
            self.ids.Vazao_saida_ar.text = f"{round(self._meas['values']['Vazao_saida_ar'],2)} m³/s"
        
        if 'Temperatura' in self.ids:
            self.ids.Temperatura.text = f"{round(self._meas['values']['Temperatura'],2)} °C"

        # Atualização do nível do termômetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['Temperatura']/45*self.ids.termometro.size[1])

        # Atualização do gráfico
        self._graph.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['Temperatura']),0)

    def stopRefresh(self):
        self._updateWidgets = False


    def liga_motor(self):

        with self._lock:
            partida_ativa = self._modbusClient.read_holding_registers(1216,1)[0]

            if partida_ativa == 1:
                self._modbusClient.write_single_register(1316,1)
            if partida_ativa == 2:
                self._modbusClient.write_single_register(1312,1)
            if partida_ativa == 3:
                self._modbusClient.write_single_register(1319,1)
            pass


    def desliga_motor(self):

        with self._lock:
            reset_ativa = self._modbusClient.read_holding_registers(1216,1)[0]

            if reset_ativa == 1:
                self._modbusClient.write_single_register(1316,0)
            if reset_ativa == 2:
                self._modbusClient.write_single_register(1312,0)
            if reset_ativa == 3:
                self._modbusClient.write_single_register(1319,0)
            pass

    def reset_motor(self):

        with self._lock:
            partida_ativa = self._modbusClient.read_holding_registers(1312,1)[0]

            if partida_ativa == 1:
                self._modbusClient.write_single_register(1316,2)
            if partida_ativa == 2:
                self._modbusClient.write_single_register(1312,2)
            if partida_ativa == 3:
                self._modbusClient.write_single_register(1319,2)
            pass


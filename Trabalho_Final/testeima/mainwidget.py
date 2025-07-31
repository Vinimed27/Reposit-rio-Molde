from kivy.uix.boxlayout import BoxLayout
from popups import ModbusPopup, ScanPopup, DataGraphPopup
from pyModbusTCP.client import ModbusClient
from kivy.core.window import Window
from threading import Thread
from time import sleep
from datetime import datetime
import random
from timeseriesgraph import TimeSeriesGraph

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
                # 
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
            self._meas['values'][key] = self._modbusClient.read_holding_registers(value['addr'],1)[0]

    def updateGUI(self):
        """
        Método para atualização da interface gráfica a partir dos dados lidos
        """
        # Atualização das labels específicas
        if 'Velocidade_saida_ar' in self.ids:
            self.ids.Velocidade_saida_ar.text = f"{self._meas['values']['Velocidade_saida_ar']} m/s"
        
        if 'Vazao_saida_ar' in self.ids:
            self.ids.Vazao_saida_ar.text = f"{self._meas['values']['Vazao_saida_ar']} m³/s"
        
        if 'Temperatura' in self.ids:
            self.ids.Temperatura.text = f"{self._meas['values']['Temperatura']} °C"

        # Atualização do nível do termômetro
        self.ids.lb_temp.size = (self.ids.lb_temp.size[0],self._meas['values']['Temperatura']/45*self.ids.termometro.size[1])

        # Atualização do gráfico
        self._graph.ids.graph.updateGraph((self._meas['timestamp'],self._meas['values']['Temperatura']),0)

    def stopRefresh(self):
        self._updateWidgets = False
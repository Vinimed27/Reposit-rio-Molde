import os 
os.environ['KIVY_GL_BACKEND'] = 'angle_sdl2'
from kivy.app import App
from mainwidget import MainWidget
from kivy.lang.builder import Builder


class MainApp(App):
    """
    Classe com o aplicativo
    """
    
    def build(self):
        """
        Método que gera o aplicativo com o widget principal
        """
        self._widget = MainWidget(scan_time=1000, server_ip='10.15.30.183',server_port=502,
        modbus_addrs = {
            'Velocidade_saida_ar': 712,
            'Vazao_saida_ar': 714,
            'Temperatura': 710,
            'Med_demanda': 1205,
            'Velocidade_compresor': 1236,
            'Alarme_Temperatura_baixa': 1231,
            'Corrente_media': 845,
            'DDP_fases': 840,
            'temp_rolamento': 700,
            'Corrente_comp': 726,
            'Potencia_ativa': 735,
            'potencia_aparente': 743,
            'fator_de_pontencis': 747

        },
        )

        return self._widget

    def on_stop(self):
        """
        Método executado quando a aplicação é fechada
        """
        self._widget.stopRefresh()

if __name__ == '__main__':
    Builder.load_string(open("mainwidget.kv",encoding="utf-8").read(),rulesonly=True)
    Builder.load_string(open("popups.kv",encoding="utf-8").read(),rulesonly=True)
    MainApp().run()

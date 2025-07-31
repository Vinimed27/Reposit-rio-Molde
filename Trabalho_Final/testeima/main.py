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
        self._widget = MainWidget(scan_time=1000, server_ip='127.0.0.1',server_port=502,
        modbus_addrs = {
            'Velocidade_saida_ar': 1004,
            'Vazao_saida_ar': 1005,
            'Temperatura': 1002,
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

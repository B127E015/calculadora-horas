
__version__ = "1.0.0"

import os
import json
from datetime import datetime

from kivy.app import App
from kivy.metrics import dp, sp
from kivy.core.clipboard import Clipboard
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup


class CalculadoraHoras(App):

    def build(self):
        self.title = "Calculadora de Horas"

        self.entrada = ""
        self.acumulador = None
        self.operacao = None
        self.aguardando_numero = False
        self.resultado_atual = None
        self.expressao = ""

        self.arquivo_historico = os.path.join(
            self.user_data_dir,
            "historico_calculadora.json"
        )

        self.historico = self.carregar_historico()

        principal = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(8)
        )

        titulo = Label(
            text="CALCULADORA DE HORAS",
            font_size=sp(20),
            bold=True,
            size_hint_y=0.12
        )
        principal.add_widget(titulo)

        self.label_expressao = Label(
            text="",
            font_size=sp(18),
            size_hint_y=0.10,
            halign="right",
            valign="middle"
        )
        self.label_expressao.bind(
            size=self.ajustar_texto
        )
        principal.add_widget(self.label_expressao)

        self.display = Label(
            text="00:00",
            font_size=sp(42),
            bold=True,
            size_hint_y=0.22,
            halign="right",
            valign="middle"
        )
        self.display.bind(size=self.ajustar_texto)
        principal.add_widget(self.display)

        botoes = GridLayout(
            cols=4,
            spacing=dp(7),
            size_hint_y=0.56
        )

        teclas = [
            ("AC", self.limpar, "#B84A4A"),
            ("DEL", self.apagar, "#555555"),
            ("Histórico", self.abrir_historico, "#555555"),
            ("+", lambda: self.escolher_operacao("+"), "#287AAB"),

            ("7", lambda: self.digitar("7"), "#333333"),
            ("8", lambda: self.digitar("8"), "#333333"),
            ("9", lambda: self.digitar("9"), "#333333"),
            ("−", lambda: self.escolher_operacao("-"), "#287AAB"),

            ("4", lambda: self.digitar("4"), "#333333"),
            ("5", lambda: self.digitar("5"), "#333333"),
            ("6", lambda: self.digitar("6"), "#333333"),
            ("00", lambda: self.digitar("00"), "#333333"),

            ("1", lambda: self.digitar("1"), "#333333"),
            ("2", lambda: self.digitar("2"), "#333333"),
            ("3", lambda: self.digitar("3"), "#333333"),
            ("0", lambda: self.digitar("0"), "#333333"),

            ("=", self.calcular, "#218838"),
        ]

        for texto, funcao, cor in teclas:
            botao = Button(
                text=texto,
                font_size=sp(22),
                background_normal="",
                background_color=self.cor(cor)
            )

            botao.bind(
                on_release=lambda btn, f=funcao: f()
            )

            botoes.add_widget(botao)

        principal.add_widget(botoes)

        return principal

    def cor(self, hexadecimal):
        hexadecimal = hexadecimal.replace("#", "")

        return tuple(
            int(hexadecimal[i:i + 2], 16) / 255
            for i in (0, 2, 4)
        ) + (1,)

    def ajustar_texto(self, instancia, tamanho):
        instancia.text_size = tamanho

    def formatar(self, minutos):
        sinal = "-" if minutos < 0 else ""
        minutos = abs(int(minutos))

        horas = minutos // 60
        resto = minutos % 60

        return f"{sinal}{horas:02d}:{resto:02d}"

    def obter_valor(self):
        if not self.entrada:
            return 0

        valor = self.entrada.zfill(3)

        horas = int(valor[:-2])
        minutos = int(valor[-2:])

        if minutos >= 60:
            raise ValueError(
                "Os minutos devem estar entre 00 e 59."
            )

        return horas * 60 + minutos

    def digitar(self, numero):

        if self.aguardando_numero:
            self.entrada = ""
            self.aguardando_numero = False

        elif self.resultado_atual is not None:
            self.entrada = ""
            self.resultado_atual = None
            self.expressao = ""
            self.label_expressao.text = ""

        nova_entrada = self.entrada + numero

        if len(nova_entrada) > 8:
            return

        valor = nova_entrada.zfill(3)

        if int(valor[-2:]) >= 60:
            return

        self.entrada = nova_entrada

        self.display.text = self.formatar(
            self.obter_valor()
        )

    def escolher_operacao(self, nova_operacao):

        try:
            if self.operacao is not None:

                if self.aguardando_numero:
                    self.operacao = nova_operacao

                    self.expressao = (
                        self.expressao[:-1] + nova_operacao
                    )

                    self.label_expressao.text = self.expressao
                    return

                segundo_valor = self.obter_valor()

                if self.operacao == "+":
                    self.acumulador += segundo_valor
                else:
                    self.acumulador -= segundo_valor

                self.entrada = ""

                self.display.text = self.formatar(
                    self.acumulador
                )

                self.expressao += (
                    " " + self.formatar(segundo_valor)
                    + " " + nova_operacao
                )

            else:

                if self.resultado_atual is not None:
                    self.acumulador = self.resultado_atual

                    self.expressao = self.formatar(
                        self.resultado_atual
                    )

                else:
                    self.acumulador = self.obter_valor()

                    self.expressao = self.formatar(
                        self.acumulador
                    )

                self.expressao += " " + nova_operacao

            self.operacao = nova_operacao
            self.aguardando_numero = True
            self.resultado_atual = None

            self.label_expressao.text = self.expressao

        except ValueError as erro:
            self.mostrar_erro(str(erro))

    def calcular(self):

        if self.operacao is None or self.aguardando_numero:
            return

        try:
            segundo_valor = self.obter_valor()

            if self.operacao == "+":
                resultado = self.acumulador + segundo_valor
            else:
                resultado = self.acumulador - segundo_valor

            expressao_completa = (
                self.expressao + " "
                + self.formatar(segundo_valor)
            )

            resultado_formatado = self.formatar(resultado)

            self.display.text = resultado_formatado

            self.label_expressao.text = (
                expressao_completa + " ="
            )

            registro = {
                "expressao": expressao_completa,
                "resultado": resultado_formatado,
                "data": datetime.now().strftime(
                    "%d/%m/%Y %H:%M"
                )
            }

            self.historico.insert(0, registro)
            self.salvar_historico()

            self.resultado_atual = resultado
            self.entrada = ""
            self.acumulador = None
            self.operacao = None
            self.aguardando_numero = True
            self.expressao = ""

        except ValueError as erro:
            self.mostrar_erro(str(erro))

    def limpar(self):
        self.entrada = ""
        self.acumulador = None
        self.operacao = None
        self.aguardando_numero = False
        self.resultado_atual = None
        self.expressao = ""

        self.display.text = "00:00"
        self.label_expressao.text = ""

    def apagar(self):

        if self.aguardando_numero:
            return

        self.entrada = self.entrada[:-1]

        self.display.text = self.formatar(
            self.obter_valor()
        )

    def carregar_historico(self):

        if not os.path.exists(self.arquivo_historico):
            return []

        try:
            with open(
                self.arquivo_historico,
                "r",
                encoding="utf-8"
            ) as arquivo:

                dados = json.load(arquivo)

            return dados if isinstance(dados, list) else []

        except (OSError, json.JSONDecodeError):
            return []

    def salvar_historico(self):

        try:
            with open(
                self.arquivo_historico,
                "w",
                encoding="utf-8"
            ) as arquivo:

                json.dump(
                    self.historico,
                    arquivo,
                    ensure_ascii=False,
                    indent=4
                )

        except OSError:
            self.mostrar_erro(
                "Não foi possível salvar o histórico."
            )

    def mostrar_erro(self, mensagem):

        popup = Popup(
            title="Atenção",
            content=Label(
                text=mensagem,
                halign="center"
            ),
            size_hint=(0.85, 0.3)
        )

        popup.open()

    def abrir_historico(self, *args):

        conteudo = BoxLayout(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(10)
        )

        conteudo.add_widget(Label(
            text="Histórico de cálculos",
            font_size=sp(19),
            bold=True,
            size_hint_y=None,
            height=dp(40)
        ))

        rolagem = ScrollView()

        lista = GridLayout(
            cols=1,
            spacing=dp(8),
            size_hint_y=None
        )

        lista.bind(
            minimum_height=lista.setter("height")
        )

        if not self.historico:
            lista.add_widget(Label(
                text="Nenhum cálculo registrado.",
                size_hint_y=None,
                height=dp(60)
            ))

        for item in self.historico:

            cartao = BoxLayout(
                orientation="vertical",
                padding=dp(8),
                spacing=dp(5),
                size_hint_y=None,
                height=dp(145)
            )

            cartao.add_widget(Label(
                text=item.get("data", ""),
                font_size=sp(12),
                size_hint_y=0.22
            ))

            cartao.add_widget(Label(
                text=item.get("expressao", ""),
                font_size=sp(15),
                size_hint_y=0.25
            ))

            cartao.add_widget(Label(
                text="Resultado: " + item.get("resultado", ""),
                font_size=sp(19),
                bold=True,
                size_hint_y=0.25
            ))

            acoes = BoxLayout(
                size_hint_y=0.35,
                spacing=dp(5)
            )

            copiar = Button(
                text="Copiar",
                background_normal="",
                background_color=self.cor("#287AAB")
            )

            copiar.bind(
                on_release=lambda btn, valor=item.get(
                    "resultado", ""
                ): self.copiar(valor)
            )

            excluir = Button(
                text="Excluir",
                background_normal="",
                background_color=self.cor("#B84A4A")
            )

            excluir.bind(
                on_release=lambda btn, registro=item: (
                    self.excluir_registro(registro, janela)
                )
            )

            acoes.add_widget(copiar)
            acoes.add_widget(excluir)

            cartao.add_widget(acoes)
            lista.add_widget(cartao)

        rolagem.add_widget(lista)
        conteudo.add_widget(rolagem)

        botoes_inferiores = BoxLayout(
            size_hint_y=None,
            height=dp(48),
            spacing=dp(8)
        )

        limpar_tudo = Button(
            text="Limpar histórico",
            background_normal="",
            background_color=self.cor("#B84A4A")
        )

        fechar = Button(
            text="Fechar",
            background_normal="",
            background_color=self.cor("#555555")
        )

        limpar_tudo.bind(
            on_release=lambda btn: self.confirmar_limpeza(janela)
        )

        fechar.bind(
            on_release=lambda btn: janela.dismiss()
        )

        botoes_inferiores.add_widget(limpar_tudo)
        botoes_inferiores.add_widget(fechar)

        conteudo.add_widget(botoes_inferiores)

        janela = Popup(
            title="",
            content=conteudo,
            size_hint=(0.95, 0.85)
        )

        janela.open()

    def copiar(self, valor):
        Clipboard.copy(valor)
        self.mostrar_erro("Resultado copiado!")

    def excluir_registro(self, registro, janela):

        if registro in self.historico:
            self.historico.remove(registro)
            self.salvar_historico()

        janela.dismiss()
        self.abrir_historico()

    def confirmar_limpeza(self, janela):

        conteudo = BoxLayout(
            orientation="vertical",
            spacing=dp(12),
            padding=dp(12)
        )

        conteudo.add_widget(Label(
            text="Deseja apagar todo o histórico?"
        ))

        botoes = BoxLayout(
            size_hint_y=None,
            height=dp(45),
            spacing=dp(8)
        )

        sim = Button(text="Sim")
        nao = Button(text="Cancelar")

        popup = Popup(
            title="Confirmar",
            content=conteudo,
            size_hint=(0.85, 0.35)
        )

        def apagar_tudo(*args):
            self.historico.clear()
            self.salvar_historico()
            popup.dismiss()
            janela.dismiss()
            self.abrir_historico()

        sim.bind(on_release=apagar_tudo)
        nao.bind(on_release=lambda btn: popup.dismiss())

        botoes.add_widget(sim)
        botoes.add_widget(nao)

        conteudo.add_widget(botoes)

        popup.open()


if __name__ == "__main__":
    CalculadoraHoras().run()

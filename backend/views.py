from django.shortcuts import render
from rest_framework import viewsets, generics

# Create your views here.
from backend.models import Report
from backend.serializers import ReportSerializer,SettingsReportSerializer
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from .models import Report
from io import BytesIO
from datetime import datetime

from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from .models import Report,SettingsReport
from datetime import datetime
class ReportViewSet(viewsets.ModelViewSet):
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    #permission_classes = [permissions.AllowAny]

    queryset = Report.objects.all()
    serializer_class = ReportSerializer
    http_method_names = ['get', 'post', 'put', 'path','delete']

class SettingsReportViewSet(viewsets.ModelViewSet):
    #authentication_classes = [SessionAuthentication, BasicAuthentication]
    #permission_classes = [DjangoModelPermissionsOrAnonReadOnly]
    #permission_classes = [permissions.AllowAny]

    queryset = SettingsReport.objects.all()
    serializer_class = SettingsReportSerializer
    http_method_names = ['get', 'post', 'put', 'path','delete']
from django.shortcuts import render
from rest_framework import viewsets
from backend.models import Report, SettingsReport
from backend.serializers import ReportSerializer, SettingsReportSerializer
from django.http import HttpResponse
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from datetime import datetime
import matplotlib.pyplot as plt

class PDFGenerator:
    def __init__(self, queryset):
        self.queryset = queryset
        self.buffer = BytesIO()
        self.pdf = canvas.Canvas(self.buffer, pagesize=letter)
        self.configurar_estilo()

    def configurar_estilo(self):
        # Configurações de estilo
        self.margem_esquerda = 30
        self.margem_inferior = 50
        self.largura_pagina, self.altura_pagina = letter

        # Fontes
        self.pdf.setFont("Helvetica-Bold", 12)
        self.pdf.setFont("Helvetica", 11)

    def adicionar_capa(self):
        # Adicionar capa com título e nome da empresa
        try:
            settings_report = SettingsReport.objects.first()
            nome_empresa = settings_report.name if settings_report else "Nome da Sua Empresa"
        except SettingsReport.DoesNotExist:
            nome_empresa = "Nome da Sua Empresa"

        self.pdf.setFont("Helvetica-Bold", 24)
        self.pdf.drawCentredString(self.largura_pagina / 2, self.altura_pagina / 2 + 100, "Relatório de Vulnerabilidades")
        self.pdf.setFont("Helvetica-Bold", 16)
        self.pdf.drawCentredString(self.largura_pagina / 2, self.altura_pagina / 2 + 50, nome_empresa)

        # Adicionar data
        self.adicionar_data()

        self.pdf.showPage()  # Nova página após a capa

    def adicionar_data(self):
        # Obter data atual
        data_atual = datetime.now().strftime('%d/%m/%Y')
        
        # Posicionar a data no canto inferior direito
        self.pdf.setFont("Helvetica", 10)
        self.pdf.drawString(self.largura_pagina - self.margem_esquerda - 100, self.margem_inferior - 20, f"Data: {data_atual}")

    def adicionar_aviso_legal(self):
        # Texto do aviso legal

        self.pdf.drawString(self.margem_esquerda, self.altura_pagina - self.margem_inferior - 50, "2. Aviso Legal")

        aviso_legal = """
Aviso Legal

O Pentest foi realizado durante o período de 15/02/2023 até 26/02/2023. As constatações e recomendações refletem as informações coletadas durante a avaliação e estado do ambiente naquele momento e não quaisquer alterações realizadas posteriormente fora deste período.

O trabalho desenvolvido pela MEIRA SEC NÃO tem como objetivo corrigir as possíveis vulnerabilidades, nem proteger a CONTRATANTE contra ataques internos e externos, nosso objetivo é fazer um levantamento dos riscos e recomendar formas para minimizá-los.

As recomendações sugeridas neste relatório devem ser testadas e validadas pela equipe técnica da empresa CONTRATANTE antes de serem implementadas no ambiente em produção. A MEIRA SEC não se responsabiliza por essa implementação e possíveis impactos que possam vir a ocorrer em outras aplicações ou serviços.
"""

        # Configurações para o texto do aviso legal
        self.pdf.setFont("Helvetica", 11)
        margem = 50  # Margem esquerda do texto
        y = self.altura_pagina - self.margem_inferior

        # Dividir o texto em linhas e ajustar a posição Y para cada linha
        linhas = aviso_legal.splitlines()
        for linha in linhas:
            self.pdf.drawString(self.margem_esquerda + margem, y, linha.strip())
            y -= 15  # Ajustar para a próxima linha

        self.pdf.showPage()  # Nova página após o aviso legal

    def adicionar_sumario_executivo(self):
        # Calcular a distribuição de riscos
        riscos = {
            'Baixo': 0,
            'Médio': 0,
            'Alto': 0,
            'Crítica': 0
        }
        self.pdf.drawString(self.margem_esquerda, self.altura_pagina - self.margem_inferior - 50, "1. Sumário")

        for report in self.queryset:
            if report.risco == 'Baixo':
                riscos['Baixo'] += 1
            elif report.risco == 'Médio':
                riscos['Médio'] += 1
            elif report.risco == 'Alto':
                riscos['Alto'] += 1
            elif report.risco == 'Crítica':
                riscos['Crítica'] += 1

        # Preparar dados para o gráfico de pizza
        labels = []
        sizes = []
        colors = []

        for risco, quantidade in riscos.items():
            if quantidade > 0:
                labels.append(risco)
                sizes.append(quantidade)
                if risco == 'Crítica':
                    colors.append('#B80000')  # Vermelho escuro para crítico
                elif risco == 'Alto':
                    colors.append('#FFA500')  # Laranja para alto
                elif risco == 'Médio':
                    colors.append('#FFD700')  # Amarelo para médio
                elif risco == 'Baixo':
                    colors.append('#32CD32')  # Verde para baixo

        if not sizes:
            # Caso não haja dados para exibir no gráfico
            self.pdf.drawString(self.margem_esquerda, self.altura_pagina - self.margem_inferior - 200,
                                "Não há dados disponíveis para o gráfico de pizza.")
        else:
            # Gerar gráfico de pizza apenas se houver dados
            fig, ax = plt.subplots()
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, colors=colors)
            ax.axis('equal')  # Assegura que o gráfico de pizza é desenhado como um círculo

            # Salvar gráfico como imagem temporária
            img_path = '/tmp/grafico_riscos.png'
            plt.savefig(img_path)
            plt.close()

            # Adicionar imagem ao PDF
            img = ImageReader(img_path)
            self.pdf.drawImage(img, self.margem_esquerda, self.altura_pagina - self.margem_inferior - 200, width=300, height=300)

            self.pdf.setFont("Helvetica-Bold", 14)
            self.pdf.drawCentredString(self.largura_pagina / 2, self.altura_pagina - self.margem_inferior - 230,
                                    "Distribuição de Riscos das Vulnerabilidades")

        self.pdf.showPage()  # Nova página após o sumário executivo


    def adicionar_escopo(self):
        # Texto do escopo
        escopo = """
Escopo

Este relatório abrange as vulnerabilidades encontradas durante o Pentest realizado na rede corporativa da empresa X no período de 15/02/2023 a 26/02/2023.
"""

        # Configurações para o texto do escopo
        self.pdf.setFont("Helvetica-Bold", 14)
        self.pdf.drawString(self.margem_esquerda, self.altura_pagina - self.margem_inferior - 50, "3. Escopo")
        self.pdf.setFont("Helvetica", 11)
        margem = 50  # Margem esquerda do texto
        y = self.altura_pagina - self.margem_inferior - 70

        # Dividir o texto em linhas e ajustar a posição Y para cada linha
        linhas = escopo.splitlines()
        for linha in linhas:
            self.pdf.drawString(self.margem_esquerda + margem, y, linha.strip())
            y -= 15  # Ajustar para a próxima linha

        self.pdf.showPage()  # Nova página após o escopo

    def adicionar_metodologia(self):
        # Texto da metodologia
        metodologia = """
Metodologia

O Pentest foi realizado seguindo o método X para identificação de vulnerabilidades na infraestrutura de rede da empresa.
"""

        # Configurações para o texto da metodologia
        self.pdf.setFont("Helvetica-Bold", 14)
        self.pdf.drawString(self.margem_esquerda, self.altura_pagina - self.margem_inferior - 50, "4. Metodologia")
        self.pdf.setFont("Helvetica", 11)
        margem = 50  # Margem esquerda do texto
        y = self.altura_pagina - self.margem_inferior - 70

        # Dividir o texto em linhas e ajustar a posição Y para cada linha
        linhas = metodologia.splitlines()
        for linha in linhas:
            self.pdf.drawString(self.margem_esquerda + margem, y, linha.strip())
            y -= 15  # Ajustar para a próxima linha

        self.pdf.showPage()  # Nova página após a metodologia

    def adicionar_conteudo(self):
        # Adicionar título e subseções
        self.pdf.setFont("Helvetica-Bold", 18)
        self.pdf.drawCentredString(self.largura_pagina / 2, self.altura_pagina - self.margem_inferior - 30, "Conteúdo Detalhado")

        # Definir o conteúdo do PDF
        y = self.altura_pagina - self.margem_inferior - 60
        for report in self.queryset:
            # Verificar se há espaço suficiente para o próximo item
            if y <= self.margem_inferior:
                self.pdf.showPage()  # Nova página
                y = self.altura_pagina - self.margem_inferior - 60  # Reiniciar posição Y para nova página

            self.pdf.setFont("Helvetica-Bold", 12)
            self.pdf.drawString(self.margem_esquerda, y, f'Título: {report.titulo}')
            self.pdf.setFont("Helvetica", 11)
            self.pdf.drawString(self.margem_esquerda, y - 20, f'Descrição: {report.descricao}')
            self.pdf.drawString(self.margem_esquerda, y - 40, f'Impacto: {report.impacto}')
            self.pdf.drawString(self.margem_esquerda, y - 60, f'Risco: {report.risco}')
            y -= 80  # Ajustar a posição para o próximo item

    def salvar_pdf(self):
        # Adicionar capa
        self.adicionar_capa()

        # Adicionar sumário executivo
        self.adicionar_sumario_executivo()

        # Adicionar aviso legal
        self.adicionar_aviso_legal()

        # Adicionar escopo
        self.adicionar_escopo()

        # Adicionar metodologia
        self.adicionar_metodologia()

        # Adicionar conteúdo
        self.adicionar_conteudo()

        # Concluir e salvar o PDF
        self.pdf.save()

    def get_pdf_bytes(self):
        self.buffer.seek(0)
        return self.buffer.getvalue()


def gerar_pdf(request):
    # Recuperar todos os relatórios do banco de dados
    reports = Report.objects.all()

    # Inicializar o gerador de PDF
    pdf_generator = PDFGenerator(reports)

    # Inicializar a resposta HTTP
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="relatorio.pdf"'

    # Gerar e escrever o PDF na resposta
    pdf_generator.salvar_pdf()
    response.write(pdf_generator.get_pdf_bytes())

    return response

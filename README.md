🏛️ Integrador Receita

Gerenciador centralizado dos programas da Receita Federal do Brasil.

O Integrador Receita permite baixar, instalar e executar os principais programas tributários da Receita Federal (IRPF, DIRF, DCTF, Receitanet, SPED etc.) a partir de uma única interface gráfica em Windows, com estrutura organizada de pastas, logs e atalhos.
📋 Índice

    Visão Geral
    Funcionalidades
    Requisitos
    Instalação do Integrador
    Como Usar
        Primeira execução
        Baixar e instalar um programa
        Reconhecimento de programas instalados (pasta Atalhos)
        Executar um programa instalado
        Verificar atualizações 
    Estrutura de Pastas
    Configuração de Programas (versionsjson)
    Execução em Modo Desenvolvimento
    Empacotamento em .exe Portátil
    Soluções de Problemas
    Contribuição
    Licença

🧾 Visão Geral

O Integrador Receita foi criado para:

    Centralizar o uso dos programas da Receita Federal em um único lugar;
    Automatizar download e organização dos instaladores oficiais;
    Oferecer uma forma simples de reconhecer e executar programas já instalados, via atalhos;
    Manter uma estrutura de pastas portátil, que pode ser copiada para qualquer máquina Windows;
    Fornecer logs detalhados para facilitar suporte e diagnóstico de problemas.

Programas suportados (definidos em data/versions.json):

    IRPF 2025
    IRPF 2024
    DIRF 2025
    DCTF 2025
    Receitanet
    Receitanet BX
    SPED Contribuições
    SPED EFD
    SPED Fiscal
    SPED ICMS/IPI

✨ Funcionalidades

    Interface gráfica (Tkinter) com lista de programas, status e botões de ação
    Download automático dos instaladores oficiais (URLs da Receita Federal)
    Organização automática dos instaladores na pasta Instaladores/
    Reconhecimento de instalação via atalhos na pasta Atalhos/
    Execução centralizada dos programas instalados, abrindo o atalho .lnk
    Verificação de atualizações com base no versions.json
    Logs detalhados em logs/loggerReport.log
    Portátil: o diretório do Integrador pode ser copiado para outra máquina e usado sem reconfiguração

💻 Requisitos

    Windows 10 ou 11 (64 bits)
    Python 3.8 ou superior instalado
    Pacotes Python necessários:

pip install requests pywin32

📦 Instalação do Integrador

    Clonar o repositório

git clone https://github.com/SEU_USUARIO/IntegradorReceita.git
cd IntegradorReceita

    Instalar as dependências


pip install requests pywin32

    Executar o programa


python main.py

🚀 Como Usar
Primeira execução

Na primeira execução:

    O sistema cria automaticamente as pastas Instaladores/, Atalhos/ e logs/;
    Carrega a lista de programas do arquivo data/versions.json;
    Exibe a interface com um banner informando que os atalhos devem ficar na pasta Atalhos.

Baixar e instalar um programa

    Abra o Integrador (python main.py);
    Dê duplo clique em um programa com status "Não Instalado";
    Confirme o download quando aparecer a pergunta;
    O instalador será baixado para Instaladores/ e iniciado automaticamente;
    Conclua a instalação normalmente (você pode escolher qualquer diretório no Windows).

Reconhecimento de programas instalados (pasta Atalhos)

O Integrador reconhece um programa como "Instalado" quando:

    Existe um atalho .lnk correspondente na pasta Atalhos/;
    O nome desse atalho é exatamente o mesmo definido em atalho_nome no versions.json.

Passo a passo:

    Após instalar o programa, localize o executável (.exe);
    Clique com o botão direito → Criar atalho;
    Copie o atalho para IntegradorReceita/Atalhos/;
    Renomeie o atalho para o nome configurado em versions.json;
    No Integrador, clique em "🔄 Atualizar Lista".

Exemplo:

    atalho_nome no versions.json: "IRPF 2025.lnk"
    Arquivo na pasta: IntegradorReceita/Atalhos/IRPF 2025.lnk

Executar um programa instalado

    Duplo clique em um programa com status "Instalado";
    O Integrador abre o atalho .lnk na pasta Atalhos/;
    Se o atalho estiver incorreto ou ausente, o sistema mostra uma mensagem explicando como criar/ajustar o atalho.

Verificar atualizações

    Clique em "🔍 Verificar Atualizações";
    O sistema compara as versões locais com versao_disponivel do versions.json;
    Se houver atualizações, os programas são listados em uma mensagem.

📁 Estrutura de Pastas

IntegradorReceita/
│
├── main.py                    # Arquivo principal
├── README.md                  # Este arquivo
│
├── core/
│   ├── __init__.py
│   ├── paths.py               # Gerenciamento de caminhos
│   ├── logger.py              # Sistema de logs
│   ├── programs_registry.py   # Registro de programas
│   └── updater.py             # Download e instalação
│
├── ui/
│   ├── __init__.py
│   └── main_window.py         # Janela principal (Tkinter)
│
├── data/
│   └── versions.json          # Lista de programas e URLs
│
├── Instaladores/              # Arquivos .exe baixados
│   └── IRPF2025Win64v1.7.exe  # Exemplo
│
├── Atalhos/                   # Atalhos .lnk dos programas
│   └── IRPF 2025.lnk          # Exemplo
│
└── logs/
    └── loggerReport.log       # Log principal

🔧 Configuração de Programas (versions.json)

Exemplo de entrada:
json

{
  "IRPF2025": {
    "nome": "IRPF 2025",
    "versao_disponivel": "1.7",
    "url_download": "https://downloadirpf.receita.fazenda.gov.br/.../IRPF2025Win64v1.7.exe",
    "nome_arquivo": "IRPF2025Win64v1.7.exe",
    "atalho_nome": "IRPF 2025.lnk",
    "descricao": "Declaração do Imposto de Renda Pessoa Física 2025"
  }
}

Para adicionar novo programa, siga o mesmo modelo, criando novas chaves no JSON.
🧪 Execução em Modo Desenvolvimento

    Interface:

python -m ui.main_window

    Registro de programas:

python -m core.programs_registry

    Updater:

python -m core.updater

📦 Empacotamento em .exe Portátil

    Instalar PyInstaller:

pip install pyinstaller

    Gerar executável:

pyinstaller --onefile --windowed main.py

    Distribuir o .exe junto com:

    data/
    Atalhos/
    Instaladores/
    logs/ (será criada se não existir)

🐛 Soluções de Problemas

Programa não aparece como "Instalado"

    Verificar se:
        Existe atalho .lnk em Atalhos/;
        Nome do atalho = atalho_nome em versions.json;
        Clicou em "🔄 Atualizar Lista". 

Download falha

    Testar a URL do versions.json no navegador;
    Verificar conexão;
    Consultar logs/loggerReport.log.

Instalador não abre

    Executar manualmente o .exe em Instaladores/;
    Verificar permissões de administrador;
    Consultar o log para detalhes.

🤝 Contribuição

    Fazer fork;
    Criar branch:

git checkout -b feature/minha-melhoria

    Commitar:

git commit -m "Adiciona minha-melhoria"

    Enviar:

```bash git push origin feature/minha-melhoria

    Abrir Pull Request.

📄 Licença

Projeto de código aberto para fins educacionais e automação pessoal.

Os programas da Receita Federal são propriedade do Governo Federal do Brasil e seguem suas próprias licenças.

Integrador Receita – Centralizando os programas da Receita Federal em um único lugar.
# 🏛️ Integrador Receita

Gerenciador centralizado dos programas da Receita Federal do Brasil.

O Integrador permite **baixar, instalar e executar** os principais programas da Receita Federal (IRPF, DIRF, DCTF, Receitanet, SPED etc.) a partir de uma única interface, de forma organizada e portátil.

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Requisitos](#-requisitos)
- [Instalação do Integrador](#-instalação-do-integrador)
- [Como Usar](#-como-usar)
  - [Baixar e instalar um programa](#baixar-e-instalar-um-programa)
  - [Reconhecimento de programas instalados (pasta Atalhos)](#reconhecimento-de-programas-instalados-pasta-atalhos)
  - [Executar um programa instalado](#executar-um-programa-instalado)
  - [Verificar atualizações](#verificar-atualizações)
- [Estrutura de Pastas](#-estrutura-de-pastas)
- [Configuração de Programas (versionsjson)](#-configuração-de-programas-versionsjson)
- [Execução em Modo Desenvolvimento](#-execução-em-modo-desenvolvimento)
- [Soluções de Problemas](#-soluções-de-problemas)
- [Contribuição](#-contribuição)
- [Licença](#-licença)

---

## 🧾 Visão Geral

O **Integrador Receita** foi desenvolvido para:

- Centralizar o gerenciamento dos programas da Receita Federal;
- Evitar que o usuário tenha que procurar manualmente instaladores e atalhos;
- Manter uma estrutura de pastas organizada: instaladores, atalhos, logs, dados etc.;
- Ser **portátil**: pode ser copiado para qualquer pasta ou máquina Windows, mantendo seu funcionamento, desde que o Python e as dependências estejam instaladas.

Programas suportados inicialmente (exemplos):

- IRPF 2025
- IRPF 2024
- DIRF
- DCTF
- Receitanet
- Receitanet BX
- SPED Contribuições
- SPED EFD
- SPED Fiscal
- SPED ICMS/IPI

---

## 💻 Requisitos

- Sistema operacional: **Windows 10 ou 11** (64 bits)
- **Python 3.8 ou superior** instalado no sistema
- Bibliotecas Python:

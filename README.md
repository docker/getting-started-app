# APP TodoList no Docker

Bem-vindo ao repositório do Projeto TodoList! Este projeto é uma aplicação de lista de tarefas desenvolvida utilizando Docker,Javascript e Node.js.Aqui você encontrará informações e recursos relacionados a criação,excução e manutenção essa aplicação utilizando essas tecnologias.

# Criando uma aplicação Dockerizada

- Foi utilizado uma imagem **node:alpine** para otimizar o tamanho da imagem , reduzindo o tamanho do upload e os requisitos de armazenamento , para realizar o donwload da imagem , acesse: https:/ hub.docker.com/_/node
- Criação de um Dockerfile com as configurações do ambiente para facilitar o controle de versão e implantação em diferentes ambientes.

# Criando o build da imagem

No terminal de sua preferência dê este comando:

```
docker build nomedasuaiagem  .
```

# Criando tags na imagem

- Para criar tags na imagem é necessário realizar o seguinte comando :

```
docker image tag nomedasuaimagem  
```

# Instalando depedências para executar a aplicação

- Foi utilizado o npm(Node Package Manager)para gerenciar e instalar as depedências do projeto.
- Durante o processo de constução da imagem docker, realizamos a instalação das depedências especificadas no arquivo **package.json** para garantir que a aplicação seja executada sem problemas.


# Rodando a aplicação

Após criar a aplicação no terminal , abra o navegador de sua preferência e digite: 

```
localhost:3000 
```








## Documentação

Este repositório simples foi baseado na documentação:  (https://docs.docker.com/get-started/02_our_app/)

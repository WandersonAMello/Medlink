# Dockerfile

# Passo 1: Usar uma imagem base oficial do Python.
# A tag '-slim' é uma versão mais leve, ideal para produção.
FROM python:3.10-slim

# Passo 2: Definir o diretório de trabalho dentro do contêiner.
WORKDIR /app

# Passo 3: Copiar o arquivo de dependências primeiro.
# Isso aproveita o cache do Docker. Se o requirements.txt não mudar,
# o passo de instalação não será executado novamente, acelerando o build.
COPY app/requirements.txt requirements.txt

# Passo 4: Instalar as dependências.
# '--no-cache-dir' reduz o tamanho da imagem.
RUN pip install --no-cache-dir -r requirements.txt

# Passo 5: Copiar o restante do código da aplicação para o diretório de trabalho.
COPY ./app/ .

# Passo 6: Expor a porta que a aplicação Flask irá rodar.
EXPOSE 5000

# Passo 7: Comando para iniciar a aplicação quando o contêiner for executado.
# '--host=0.0.0.0' torna a aplicação acessível de fora do contêiner.
CMD ["flask", "run", "--host=0.0.0.0"]
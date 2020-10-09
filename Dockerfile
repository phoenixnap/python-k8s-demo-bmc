FROM python:3.7.4-alpine3.10

RUN apk --no-cache add curl openssh
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/$(curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt)/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
RUN mv ./kubectl /usr/local/bin
WORKDIR /app
ADD . /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python","k8s-demo.py"]

FROM python:3.7-alpine

LABEL description="Damn Vulnerable GraphQL Application 1.4.0"
LABEL github="https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application"
LABEL maintainers="Dolev Farhi & Connor McKinnon"

ARG VERSION_SUFFIX=_1.4.0
ARG TARGET_FOLDER=/opt/dvga$VERSION_SUFFIX
WORKDIR $TARGET_FOLDER/

RUN apk add --update curl

COPY requirements.txt /opt/dvga$VERSION_SUFFIX/
RUN pip install -r requirements.txt

ADD dvga /opt/dvga$VERSION_SUFFIX/dvga
ADD static /opt/dvga$VERSION_SUFFIX/static
ADD templates /opt/dvga$VERSION_SUFFIX/templates
ADD pastes /opt/dvga$VERSION_SUFFIX/pastes

COPY app.py /opt/dvga$VERSION_SUFFIX/
COPY config.py /opt/dvga$VERSION_SUFFIX/
COPY setup.py /opt/dvga$VERSION_SUFFIX/
COPY stuffing.py /opt/dvga$VERSION_SUFFIX/

RUN python setup.py

EXPOSE 5000/tcp
CMD ["python3", "app.py"]

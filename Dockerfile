FROM python:3.10

LABEL description="Damn Vulnerable GraphQL Application"
LABEL github="https://github.com/dolevf/Damn-Vulnerable-GraphQL-Application"
LABEL maintainers="Dolev Farhi & Nick Aleks"

ARG TARGET_FOLDER=/opt/dvga
WORKDIR $TARGET_FOLDER/

RUN apt install curl git

RUN useradd dvga -m 
RUN chown dvga. $TARGET_FOLDER/
USER dvga

RUN python -m venv venv
RUN . venv/bin/activate
RUN pip3 install --user --upgrade pip --no-warn-script-location --disable-pip-version-check

ADD --chown=dvga:dvga core /opt/dvga/core
ADD --chown=dvga:dvga db /opt/dvga/db
ADD --chown=dvga:dvga static /opt/dvga/static
ADD --chown=dvga:dvga templates /opt/dvga/templates

COPY --chown=dvga:dvga app.py /opt/dvga
COPY --chown=dvga:dvga config.py /opt/dvga
COPY --chown=dvga:dvga setup.py /opt/dvga/
COPY --chown=dvga:dvga version.py /opt/dvga/
COPY --chown=dvga:dvga requirements.txt /opt/dvga/

RUN pip3 install -r requirements.txt --user --no-warn-script-location
RUN python setup.py

EXPOSE 5013/tcp
CMD ["python", "app.py"]

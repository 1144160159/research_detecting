FROM python:3.12

#Install all the dependencies
RUN pip3 install --upgrade pip
#install the original flower with all the dependencies, then changed with the edited version
RUN pip3  install flwr == 1.8.0    
RUN pip3  install  torch -vvv
RUN pip3  install pandas
RUN pip3 install scikit-learn

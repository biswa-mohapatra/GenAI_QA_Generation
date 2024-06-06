echo [$(date)] : "START"
echo [$(date)] : "CREATING CONDA ENVIROMENT WITH PYTHON=3.11"
export _VERSION_ = 3.11
conda create --prefix ./env python=3.11 -y
echo [$(date)] : "ACTIVATE ENVIROMENT"
source activate ./env
echo [$(date)] : "INSTALLING DEV REQUIREMENTS"
pip install -r requirements.txt
echo [$(date)] : "END"
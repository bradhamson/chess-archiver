SCRIPT_HOME=../

createEnv(){
    echo "creating virtualenv..."
    cd $SCRIPT_HOME
    python -m venv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
}

createEnv
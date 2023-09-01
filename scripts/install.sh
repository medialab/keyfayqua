# # Install PyPi requirements
# pip install -r scripts/requirements.txt

# # Install Hopsparser from source
# mkdir resources
# cd resources
# git clone https://github.com/kat-kel/hopsparser.git
# cd hopsparser
# pip install -e .
# pip install "hopsparser[spacy]"

# Download Hopsparser French model
# MODEL_LOCATION="https://zenodo.org/record/7703346/files/UD_French-FTB-flaubert.tar.xz?download=1"
# mkdir models
# cd models
# curl -o archive.tar.xz $MODEL_LOCATION
# tar -xf archive.tar.xz
# rm archive.tar.xz
# cd ..

# # Install SpaCy French for Hopsparser
# python -m spacy download fr_core_news_sm

# Install genshi
cd resources
git clone https://github.com/edgewall/genshi.git
cd genshi
python setup.py install
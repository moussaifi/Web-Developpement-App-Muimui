conda env create -f environment.yml -n muimui
conda activate muimui
git clone https://github.com/rarcega/instagram-scraper.git
cd instagram-scraper
git reset --hard '268e0d4def1e03ef2757fe6b7b64033c7364ae52'
python setup.py install
cd ..
rm -rf instagram-scraper

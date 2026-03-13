RUN FAST API

python -m venv venv
venv\Scripts\activate           
pip install -r requirements.txt
uvicorn app.main:app --reload


git init
git add .
git commit -m "Text"
git branch -M main
git push -u origin main
git switch -c Fitur-Laporan-Angsuran-Profil
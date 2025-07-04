from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/train/<int:train_number>', methods=['GET'])
def get_train_info(train_number):
    url = f'https://mersultrenurilor.infofer.ro/ro-RO/Trains/Tren/{train_number}'
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        res = requests.get(url, headers=headers)
        res.raise_for_status()
    except Exception as e:
        return jsonify({'error': 'Nu am putut accesa pagina trenului.'}), 500

    soup = BeautifulSoup(res.text, 'html.parser')
    tabel = soup.find('table')
    if not tabel:
        return jsonify({'error': 'Nu am găsit informațiile trenului.'}), 404

    randuri = tabel.find_all('tr')[1:]
    ultima_statie = None
    urmatoarea_statie = None
    gasit_curent = False

    for i, rand in enumerate(randuri):
        coloane = rand.find_all('td')
        if len(coloane) < 5:
            continue

        statie = coloane[0].text.strip()
        sosire = coloane[1].text.strip()
        plecare = coloane[2].text.strip()
        intarziere = coloane[3].text.strip()
        stare = coloane[4].text.strip()

        if 'trenul se află' in stare.lower():
            gasit_curent = True
            ultima_statie = statie
            if i + 1 < len(randuri):
                urm = randuri[i + 1].find_all('td')
                urmatoarea_statie = urm[0].text.strip()
                ora_estim = urm[1].text.strip()
                delay = urm[3].text.strip()
            else:
                urmatoarea_statie = "-"
                ora_estim = "-"
                delay = "-"
            break

    if not gasit_curent:
        return jsonify({'error': 'Trenul nu este în mișcare sau nu apare live.'}), 404

    return jsonify({
        'tren': f'IR {train_number}',
        'statie_curenta': ultima_statie,
        'urmatoarea_statie': urmatoarea_statie,
        'ora_estimata': ora_estim,
        'intarziere': delay
    })

if __name__ == '__main__':
    app.run(debug=True)

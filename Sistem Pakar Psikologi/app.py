from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime
import json
import os

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Ganti dengan secret key yang aman

class SistemPakarDepresi:
    def __init__(self):
        self.pertanyaan = [
            "Apakah Anda merasa sedih atau murung hampir setiap hari?",
            "Apakah Anda kehilangan minat pada aktivitas yang biasanya Anda nikmati?",
            "Apakah Anda mengalami perubahan berat badan yang signifikan (naik/turun > 5kg)?",
            "Apakah Anda mengalami gangguan tidur (insomnia atau tidur berlebihan)?",
            "Apakah Anda merasa lelah atau kehilangan energi hampir setiap hari?",
            "Apakah Anda merasa tidak berharga atau bersalah berlebihan?",
            "Apakah Anda sulit berkonsentrasi atau membuat keputusan?",
            "Apakah Anda pernah berpikir tentang kematian atau bunuh diri?",
            "Apakah Anda merasa gelisah atau justru bergerak sangat lambat?",
            "Apakah Anda mengalami gejala fisik tanpa penyebab medis yang jelas?",
            "Apakah Anda menarik diri dari keluarga dan teman-teman?",
            "Apakah Anda mengalami penurunan produktivitas di kerja/sekolah?",
            "Apakah Anda merasa putus asa tentang masa depan?",
            "Apakah Anda mengalami perubahan nafsu makan yang drastis?",
            "Apakah gejala-gejala ini berlangsung lebih dari 2 minggu?"
        ]
        
        self.bobot_pertanyaan = [
            3,  # Perasaan sedih/murung
            3,  # Kehilangan minat
            2,  # Perubahan berat badan
            2,  # Gangguan tidur
            2,  # Kelelahan
            3,  # Perasaan tidak berharga
            2,  # Sulit konsentrasi
            4,  # Pikiran bunuh diri (bobot tertinggi)
            2,  # Agitasi/retardasi
            1,  # Gejala fisik
            2,  # Isolasi sosial
            2,  # Penurunan produktivitas
            3,  # Perasaan putus asa
            1,  # Perubahan nafsu makan
            2   # Durasi gejala
        ]
    
    def hitung_persentase(self, jawaban):
        skor_total = sum(self.bobot_pertanyaan[i] for i, jawab in enumerate(jawaban) if jawab)
        skor_maksimal = sum(self.bobot_pertanyaan)
        persentase = (skor_total / skor_maksimal) * 100
        return persentase, skor_total, skor_maksimal
    
    def tentukan_tingkat_depresi(self, persentase):
        if persentase >= 70:
            return "BERAT", "Sangat Tinggi"
        elif persentase >= 50:
            return "SEDANG-BERAT", "Tinggi"
        elif persentase >= 30:
            return "RINGAN-SEDANG", "Menengah"
        elif persentase >= 15:
            return "RINGAN", "Rendah"
        else:
            return "MINIMAL", "Sangat Rendah"
    
    def berikan_rekomendasi(self, tingkat):
        rekomendasi = {
            "MINIMAL": [
                "✓ Pertahankan pola hidup sehat",
                "✓ Lakukan aktivitas yang menyenangkan",
                "✓ Jaga hubungan sosial yang positif",
                "✓ Olahraga teratur dan tidur cukup"
            ],
            "RINGAN": [
                "• Tingkatkan aktivitas fisik dan sosial",
                "• Praktikkan teknik relaksasi atau meditasi",
                "• Pertimbangkan konseling atau terapi ringan",
                "• Monitor perkembangan gejala"
            ],
            "RINGAN-SEDANG": [
                "⚠ Disarankan berkonsultasi dengan psikolog",
                "⚠ Pertimbangkan terapi kognitif-perilaku",
                "⚠ Jaga pola makan dan tidur teratur",
                "⚠ Hindari alkohol dan substansi lain"
            ],
            "SEDANG-BERAT": [
                "🚨 SANGAT DISARANKAN konsultasi dengan psikiater",
                "🚨 Pertimbangkan terapi profesional",
                "🚨 Informasikan kondisi kepada keluarga terdekat",
                "🚨 Monitor ketat gejala yang memburuk"
            ],
            "BERAT": [
                "🆘 SEGERA hubungi profesional kesehatan mental",
                "🆘 Jangan biarkan diri sendiri sendirian",
                "🆘 Hubungi hotline crisis jika diperlukan",
                "🆘 Pertimbangkan rawat inap jika diperlukan"
            ]
        }
        return rekomendasi.get(tingkat, [])
    
    def analisis_gejala(self, jawaban):
        gejala_positif = []
        for i, jawab in enumerate(jawaban):
            if jawab:
                gejala_positif.append((self.pertanyaan[i], self.bobot_pertanyaan[i]))
        
        # Urutkan berdasarkan bobot tertinggi
        gejala_positif.sort(key=lambda x: x[1], reverse=True)
        return gejala_positif[:5]  # Return 5 teratas
    
    def simpan_hasil(self, hasil_data):
        try:
            waktu = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Simpan ke file JSON untuk kemudahan parsing
            hasil_file = "hasil_skrining_depresi.json"
            
            data_baru = {
                "waktu": waktu,
                "persentase": hasil_data["persentase"],
                "tingkat": hasil_data["tingkat"],
                "risiko": hasil_data["risiko"],
                "skor": hasil_data["skor"],
                "skor_maksimal": hasil_data["skor_maksimal"],
                "jawaban": hasil_data["jawaban"],
                "gejala_dominan": hasil_data["gejala_dominan"]
            }
            
            # Baca data existing atau buat list baru
            if os.path.exists(hasil_file):
                with open(hasil_file, 'r', encoding='utf-8') as f:
                    data_existing = json.load(f)
            else:
                data_existing = []
            
            data_existing.append(data_baru)
            
            # Simpan kembali
            with open(hasil_file, 'w', encoding='utf-8') as f:
                json.dump(data_existing, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"Error saving: {e}")
            return False

# Inisialisasi sistem
sistem = SistemPakarDepresi()

@app.route('/')
def index():
    # Reset session
    session.clear()
    return render_template('index.html')

@app.route('/start_test')
def start_test():
    session['current_question'] = 0
    session['answers'] = []
    return redirect(url_for('question'))

@app.route('/question')
def question():
    current_q = session.get('current_question', 0)
    
    # Jika sudah selesai semua pertanyaan
    if current_q >= len(sistem.pertanyaan):
        return redirect(url_for('result'))
    
    return render_template('question.html', 
                         question=sistem.pertanyaan[current_q],
                         question_num=current_q + 1,
                         total_questions=len(sistem.pertanyaan))

@app.route('/answer', methods=['POST'])
def answer():
    current_q = session.get('current_question', 0)
    jawaban = request.form.get('answer') == 'ya'
    
    # Simpan jawaban
    answers = session.get('answers', [])
    answers.append(jawaban)
    session['answers'] = answers
    
    # Pindah ke pertanyaan berikutnya
    session['current_question'] = current_q + 1
    
    return redirect(url_for('question'))

@app.route('/result')
def result():
    answers = session.get('answers', [])
    
    if len(answers) != len(sistem.pertanyaan):
        return redirect(url_for('index'))
    
    # Hitung hasil
    persentase, skor_total, skor_maksimal = sistem.hitung_persentase(answers)
    tingkat, risiko = sistem.tentukan_tingkat_depresi(persentase)
    rekomendasi = sistem.berikan_rekomendasi(tingkat)
    gejala_dominan = sistem.analisis_gejala(answers)
    
    # Cek apakah ada pikiran bunuh diri
    pikiran_bunuh_diri = answers[7]  # Pertanyaan ke-8
    
    hasil = {
        'persentase': round(persentase, 1),
        'skor_total': skor_total,
        'skor_maksimal': skor_maksimal,
        'tingkat': tingkat,
        'risiko': risiko,
        'rekomendasi': rekomendasi,
        'gejala_dominan': gejala_dominan,
        'pikiran_bunuh_diri': pikiran_bunuh_diri,
        'answers': answers
    }
    
    # Simpan hasil di session untuk keperluan penyimpanan
    session['hasil'] = hasil
    
    return render_template('result.html', hasil=hasil)

@app.route('/save_result', methods=['POST'])
def save_result():
    hasil = session.get('hasil')
    if not hasil:
        return jsonify({'success': False, 'message': 'Tidak ada hasil untuk disimpan'})
    
    # Persiapkan data untuk disimpan
    hasil_data = {
        'persentase': hasil['persentase'],
        'tingkat': hasil['tingkat'],
        'risiko': hasil['risiko'],
        'skor': hasil['skor_total'],
        'skor_maksimal': hasil['skor_maksimal'],
        'jawaban': hasil['answers'],
        'gejala_dominan': [{'pertanyaan': g[0], 'bobot': g[1]} for g in hasil['gejala_dominan']]
    }
    
    success = sistem.simpan_hasil(hasil_data)
    
    if success:
        return jsonify({'success': True, 'message': 'Hasil berhasil disimpan'})
    else:
        return jsonify({'success': False, 'message': 'Gagal menyimpan hasil'})

@app.route('/history')
def history():
    try:
        hasil_file = "hasil_skrining_depresi.json"
        if os.path.exists(hasil_file):
            with open(hasil_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            # Urutkan berdasarkan waktu terbaru
            data.sort(key=lambda x: x['waktu'], reverse=True)
            return render_template('history.html', history_data=data)
        else:
            return render_template('history.html', history_data=[])
    except Exception as e:
        return render_template('history.html', history_data=[], error=str(e))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
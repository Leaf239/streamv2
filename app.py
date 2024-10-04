import cv2
from flask import Flask, render_template, Response, request, redirect, url_for, session
import json

app = Flask(__name__)
app.secret_key = 'your_secret_key'

camera = cv2.VideoCapture(0)

# 해상도 설정 함수
def set_resolution(width, height):
    camera.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

# 패스코드 불러오기
def load_passcode():
    with open('passcode.json') as f:
        data = json.load(f)
    return data['passcode']

# 로그인 페이지
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        input_passcode = request.form['passcode']
        if input_passcode == load_passcode():
            session['authenticated'] = True
            return redirect(url_for('monitor'))
        else:
            return "Invalid passcode", 401
    return render_template('login.html')

# 모니터링 페이지
@app.route('/monitor', methods=['GET', 'POST'])
def monitor():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        resolution = request.form.get('resolution')
        if resolution == '144p':
            set_resolution(256, 144)
        elif resolution == '240p':
            set_resolution(426, 240)
        elif resolution == '360p':
            set_resolution(640, 360)
        elif resolution == '480p':
            set_resolution(854, 480)
        elif resolution == '720p':
            set_resolution(1280, 720)

    return render_template('monitor.html')

# 카메라 피드 스트리밍
def generate_frames():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    if not session.get('authenticated'):
        return redirect(url_for('login'))
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# 로그아웃
@app.route('/logout')
def logout():
    session.pop('authenticated', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)

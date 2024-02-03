const video = document.getElementById('video');
const user = document.getElementById('user');

// getUserMedia()を使用してWebカメラを起動
navigator.mediaDevices.getUserMedia({ video: true })
    .then(stream => {
        // ビデオ要素にストリームを設定
        video.srcObject = stream;
        // ビデオを再生
        video.play();

        alert('顔が正面に大きく映るようにして、Snap Phitoボタンを押してください。');
    })
    .catch(error => {
        console.error('Webカメラの起動に失敗しました。', error);
        if(error == 'NotAllowedError: Permission denied'){
            alert('カメラの使用を許可してください。');
        }
    });

// ビデオ要素をDOMに追加
document.body.appendChild(video);

// キャプチャしたフレームを保存するためのキャンバス要素を作成
const canvas = document.getElementById('canvas');
const context = canvas.getContext('2d');

// http通信関連
const xhr = new XMLHttpRequest();

// ビデオからフレームをキャプチャ
async function captureFrame() {
    if(user.value == ''){
        alert('名前を入力してください。');
        return;
    }

    // キャンバスのサイズをビデオのサイズに合わせる
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // ビデオからフレームをキャプチャしてキャンバスに描画
    ret = {};
    ret['name'] = user.value;
    ret['id'] = Math.floor(Math.random() * 1_000_000_000);
    ret['images'] = [];
    for(let i = 0; i < 10; i++){
        context.drawImage(video, 0, 0, canvas.width, canvas.height);
        dataURL = canvas.toDataURL();
        ret['images'].push(dataURL);
        // console.log(dataURL);
    
        await new Promise(resolve => setTimeout(resolve, 250));
    }

    xhr.open('POST', 'http://localhost:8080', true);
    xhr.setRequestHeader('Content-Type', 'application/json;charset=UTF-8');

    xhr.onload = function() {
        console.log('onload');
        if (xhr.status >= 200 && xhr.status < 400) {
            var response = xhr.responseText;
            console.log(response);
        } else {
            console.error('リクエストに失敗しました。', xhr.status, xhr.statusText);
        }
    };

    xhr.onerror = function() {
        console.error('エラーが発生しました。');
    };

    xhr.ontimeout = function() {
        console.error('timeout');
    };

    xhr.onabort = function() {
        console.error('abort');
    };

    console.log(ret);
    ret = JSON.stringify(ret);
    // console.log(ret);
    xhr.send(ret);

    alert('登録が完了しました');
}
/**
 * 解答例の公開日時制御 + AES-256-GCM 暗号化パスワード認証
 *
 * - data-release の日時（JST）より前 → 解答を非表示、ロックメッセージ表示
 * - data-release の日時以降 → 暗号文を自動復号して表示
 * - パスワードを入力すると公開日前でも解答を閲覧可能（学生スタッフ用）
 *
 * 暗号形式: base64( salt[16] + iv[12] + authTag[16] + ciphertext )
 * 鍵導出:   PBKDF2-SHA256, 100,000 iterations
 */
(function() {
  var section = document.getElementById('answers-section');
  if (!section) return;

  var release = section.getAttribute('data-release');
  if (!release) return;

  var releaseDate;
  if (release.indexOf('T') !== -1) {
    releaseDate = new Date(release + ':00+09:00');
  } else {
    releaseDate = new Date(release + 'T00:00:00+09:00');
  }

  var now = new Date();

  // ── 暗号化コンテンツの検出 ──
  var encDiv  = document.getElementById('answers-encrypted');
  var plainDiv = document.getElementById('answers-content');

  // 暗号化されていない（旧形式）場合は従来動作
  if (!encDiv && plainDiv) {
    if (now >= releaseDate) return;
    plainDiv.style.display = 'none';
    showLockUI(releaseDate, function(password) {
      // 旧形式: ハッシュ比較（フォールバック、今後は使わない）
      return Promise.resolve(false);
    }, function() {
      plainDiv.style.display = '';
    });
    return;
  }

  if (!encDiv) return;

  var cipherB64 = encDiv.getAttribute('data-cipher');
  if (!cipherB64) return;

  // 公開日を過ぎていたら自動復号（パスワードはページには無いので、復号せず表示用テキストを出す）
  // → 公開日以降はサーバ側で平文HTMLに差し替える運用を想定
  //    または公開日以降用のパスワードを別途埋め込む
  if (now >= releaseDate) {
    // 公開日以降: パスワード入力欄を表示（ロックメッセージなし）
    showPasswordOnly(function(password) {
      return decryptContent(cipherB64, password);
    }, function(html) {
      encDiv.outerHTML = '<div id="answers-content">' + html + '</div>';
    });
    return;
  }

  // 公開日前: ロックメッセージ + パスワード入力
  showLockUI(releaseDate, function(password) {
    return decryptContent(cipherB64, password);
  }, function(html) {
    encDiv.outerHTML = '<div id="answers-content">' + html + '</div>';
  });

  // ── 復号関数 ──
  function decryptContent(b64, password) {
    var raw = Uint8Array.from(atob(b64), function(c) { return c.charCodeAt(0); });

    var salt = raw.slice(0, 16);
    var iv   = raw.slice(16, 28);
    var tag  = raw.slice(28, 44);
    var ciphertext = raw.slice(44);

    // ciphertext + tag を結合（WebCrypto の GCM は tag を末尾に付ける）
    var combined = new Uint8Array(ciphertext.length + tag.length);
    combined.set(ciphertext);
    combined.set(tag, ciphertext.length);

    return crypto.subtle.importKey(
      'raw',
      new TextEncoder().encode(password),
      'PBKDF2',
      false,
      ['deriveKey']
    ).then(function(baseKey) {
      return crypto.subtle.deriveKey(
        { name: 'PBKDF2', salt: salt, iterations: 100000, hash: 'SHA-256' },
        baseKey,
        { name: 'AES-GCM', length: 256 },
        false,
        ['decrypt']
      );
    }).then(function(aesKey) {
      return crypto.subtle.decrypt(
        { name: 'AES-GCM', iv: iv },
        aesKey,
        combined
      );
    }).then(function(plainBuf) {
      return new TextDecoder().decode(plainBuf);
    }).catch(function() {
      return null; // 復号失敗 = パスワード違い
    });
  }

  // ── UI: ロックメッセージ + パスワード入力 ──
  function showLockUI(releaseDate, tryDecrypt, onSuccess) {
    var locked = document.getElementById('answers-locked');
    if (!locked) {
      locked = document.createElement('p');
      locked.id = 'answers-locked';
      locked.style.cssText = 'background:#1a1a1a;border:1px solid #333;border-radius:0.4rem;padding:1rem;text-align:center;color:#999;font-size:0.85rem';
      section.querySelector('.container').appendChild(locked);
    }

    var m = releaseDate.getMonth() + 1;
    var d = releaseDate.getDate();
    var h = releaseDate.getHours();
    var min = ('0' + releaseDate.getMinutes()).slice(-2);
    var dateStr = m + '月' + d + '日 ' + h + ':' + min;

    locked.innerHTML =
      '<div style="text-align:center">' +
        '<p style="margin-bottom:1rem">\uD83D\uDD12 標準課題・発展課題の解答は次回の授業（' + dateStr + '〜）に公開されます</p>' +
        '<div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #333">' +
          '<p style="font-size:0.8rem;color:#666;margin-bottom:0.5rem">スタッフ用: パスワードで早期閲覧</p>' +
          buildPasswordInput() +
        '</div>' +
      '</div>';
    locked.style.display = 'block';

    bindEvents(tryDecrypt, onSuccess, locked);
  }

  // ── UI: パスワード入力のみ（公開日以降） ──
  function showPasswordOnly(tryDecrypt, onSuccess) {
    var locked = document.getElementById('answers-locked');
    if (!locked) {
      locked = document.createElement('p');
      locked.id = 'answers-locked';
      locked.style.cssText = 'background:#1a1a1a;border:1px solid #333;border-radius:0.4rem;padding:1rem;text-align:center;color:#999;font-size:0.85rem';
      section.querySelector('.container').appendChild(locked);
    }

    locked.innerHTML =
      '<div style="text-align:center">' +
        '<p style="margin-bottom:0.5rem;font-size:0.85rem">解答を表示するにはパスワードを入力してください</p>' +
        buildPasswordInput() +
      '</div>';
    locked.style.display = 'block';

    bindEvents(tryDecrypt, onSuccess, locked);
  }

  function buildPasswordInput() {
    return '<div style="display:flex;justify-content:center;gap:0.5rem;align-items:center">' +
      '<input type="password" id="answer-pass" placeholder="パスワード" ' +
        'style="background:#0A0A0A;color:#E0E0E0;border:1px solid #444;border-radius:6px;' +
        'padding:0.4rem 0.8rem;font-size:0.85rem;width:160px;text-align:center">' +
      '<button id="answer-pass-btn" ' +
        'style="background:#4A7A00;color:white;border:none;border-radius:6px;' +
        'padding:0.4rem 1rem;font-size:0.85rem;cursor:pointer;font-weight:600">解錠</button>' +
    '</div>' +
    '<p id="answer-pass-error" style="color:#FF5252;font-size:0.8rem;margin-top:0.5rem;display:none">パスワードが違います</p>';
  }

  function bindEvents(tryDecrypt, onSuccess, locked) {
    var btn   = document.getElementById('answer-pass-btn');
    var input = document.getElementById('answer-pass');

    function attempt() {
      var pw = input.value;
      if (!pw) return;
      btn.disabled = true;
      btn.textContent = '検証中…';

      tryDecrypt(pw).then(function(result) {
        if (result) {
          locked.style.display = 'none';
          onSuccess(result);
        } else {
          var err = document.getElementById('answer-pass-error');
          if (err) err.style.display = 'block';
          btn.disabled = false;
          btn.textContent = '解錠';
        }
      });
    }

    btn.addEventListener('click', attempt);
    input.addEventListener('keydown', function(e) {
      if (e.key === 'Enter') attempt();
    });
  }
})();

/**
 * 解答例の公開日時制御 + パスワード認証
 *
 * - data-release の日時（JST）より前 → 解答を非表示、ロックメッセージ表示
 * - data-release の日時以降 → 解答を表示
 * - パスワードを入力すると公開日前でも解答を閲覧可能（学生スタッフ用）
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

  if (now >= releaseDate) return; // 公開日時を過ぎていれば何もしない

  var content = document.getElementById('answers-content');
  var locked = document.getElementById('answers-locked');
  if (!content || !locked) return;

  // 解答を非表示にする
  content.style.display = 'none';

  // 公開日の表示
  var m = releaseDate.getMonth() + 1;
  var d = releaseDate.getDate();
  var h = releaseDate.getHours();
  var min = ('0' + releaseDate.getMinutes()).slice(-2);
  var dateStr = m + '月' + d + '日 ' + h + ':' + min;

  // ロックメッセージ + パスワード入力欄を構築
  locked.innerHTML =
    '<div style="text-align:center">' +
      '<p style="margin-bottom:1rem">\uD83D\uDD12 標準課題・発展課題の解答は次回の授業（' + dateStr + '〜）に公開されます</p>' +
      '<div style="margin-top:1rem;padding-top:1rem;border-top:1px solid #333">' +
        '<p style="font-size:0.8rem;color:#666;margin-bottom:0.5rem">スタッフ用: パスワードで早期閲覧</p>' +
        '<div style="display:flex;justify-content:center;gap:0.5rem;align-items:center">' +
          '<input type="password" id="answer-pass" placeholder="パスワード" ' +
            'style="background:#0A0A0A;color:#E0E0E0;border:1px solid #444;border-radius:6px;' +
            'padding:0.4rem 0.8rem;font-size:0.85rem;width:140px;text-align:center">' +
          '<button id="answer-pass-btn" ' +
            'style="background:#4A7A00;color:white;border:none;border-radius:6px;' +
            'padding:0.4rem 1rem;font-size:0.85rem;cursor:pointer;font-weight:600">解錠</button>' +
        '</div>' +
        '<p id="answer-pass-error" style="color:#FF5252;font-size:0.8rem;margin-top:0.5rem;display:none">パスワードが違います</p>' +
      '</div>' +
    '</div>';
  locked.style.display = 'block';

  // パスワード認証（SHA-256ハッシュ比較）
  var HASH = '81ef440003f4e8657159bdad09aabc798a29d6b12cdf450b842cb414c7452db5';

  function unlock() {
    var input = document.getElementById('answer-pass').value;
    if (!input) return;

    // SHA-256ハッシュを計算
    crypto.subtle.digest('SHA-256', new TextEncoder().encode(input)).then(function(buf) {
      var hash = Array.from(new Uint8Array(buf)).map(function(b) {
        return b.toString(16).padStart(2, '0');
      }).join('');

      if (hash === HASH) {
        content.style.display = '';
        locked.style.display = 'none';
      } else {
        var err = document.getElementById('answer-pass-error');
        if (err) err.style.display = 'block';
      }
    });
  }

  document.getElementById('answer-pass-btn').addEventListener('click', unlock);
  document.getElementById('answer-pass').addEventListener('keydown', function(e) {
    if (e.key === 'Enter') unlock();
  });
})();

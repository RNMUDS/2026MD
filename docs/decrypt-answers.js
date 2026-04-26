#!/usr/bin/env node
/**
 * 解答セクション（AES-256-GCM 暗号化）を平文に戻すスクリプト
 *
 * 使い方:
 *   node decrypt-answers.js <password> <file.html> [file2.html ...]
 *   node decrypt-answers.js <password> --all     # docs/week*.html を一括処理（同一PW）
 *   node decrypt-answers.js <password> <file>... --dry-run   # 復号確認のみ（書き換えなし）
 *
 * ⚠️ パスワード運用ルール:
 *   各週ごとに異なるパスワードを使用すること。
 *   1つのパスワードが漏れても他週の解答は守られる設計。
 *   そのため通常は --all を使わず、ファイル単位で実行する:
 *     node decrypt-answers.js <pw_week01> docs/week01.html
 *     node decrypt-answers.js <pw_week02> docs/week02.html
 *     ...
 *
 * 処理:
 *   1. <div id="answers-encrypted" data-cipher="..."> を探す
 *   2. data-cipher の base64 を取り出して PBKDF2+AES-256-GCM で復号
 *   3. <div id="answers-content">...復号した HTML...</div> に置換して上書き保存
 *
 * 暗号形式（encrypt-answers.js と一致）:
 *   base64( salt[16] + iv[12] + authTag[16] + ciphertext )
 *   PBKDF2-SHA256, 100,000 iterations, AES-256
 */
'use strict';

const crypto = require('crypto');
const fs     = require('fs');
const path   = require('path');

// ── 暗号パラメータ（encrypt-answers.js と完全一致が必須） ──
const PBKDF2_ITERATIONS = 100_000;
const KEY_LEN           = 32;
const SALT_LEN          = 16;
const IV_LEN            = 12;
const TAG_LEN           = 16;

function decrypt(cipherB64, password) {
  const raw = Buffer.from(cipherB64, 'base64');
  if (raw.length < SALT_LEN + IV_LEN + TAG_LEN + 1) {
    throw new Error('cipher too short');
  }
  const salt       = raw.subarray(0, SALT_LEN);
  const iv         = raw.subarray(SALT_LEN, SALT_LEN + IV_LEN);
  const tag        = raw.subarray(SALT_LEN + IV_LEN, SALT_LEN + IV_LEN + TAG_LEN);
  const ciphertext = raw.subarray(SALT_LEN + IV_LEN + TAG_LEN);

  const key = crypto.pbkdf2Sync(password, salt, PBKDF2_ITERATIONS, KEY_LEN, 'sha256');

  const decipher = crypto.createDecipheriv('aes-256-gcm', key, iv);
  decipher.setAuthTag(tag);
  const dec = Buffer.concat([decipher.update(ciphertext), decipher.final()]);
  return dec.toString('utf8');
}

function processFile(filePath, password, dryRun) {
  let html = fs.readFileSync(filePath, 'utf8');

  // 既に平文（answers-content）が含まれているなら、何もしない
  if (html.indexOf('id="answers-content"') !== -1) {
    console.log(`  SKIP: ${filePath} (already plaintext / answers-content present)`);
    return false;
  }

  // <div id="answers-encrypted" data-cipher="..."> を探す
  // 属性順序や属性間の空白に多少寛容な正規表現
  const reEncrypted = /<div\s+id="answers-encrypted"\s+data-cipher="([^"]+)"\s*>\s*<\/div>/;
  const match = html.match(reEncrypted);
  if (!match) {
    console.log(`  SKIP: ${filePath} (answers-encrypted not found)`);
    return false;
  }

  const cipherB64 = match[1];
  let plaintext;
  try {
    plaintext = decrypt(cipherB64, password);
  } catch (err) {
    console.log(`  ERR: ${filePath} (decryption failed: ${err.message}) ── パスワード違いの可能性`);
    return false;
  }

  const oldBlock = match[0];
  const newBlock = '<div id="answers-content">\n' + plaintext + '\n</div>';

  if (dryRun) {
    console.log(`  DRY-RUN OK: ${filePath} (cipher ${cipherB64.length} chars → plaintext ${plaintext.length} chars)`);
    return true;
  }

  html = html.replace(oldBlock, newBlock);
  fs.writeFileSync(filePath, html, 'utf8');
  console.log(`  OK: ${filePath} (cipher ${cipherB64.length} chars → plaintext ${plaintext.length} chars)`);
  return true;
}

// ── メイン ──
const args = process.argv.slice(2);
if (args.length < 2) {
  console.error('Usage: node decrypt-answers.js <password> <file.html ...> [--dry-run]');
  console.error('       node decrypt-answers.js <password> --all [--dry-run]');
  process.exit(1);
}

const password = args[0];
let rest = args.slice(1);

const dryRun = rest.includes('--dry-run');
rest = rest.filter(a => a !== '--dry-run');

let files;
if (rest[0] === '--all') {
  const dir = path.dirname(path.resolve(__filename));
  files = fs.readdirSync(dir)
    .filter(f => /^week\d+\.html$/.test(f))
    .map(f => path.join(dir, f));
} else {
  files = rest.map(f => path.resolve(f));
}

console.log(`${dryRun ? '[DRY-RUN] ' : ''}Decrypting ${files.length} file(s) with PBKDF2+AES-256-GCM ...`);
let count = 0;
for (const f of files) {
  if (processFile(f, password, dryRun)) count++;
}
console.log(`Done: ${count} file(s) ${dryRun ? 'verified' : 'decrypted'}.`);
